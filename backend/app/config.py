from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/scenario_analytics"
    csv_path: str = "data/scenarios.csv"
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()
