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


async def get_minio():
    yield AsyncMinio(**settings.minio_keys, secure=False)
