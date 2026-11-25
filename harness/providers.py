"""Real model providers (no SDK dependency, stdlib HTTP only).

Supported providers:
  openai      - OpenAI chat/completions  (OPENAI_API_KEY, optional OPENAI_BASE_URL)
  anthropic   - Anthropic messages       (ANTHROPIC_API_KEY)
  gemini      - Google generateContent   (GEMINI_API_KEY / GOOGLE_API_KEY)
  compatible  - any OpenAI-compatible endpoint: vLLM, Ollama, Together, Groq,
                OpenRouter, LM Studio ... (base_url required, key optional)

Every provider exposes:
    provider.name                         -> "provider:model"
    provider.complete(prompt, ...)        -> Completion

Transient failures (429, 5xx, network) are retried with exponential backoff
and jitter; permanent 4xx errors raise ProviderError immediately.
"""

from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.request

from harness.types import Completion


class ProviderError(RuntimeError):
    pass


_RETRYABLE = {429, 500, 502, 503, 504}


def _post_json(url: str, headers: dict, payload: dict, timeout: int = 180,
               max_retries: int = 4) -> dict:
    data = json.dumps(payload).encode("utf-8")
    last = None
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:600]
            last = f"HTTP {e.code}: {body}"
            if e.code in _RETRYABLE and attempt < max_retries:
                time.sleep(min(30, 2 ** attempt) + random.random())
                continue
            raise ProviderError(last) from e
        except urllib.error.URLError as e:
            last = f"network error: {e}"
            if attempt < max_retries:
                time.sleep(min(30, 2 ** attempt) + random.random())
                continue
            raise ProviderError(last) from e
    raise ProviderError(last or "unknown error")


class BaseProvider:
    name = "base"

    def complete(self, prompt: str, *, system: str = "", temperature: float = 0.0,
                 max_tokens: int = 4096) -> Completion:
        raise NotImplementedError


class OpenAIProvider(BaseProvider):
    def __init__(self, model: str, api_key: str | None = None,
                 base_url: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL",
                                                    "https://api.openai.com/v1")).rstrip("/")
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is not set")
        self.name = f"openai:{model}"

    def complete(self, prompt, *, system="", temperature=0.0, max_tokens=4096):
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        payload = {"model": self.model, "temperature": temperature,
                   "max_tokens": max_tokens, "messages": msgs}
        d = _post_json(self.base_url + "/chat/completions",
                       {"Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"}, payload)
        u = d.get("usage", {}) or {}
        text = d["choices"][0]["message"]["content"]
        return Completion(text=text, model=d.get("model", self.model),
                          prompt_tokens=u.get("prompt_tokens", 0),
                          completion_tokens=u.get("completion_tokens", 0),
                          finish_reason=str(d["choices"][0].get("finish_reason") or ""),
                          raw=d)


class OpenAICompatibleProvider(OpenAIProvider):
    """OpenAI-compatible servers (vLLM, Ollama, Together, Groq, LM Studio)."""

    def __init__(self, model: str, base_url: str, api_key: str | None = None):
        if not base_url:
            raise ProviderError("--base-url is required for the 'compatible' provider")
        # Local servers often need no key; pass a placeholder so the header is valid.
        super().__init__(model, api_key=api_key or os.environ.get("COMPATIBLE_API_KEY", "not-needed"),
                         base_url=base_url)
        self.name = f"compatible:{model}"


class AnthropicProvider(BaseProvider):
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ProviderError("ANTHROPIC_API_KEY is not set")
        self.name = f"anthropic:{model}"

    def complete(self, prompt, *, system="", temperature=0.0, max_tokens=4096):
        payload = {"model": self.model, "max_tokens": max_tokens,
                   "temperature": temperature,
                   "messages": [{"role": "user", "content": prompt}]}
        if system:
            payload["system"] = system
        d = _post_json("https://api.anthropic.com/v1/messages",
                       {"Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"}, payload)
        text = "".join(b.get("text", "") for b in d.get("content", [])
                       if b.get("type") == "text")
        u = d.get("usage", {}) or {}
        return Completion(text=text, model=d.get("model", self.model),
                          prompt_tokens=u.get("input_tokens", 0),
                          completion_tokens=u.get("output_tokens", 0), raw=d)


