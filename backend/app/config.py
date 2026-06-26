from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://fbcommerce:changeme@localhost:5432/fbcommerce"
    bot_token: str = ""
    secret_key: str = "change-me"
    debug: bool = True
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"
    kbz_pay_api_key: str = ""
    wave_money_api_key: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.database_url:
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace(
                    "postgres://", "postgresql+asyncpg://", 1
                )
            elif self.database_url.startswith("postgresql://"):
                self.database_url = self.database_url.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                )


settings = Settings()
