from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./chainnetra.db"
    SECRET_KEY: str = "changeme"
    LIVE_MODE: bool = False
    TRONGRID_API_KEY: str = ""
    TRONSCAN_API_KEY: str = ""
    ETHERSCAN_API_KEY: str = ""
    TRONGRID_BASE_URL: str = "https://api.trongrid.io"
    TRONSCAN_BASE_URL: str = "https://apilist.tronscanapi.com"
    VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
