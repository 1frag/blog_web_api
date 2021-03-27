from core.config import settings
from minio import Minio


def run():
    m = Minio(
        settings.minio.endpoint,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=False
    )
    m.make_bucket(settings.minio.bucket_name)


if __name__ == '__main__':
    # PYTHONPATH=$(pwd) python minio_migrations/init.py
    run()
