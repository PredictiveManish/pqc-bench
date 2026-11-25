"""Process-level isolation for executing model-submitted code.

Honest scope — this is NOT a container. It provides:

  * a fresh temporary working directory (cwd isolation)
  * environment scrubbing (no KEY/TOKEN/SECRET/PASSWORD/CREDENTIAL variables)
  * rlimits (CPU seconds, address space, open files)
  * a wall-clock timeout
  * a network namespace via `unshare -n` **when the kernel permits it**

It does NOT provide filesystem namespaces, a UID change, or guaranteed network
isolation. `unshare -n` is commonly blocked in containerised environments; the
result of `network_isolated` tells you which case you are in. Do not run hostile
code from strangers with this.
"""

import contextlib
import os
import re
import shutil
import subprocess
import tempfile

_SECRET = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PASSWD", re.I)


def scrubbed_env(extra: dict | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if not _SECRET.search(k)}
    env.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if extra:
        env.update(extra)
    return env


def _limits(cpu: int):
    try:
        import resource

        def _apply():
            resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
            resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
            resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
        return _apply
    except Exception:
        return None


_NET = None


def _net_prefix() -> list:
    """Return ['unshare','-n'] only if a network namespace actually works here."""
    global _NET
    if _NET is not None:
        return _NET
    if not shutil.which("unshare"):
        _NET = []
        return _NET
    try:
        p = subprocess.run(["unshare", "-n", "true"], capture_output=True, timeout=5)
        _NET = ["unshare", "-n"] if p.returncode == 0 else []
    except Exception:
        _NET = []
    return _NET


def run(argv: list, cwd: str, timeout: int = 60,
        extra_env: dict | None = None) -> dict:
    import sys
    argv = [sys.executable if a == "python3" else a for a in argv]
    cmd = _net_prefix() + list(argv)
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, preexec_fn=_limits(timeout),
                           env=scrubbed_env(extra_env))
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "stdout": "", "stderr": "",
                "network_isolated": bool(_net_prefix())}
    return {"ok": p.returncode == 0, "returncode": p.returncode,
            "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:],
            "network_isolated": bool(_net_prefix())}


@contextlib.contextmanager
def workspace(fixture_dir: str):
    """Copy a fixture into a throwaway directory and clean it up afterwards."""
    d = tempfile.mkdtemp(prefix="pqc-repo-")
    dst = os.path.join(d, "work")
    shutil.copytree(fixture_dir, dst)
    try:
        yield dst
    finally:
        shutil.rmtree(d, ignore_errors=True)
