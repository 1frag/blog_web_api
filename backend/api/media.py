import uuid

from fastapi import Depends, status, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

import asynctempfile
import minio

from api import models, utils, deps
from core.config import settings

router = InferringRouter()


@cbv(router)
class MediaController:
    minio_client: deps.AsyncMinio = Depends(deps.get_minio)

    @router.post("/upload", responses={400: {"models": ...}},)
    async def upload(
            self,
            authorize: AuthJWT = Depends(),
            file: UploadFile = File(...),
            token: str = Depends(deps.auth)
    ) -> models.UploadMediaResponse:
        if not authorize.get_jwt_subject():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        async with asynctempfile.NamedTemporaryFile() as fp:
            content = await file.read()
            await fp.write(content)

            if utils.get_valid_type(content) is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="only video or images supported")

            name = uuid.uuid4().hex
            await fp.seek(0)
            await self.minio_client.async_upload_to_minio(
                settings.minio_bucket_name,
                f"media/common/{name}",
                fp.name
            )
            return models.UploadMediaResponse(status=201, name=name)

    @router.get(
        "/download",
        response_class=FileResponse,
        responses={404: {"models": ...}},
    )
    async def download(self, name: str):
        file_ctx = asynctempfile.NamedTemporaryFile()
        afp = await file_ctx.__aenter__()

        try:
            await self.minio_client.async_fget_object(
                settings.minio_bucket_name,
                f"media/common/{name}",
                afp.name,
            )
        except minio.error.S3Error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        await afp.seek(0)
        kind = utils.get_valid_type(afp.name)

        await afp.seek(0)
        return FileResponse(
            afp.name, media_type=kind.MIME,
            filename=f"{name}.{kind.EXTENSION}",
            background=file_ctx.__aexit__
        )
