import sys
import pathlib
import datetime

import dotenv

from fastapi_jwt_auth import AuthJWT
from pydantic import BaseSettings, Field, BaseModel

project_path = (pathlib.Path(__file__) / "../..").resolve()
sys.path.append(str(project_path))
dotenv.load_dotenv(project_path / "../env/web.env")


class MinioSettings(BaseSettings):
    endpoint: str = Field(..., env='minio_endpoint')
    access_key: str = Field(..., env='minio_access_key')
    secret_key: str = Field(..., env='minio_secret_key')
    bucket_name: str = Field(..., env='minio_bucket_name')


class Settings(BaseSettings):
    database_url: str
    authjwt_secret_key: str
    expiration_token_time: datetime.timedelta = datetime.timedelta(days=5)
    page_size: int = 3
    minio: MinioSettings = MinioSettings()


settings = Settings()


@AuthJWT.load_config
def get_config():
    return settings
