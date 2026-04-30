from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BoardBook Studio API"
    app_env: str = "development"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg2://boardbook:boardbook@localhost:5432/boardbook"
    media_dir: str = "media"
    cors_origins: str = "http://localhost:3000"
    llm_provider: str = "mock"
    image_provider: str = "mock"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_keep_alive: str = "10m"
    ollama_temperature: float = 0.2
    ollama_num_ctx: int = 4096
    ollama_timeout_seconds: float = 120.0
    ollama_seed: int | None = None
    ollama_api_key: str | None = None
    comfyui_base_url: str = "http://127.0.0.1:8188"
    comfyui_timeout_seconds: float = 120.0
    comfyui_poll_interval_seconds: float = 1.0
    comfyui_max_wait_seconds: float = 240.0
    comfyui_workflow_path: str = "workflows/comfyui_text2img_api.json"
    comfyui_positive_prompt_node_id: str = "6"
    comfyui_negative_prompt_node_id: str = "7"
    comfyui_sampler_node_id: str = "3"
    comfyui_sampler_seed_input_name: str = "seed"
    comfyui_save_image_node_id: str = "9"
    comfyui_filename_prefix: str = "BoardBookStudio"
    comfyui_checkpoint_name: str | None = None
    comfyui_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
