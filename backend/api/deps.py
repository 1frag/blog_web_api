import datetime

import aiomisc
import aiopg.sa
import minio

from fastapi.security import HTTPBearer

from core import settings


async def get_db():
    async with aiopg.sa.create_engine(settings.database_url) as engine:
        yield engine


auth = HTTPBearer()


class AsyncMinio(minio.Minio):
    @aiomisc.threaded
    def async_upload_to_minio(self, *args, **kwargs):
        return self.fput_object(*args, **kwargs)

    @aiomisc.threaded
    def async_fget_object(self, *args, **kwargs):
        return self.fget_object(*args, **kwargs)

    @aiomisc.threaded
    def link_to_download_media(self, name):
        return self.presigned_get_object(
            settings.minio.bucket_name,
            f"media/common/{name}",
        )


async def get_minio():
    yield AsyncMinio(
        settings.minio.endpoint,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=False
    )
