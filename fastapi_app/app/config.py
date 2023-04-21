import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    address_justin_sun: str = "0x3ddfa8ec3052539b6c9549f12cea2c295cff5296"
    allowed_origins: list = [
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:8310",
    ]
    allowed_urls: list = [
        "/api/ping",
        "/debug/schema/swagger-ui/",
        "/debug/schema/",
        "/docs",
        "/openapi.json",
    ]
    api_keys: list = ["api_key_1", "api_key_2", "api_key_3"]
    EXPL_COM_API_KEY: str = os.getenv("EXPL_COM_API_KEY")
    HEADERS: dict = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }


settings = Settings()
