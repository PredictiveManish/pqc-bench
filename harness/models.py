"""Reference adapters used by the integrity gate (scripts/validate.py).

These are NOT models under test. They exist only to prove the scorers are
correct: the gold oracle must score 1.0, the null model 0.0. Real model runs go
through harness.providers.
"""

from __future__ import annotations

from harness.types import Completion


class GoldModel:
    """Self-test oracle: echoes each task's stored gold answer."""

    def __init__(self, gold_by_prompt: dict[str, str], name: str = "gold-oracle"):
        self.name = name
        self._gold = dict(gold_by_prompt)

    def generate(self, prompt: str, *, system: str = "", temperature: float = 0.0,
                 max_tokens: int = 4096) -> str:
        return self._gold.get(prompt, "")

    def complete(self, prompt: str, **kw) -> Completion:
        return Completion(text=self.generate(prompt), model=self.name)


class NullModel:
    """Self-test baseline: never answers. Must score 0 everywhere."""

    name = "null-model"

    def generate(self, prompt: str, *, system: str = "", temperature: float = 0.0,
                 max_tokens: int = 4096) -> str:
        return "I don't know."

    def complete(self, prompt: str, **kw) -> Completion:
        return Completion(text=self.generate(prompt), model=self.name)
