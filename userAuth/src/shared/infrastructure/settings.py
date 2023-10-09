from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    # App Configurations
    APP_NAME: str = 'appcoppel'
    SERVICE_NAME: str
    NAMESPACE: str
    API_VERSION: str
    IMAGE_VERSION: str
    ENABLE_DOCS: bool = False
    PORT: int = 8000
    RELOAD: bool = False
    SECRET_KEY: str
    ALGORITHM: str
    # Mongo
    MONGO_URI: str
    MONGO_DB_NAME: str = 'comic_shop'
    MONGO_TIMEOUT_MS: int = 500
    MONGO_MAX_POOL_SIZE: int = 20
    MONGO_ID_ERROR_DETAILS: str = 'errorDetails'
    # Logs
    VERSION_LOG: str = 'v1'
    APPENDERS: str = 'console'
    DEVELOPER_PORTAL_HTTP_ERRORS: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()
