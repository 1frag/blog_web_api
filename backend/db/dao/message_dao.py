from tortoise.transactions import in_transaction
import ujson

from api import models
from core.config import settings
from db.dao import user_dao
from db.models.blog import (
    Message, User, Like, Attachment, AttachmentKind,
)


class MessageManager(object):
    async def select_all(self, *, limit=settings.page_size, offset=0):
        async for row in (Message.all()
                                 .prefetch_related("author")
                                 .limit(limit)
                                 .offset(offset)):
            yield {
                "author": {"id": row.author.id,
                           "login": row.author.login},
                "id": row.id,
                "title": row.title,
                "created_at": row.created_at,
            }

    async def count(self):
        return await Message.all().count()

    async def detail(self, message_id: int):
        """Возвращаемое значение: {
            "id": id сообщения,
            "title": title сообщения,
            "created_at": время создания сообщения,
            "like_count": количество лайков,
            "author": {"id": id автора, "login": логин автора},
            "attachments": [{
                "id": id вложения,
                "data": данные вложения,
                "kind": тип вложения, ...}, ...]
        }"""

        async with in_transaction() as conn:
            cnt, objs = await conn.execute_query("""
                select M.id, M.title, M.created_at, COUNT(DISTINCT L.id) as like_count,
                       json_build_object('id', U.id, 'login', U.login) AS author,
                       jsonb_agg(row_to_json(A)) as attachments
                from attachment A
                right outer join message M on M.id = A.message_id
                inner join "user" U on U.id = M.author_id
                left outer join "like" L on M.id = L.message_id
                where M.id = $1
                group by u.id, M.id;
            """, (message_id,))

        if cnt == 0:
            return None
        obj = dict(objs[0].items())
        obj["author"] = ujson.loads(obj["author"])
        obj["attachments"] = ujson.loads(obj["attachments"])
        return obj

    async def create_message(
            self,
            form: models.CreateMessageInput,
            author_login: str,
    ):
        author = await user_dao.UsersManager().get_by_login(author_login)
        async with in_transaction() as connection:
            message = await Message.create(title=form.title, author=author,
                                           using_db=connection)

            for kind, data_lst in (
                    (AttachmentKind.text, [form.text]),
                    (AttachmentKind.link, form.links),
                    (AttachmentKind.media, form.media_items),
            ):
                for data in data_lst:
                    await Attachment.create(kind=kind, data=data, message=message,
                                            using_db=connection)

        return {"message_id": message.id, "status": 201}

    async def like_message(self, message_id: int, current_user_login: str):
        """Delete row or insert"""
        message = await Message.get(id=message_id)
        issuer = await user_dao.UsersManager().get_by_login(current_user_login)
        if issuer == message.author:
            return {"state": models.LikeState.self}

        async with in_transaction() as connection:
            like = await Like.get_or_none(message=message, user=issuer)

            if like is None:
                await Like.create(message=message, user=issuer, using_db=connection)
                return {"state": models.LikeState.like}

            await like.delete(using_db=connection)
            return {"state": models.LikeState.unlike}

    async def delete_message(self, message_id: int, current_user: str) -> int:
        m: Message = await Message.get_or_none(id=message_id).prefetch_related("author")

        if m is None:
            return 404
        if m.author.login != current_user:
            return 403

        await m.delete()
        return 204