class GeminiProvider(BaseProvider):
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = (api_key or os.environ.get("GEMINI_API_KEY")
                        or os.environ.get("GOOGLE_API_KEY") or "")
        if not self.api_key:
            raise ProviderError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set")
        self.name = f"gemini:{model}"

    def complete(self, prompt, *, system="", temperature=0.0, max_tokens=4096):
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self.model}:generateContent?key={self.api_key}")
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                   "generationConfig": {"temperature": temperature,
                                        "maxOutputTokens": max_tokens}}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        d = _post_json(url, {"Content-Type": "application/json"}, payload)
        cands = d.get("candidates", [])
        text = ""
        if cands:
            text = "".join(p.get("text", "") for p in
                           cands[0].get("content", {}).get("parts", []))
        u = d.get("usageMetadata", {}) or {}
        return Completion(text=text, model=self.model,
                          prompt_tokens=u.get("promptTokenCount", 0),
                          completion_tokens=u.get("candidatesTokenCount", 0), raw=d)


class SarvamProvider(BaseProvider):
    """Sarvam AI chat completions.

    OpenAI-compatible request/response shape. Authenticates with the
    `api-subscription-key` header (Bearer also accepted by Sarvam).

    Base URL defaults to /v1, which serves `sarvam-105b` and
    `sarvam-105b-conversations`. For the open-weight models on /v2
    (glm5.3, glm5.3-flash, gemma4, deepseekv4.1-flash-1017, ...) pass
    --base-url https://api.sarvam.ai/v2.

    Env: SARVAM_API_KEY, optional SARVAM_BASE_URL.
    Gotcha: Sarvam returns HTTP 403 (not 401) for an invalid/missing key.
    """

    def __init__(self, model: str = "sarvam-105b", api_key: str | None = None,
                 base_url: str | None = None):
        self.model = model
        self.api_key = api_key or os.environ.get("SARVAM_API_KEY", "")
        if not self.api_key:
            raise ProviderError("SARVAM_API_KEY is not set")
        self.base_url = (base_url or os.environ.get(
            "SARVAM_BASE_URL", "https://api.sarvam.ai/v1")).rstrip("/")
        self.name = f"sarvam:{model}"

    def complete(self, prompt, *, system="", temperature=0.0, max_tokens=4096):
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        payload = {"model": self.model, "messages": msgs,
                   "temperature": temperature, "max_tokens": max_tokens}
        try:
            d = _post_json(self.base_url + "/chat/completions",
                           {"Content-Type": "application/json",
                            "api-subscription-key": self.api_key}, payload)
        except ProviderError as e:
            if "HTTP 403" in str(e):
                raise ProviderError(
                    "Sarvam auth failed (HTTP 403). Check SARVAM_API_KEY "
                    "(Sarvam returns 403, not 401, for a bad/missing key). "
                    f"Detail: {e}") from e
            raise
        choice = (d.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        text = msg.get("content") or ""
        u = d.get("usage") or {}
        return Completion(
            text=text,
            model=d.get("model", self.model),
            prompt_tokens=u.get("prompt_tokens", u.get("input_tokens", 0)),
            completion_tokens=u.get("completion_tokens", u.get("output_tokens", 0)),
            finish_reason=str(choice.get("finish_reason") or ""),
            raw=d,
        )


_PROVIDERS = {
    "sarvam": SarvamProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
}


def make_provider(spec: str, model: str, *, base_url: str | None = None,
                  api_key: str | None = None) -> BaseProvider:
    if spec == "compatible":
        return OpenAICompatibleProvider(model, base_url=base_url or "", api_key=api_key)
    if spec == "sarvam":
        return SarvamProvider(model, api_key=api_key, base_url=base_url)
    if spec not in _PROVIDERS:
        raise ProviderError(f"unknown provider '{spec}'. "
                            f"Choose from {list(_PROVIDERS) + ['compatible']}")
    return _PROVIDERS[spec](model, api_key=api_key)
