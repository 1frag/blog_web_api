from fastapi import Depends, status, HTTPException, Query, Response
from fastapi_jwt_auth import AuthJWT
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from api import models, utils, deps
from core.config import settings
from db.models.blog import AttachmentKind
from db.dao.message_dao import MessageManager


router = InferringRouter()


@cbv(router)
class Messages:
    minio_client: deps.AsyncMinio = Depends(deps.get_minio)

    @router.get("/messages")
    async def retrieve_messages(
            self,
            limit: int = Query(settings.page_size, gt=0),
            offset: int = Query(0, ge=0),
    ) -> models.MessagesResponse:
        """Получить список сообщений"""
        objects = [row async for row in MessageManager().select_all(
            limit=limit, offset=offset
        )]
        meta = utils.build_meta(
            limit=limit, offset=offset,
            total=await MessageManager().count()
        )

        return models.MessagesResponse(meta=meta, objects=objects)

    @router.get("/messages/{message_id}")
    async def detail_message(self, message_id: int) -> models.DetailMessage:
        """Получить детальную информацию о сообщении"""
        obj = await MessageManager().detail(message_id)

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        answer = models.DetailMessage(
            id=obj["id"],
            title=obj["title"],
            created_at=obj["created_at"],
            author=obj["author"],
            text=None,
            media_links=[],
            previews=[],
            like_count=obj["like_count"]
        )

        links = []
        for at in obj["attachments"]:
            if at["kind"] == AttachmentKind.text:
                answer.text = at["data"]
            elif at["kind"] == AttachmentKind.link:
                links.append(at["data"])
            elif at["kind"] == AttachmentKind.media:
                answer.media_links.append(
                    await self.minio_client.link_to_download_media(at["data"])
                )

        answer.previews = list(await utils.PreviewFetcher()(links))
        return answer

    @router.post("/messages", responses={
        400: {"class": Response},
    })
    async def create_message(
            self,
            message: models.CreateMessageInput,
            authorize: AuthJWT = Depends(),
            token: str = Depends(deps.auth)
    ) -> models.CreateMessageResponse:
        """Отправить новое сообщение"""
        if (not message.text) and (len(message.links) == 0) and \
                (len(message.media_items) == 0):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Сообщение должно содержать текст, ссылки "
                                       "или вложения")

        authorize.jwt_required()
        current_user = authorize.get_jwt_subject()

        obj = await MessageManager().create_message(message, current_user)

        return models.CreateMessageResponse(**obj)

    @router.post("/messages/like", responses={404: {"class": Response}})
    async def like(
            self,
            message_id: int,
            authorize: AuthJWT = Depends(),
            token: str = Depends(deps.auth)
    ) -> models.LikeResponse:
        """Поставить / убрать лайк"""
        authorize.jwt_required()
        current_user = authorize.get_jwt_subject()

        obj = await MessageManager().like_message(message_id, current_user)

        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return models.LikeResponse(**obj, status=200)

    @router.delete("/messages", response_class=Response, responses={
        204: {"class": Response},
        403: {"class": Response},
        404: {"class": Response},
    })
    async def delete_message(
            self,
            message_id: int,
            authorize: AuthJWT = Depends(),
            token: str = Depends(deps.auth)
    ):
        """Удалить своё сообщение"""
        authorize.jwt_required()
        current_user = authorize.get_jwt_subject()

        rc = await MessageManager().delete_message(message_id, current_user)

        return Response(status_code=rc)
