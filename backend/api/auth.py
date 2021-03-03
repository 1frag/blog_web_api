from fastapi import Depends, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

import aiopg.sa

from api import models, utils, deps
from core.config import settings
from db.dao.user_dao import UsersManager


router = InferringRouter()


@cbv(router)
class LoginHandler:
    engine: aiopg.sa.engine.Engine = Depends(deps.get_db)

    @router.post("/login", responses={
        401: {"class": JSONResponse},
    })
    async def login(
            self,
            form: models.LoginInput,
            authorize: AuthJWT = Depends()
    ) -> models.LoginResponse:
        """Получение JWT токена для выполнения последующих операций"""

        async with self.engine.acquire() as conn:
            user = await UsersManager(conn).get_by_login(form.login)

        if (user is None) or (not utils.check_password(form.password, user["password"])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = authorize.create_access_token(
            subject=user["login"], expires_time=settings.expiration_token_time
        )
        return models.LoginResponse(token=access_token)


@cbv(router)
class RegistrationHandler:
    engine: aiopg.sa.engine.Engine = Depends(deps.get_db)

    @router.post("/registration", responses={
        400: {"class": JSONResponse},
    })
    async def registration(
            self, form: models.RegistrationInput
    ) -> models.RegistrationResponse:
        """Регистрация нового пользователя"""

        async with self.engine.acquire() as conn:
            resp = await UsersManager(conn).add_user(form.login, form.password)

        if not resp[0]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resp[1],
            )
        return models.RegistrationResponse()


@cbv(router)
class AuthCheck:
    @router.get("/check")
    async def check(
            self,
            authorize: AuthJWT = Depends(),
            token: str = Depends(deps.auth)
    ) -> models.CheckResponse:
        """Ручка проверки авторизации"""
        authorize.jwt_required()
        current_user = authorize.get_jwt_subject()
        return models.CheckResponse(login=current_user)
