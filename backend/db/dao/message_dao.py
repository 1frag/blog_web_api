import aiopg.sa
import sqlalchemy as sa

from api import models
from core.config import settings
from db.dao import user_dao
from db.models.blog import (
    Message, messages, users, User, attachments, Like, likes, AttachmentKind,
)
from sqlalchemy.sql.elements import BooleanClauseList


class MessageManager(object):
    def __init__(self, conn: aiopg.sa.SAConnection):
        self.conn = conn

    async def execute(self, query):
        return await self.conn.execute(str(query), query.params)

    async def select_all(self, *, limit=settings.page_size, offset=0):
        query = (sa.select([User.id.label("author_id"), User.login.label("author_login"),
                            Message.id, Message.title, Message.created_at])
                 .select_from(messages.join(users, User.id == Message.author))
                 .limit(limit).offset(offset)
                 .compile())
        result = await self.execute(query)

        async for row in result:
            yield {
                "author": {"id": row["author_id"], "login": row["author_login"]},
                "id": row["id"], "title": row["title"], "created_at": row["created_at"]
            }

    async def count(self):
        query = sa.select([sa.func.count()]).select_from(messages)

        return (await (await self.execute(query)).fetchone())[0]

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
        res = await self.conn.execute("""
            select M.id, M.title, M.created_at, COUNT(DISTINCT L.id) as like_count,
                   json_build_object('id', U.id, 'login', U.login) AS author,
                   jsonb_agg(row_to_json(A)) as attachments
            from app_attachments A
            right outer join app_messages M on M.id = A.message_id
            inner join app_users U on U.id = M.author
            left outer join app_likes L on M.id = L.message_id
            where M.id = %s
            group by u.id, M.id;
        """, (message_id,))

        obj = await res.fetchone()
        if not obj:
            return None

        obj = dict(obj.items())
        if obj["attachments"] == [None]:  # when attachments are absent
            obj["attachments"] = []

        return dict(obj.items())

    async def _insert_message(self, title: str, author: int):
        query = (messages
                 .insert().values(title=title, author=author)
                 .returning(Message.id)).compile()
        res = await self.execute(query)
        return (await res.fetchone())["id"]

    async def _add_attachment(
            self,
            data: str,
            kind: AttachmentKind,
            message_id: int
    ):
        query = (attachments
                 .insert().values(data=data, kind=kind, message_id=message_id)
                 .compile())
        await self.execute(query)

    async def create_message(
            self,
            message: models.CreateMessageInput,
            author_login: str,
    ):
        author = await user_dao.UsersManager(self.conn).get_by_login(author_login)
        async with self.conn.begin():
            message_id = await self._insert_message(message.title, author["id"])

            for kind, data_lst in (
                    ("text", [message.text]),
                    ("link", message.links),
                    ("media", message.media_items),
            ):
                for data in data_lst:
                    await self._add_attachment(data, kind, message_id)

        return {"message_id": message_id, "status": 201}

    async def _like_found(self, message_id: int, current_user: str):
        query = likes.select().where(
            sa.and_(Like.message_id == message_id, Like.user_id == current_user)
        ).compile()
        return await (await self.execute(query)).fetchone()

    async def _like_delete(self, cond: BooleanClauseList):
        query = likes.delete().where(cond).returning(Like.id).compile()
        return await (await self.execute(query)).fetchone()

    async def _like_insert(self, message_id: int, user_id: int):
        query = likes.insert().values(message_id=message_id, user_id=user_id).compile()
        return await self.execute(query)

    async def get_message_author(self, message_id: int):
        query = (sa.select([users])
                 .select_from(messages.join(users, User.id == Message.author))
                 .where(sa.and_(Message.id == message_id))
                 .compile())
        return await (await self.execute(query)).fetchone()

    async def like_message(self, message_id: int, current_user: str):
        """Delete row or insert"""
        author = await self.get_message_author(message_id)
        if author is None:
            return None
        issuer = await user_dao.UsersManager(self.conn).get_by_login(current_user)

        if issuer["id"] == author["id"]:
            return {"state": models.LikeState.self}
        author = await user_dao.UsersManager(self.conn).get_by_login(current_user)
        cond = sa.and_(Like.message_id == message_id, Like.user_id == author["id"])

        if not await self._like_delete(cond):
            await self._like_insert(message_id, author["id"])
            return {"state": models.LikeState.like}
        return {"state": models.LikeState.unlike}

    async def delete_message(self, message_id: int, current_user: str) -> int:
        issuer = await user_dao.UsersManager(self.conn).get_by_login(current_user)
        author = await self.get_message_author(message_id)

        if author is None:
            return 404
        if issuer["id"] != author["id"]:
            return 403

        query = messages.delete().where(Message.id == message["id"]).compile()
        await self.execute(query)
        return 204
