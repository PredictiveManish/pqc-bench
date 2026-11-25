"""Content-addressed disk cache for model completions.

Re-running the same suite against the same model costs nothing: identical
(provider, model, prompt, system, temperature, max_tokens) tuples are served
from disk. Use --no-cache to force fresh calls.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from harness.types import Completion


class DiskCache:
    def __init__(self, root: str = ".cache"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(provider: str, prompt: str, system: str, temperature: float,
            max_tokens: int, salt: str = "") -> str:
        h = hashlib.sha256()
        for part in (provider, prompt, system, repr(temperature), str(max_tokens), salt):
            h.update(part.encode("utf-8"))
            h.update(b"\x00")
        return h.hexdigest()

    def get(self, key: str) -> Completion | None:
        p = self.root / f"{key}.json"
        if not p.exists():
            return None
        try:
            return Completion.from_dict(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            return None

    def put(self, key: str, completion: Completion) -> None:
        p = self.root / f"{key}.json"
        p.write_text(json.dumps(completion.as_dict()), encoding="utf-8")
