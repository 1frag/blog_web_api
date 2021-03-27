from typing import Optional
from tortoise.exceptions import IntegrityError

from api import utils
from db.models.blog import User


class UsersManager:
    async def add_user(
            self, login: str, password: str,
    ) -> tuple[bool, Optional[str]]:
        try:
            await User(login=login, password=utils.get_password(password).decode()).save()
        except IntegrityError as e:
            if 'unique constraint "user_login_key"' in e.args[0].args[0]:
                return False, "Login already exists"
            raise e

        return True, None

    async def get_by_login(self, login: str) -> Optional[User]:
        return await User.get_or_none(login=login)
