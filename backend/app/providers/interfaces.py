from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PromptResult:
    prompt: str
    negative_prompt: str
    seed: int | None


@dataclass
class GeneratedImageResult:
    image_path: str
    provider: str
    seed: int | None


class ProviderError(RuntimeError):
    """Raised when an external provider call fails."""


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def build_initial_prompt(self, payload: dict) -> PromptResult:
        raise NotImplementedError

    @abstractmethod
    def refine_prompt(
        self,
        *,
        payload: dict,
        parent_prompt: str,
        parent_negative_prompt: str,
        instruction: str,
    ) -> PromptResult:
        raise NotImplementedError


class ImageGenerationProvider(ABC):
    name: str

    @abstractmethod
    def generate_image(self, *, prompt: str, negative_prompt: str, seed: int | None) -> GeneratedImageResult:
        raise NotImplementedError
