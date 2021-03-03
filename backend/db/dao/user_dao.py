import aiopg.sa
import psycopg2.errors

from typing import Optional

from api import utils
from db.models.blog import users, User, engine


class UsersManager:
    def __init__(self, conn: aiopg.sa.SAConnection):
        self.conn = conn

    async def add_user(
            self, login: str, password: str,
    ) -> tuple[bool, Optional[str]]:

        query = users.insert().values(
            login=login, password=utils.get_password(password).decode(),
        ).compile(bind=engine)

        try:
            await self.conn.execute(str(query), query.params)

        except psycopg2.Error as e:
            if type(e).__name__ == "UniqueViolation":
                return False, "Login already exists"
            raise e

        return True, None

    async def get_by_login(self, login):
        query = users.select().where(User.login == login).compile()
        return await (
            await self.conn.execute(str(query), query.params)
        ).fetchone()
