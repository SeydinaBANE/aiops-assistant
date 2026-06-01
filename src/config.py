from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_log_level: str = "INFO"

    # LLM (OpenRouter)
    openrouter_api_key: str = ""
    llm_model: str = "openai/gpt-4o-mini"
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.1

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_grpc_port: int = 6334
    collection_name: str = "runbooks"

    # OpenTelemetry
    otel_service_name: str = "aiops-assistant"
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_traces_sampler: str = "parentbased_traceidratio"
    otel_traces_sampler_arg: float = 0.1


settings = Settings()
