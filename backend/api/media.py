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

            kind = utils.get_valid_type(content)
            if kind is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="only video or images supported")

            name = ".".join([uuid.uuid4().hex, kind.EXTENSION])
            await fp.seek(0)
            await self.minio_client.async_upload_to_minio(
                settings.minio_bucket_name,
                f"media/common/{name}",
                fp.name
            )
            return models.UploadMediaResponse(status=201, name=name)
