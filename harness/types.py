"""Shared value types."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class Completion:
    text: str
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: str = ""
    raw: dict | None = field(default=None, repr=False)

    def as_dict(self) -> dict:
        return {
            "text": self.text,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "finish_reason": self.finish_reason,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Completion":
        return cls(
            text=d.get("text", ""),
            model=d.get("model", ""),
            prompt_tokens=d.get("prompt_tokens", 0),
            completion_tokens=d.get("completion_tokens", 0),
            finish_reason=d.get("finish_reason", ""),
        )
