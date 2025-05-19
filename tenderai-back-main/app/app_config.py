from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_USER: str = "user"
    MYSQL_PASSWORD: str = "user"
    MYSQL_SERVER: str = "193.233.133.139"
    MYSQL_PORT: str = "3307"
    MYSQL_DB: str = "tenderai"
    DATABASE_URL: str = "mysql+pymysql://user:user@193.233.133.139:3307/tenderai"
    EXTERNAL_API_URL: str = "https://tender-api.foowe.ru"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()