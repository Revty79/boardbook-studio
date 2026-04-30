from app.core.config import get_settings
from app.providers.comfyui import ComfyUIProvider
from app.providers.interfaces import ImageGenerationProvider, LLMProvider
from app.providers.mock_image import MockImageProvider
from app.providers.mock_llm import MockLLMProvider
from app.providers.ollama import OllamaProvider


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider.lower() == "ollama":
        return OllamaProvider()
    return MockLLMProvider()


def get_image_provider() -> ImageGenerationProvider:
    settings = get_settings()
    if settings.image_provider.lower() == "comfyui":
        return ComfyUIProvider()
    return MockImageProvider()
