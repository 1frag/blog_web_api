from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from tortoise.contrib.fastapi import register_tortoise

from api import auth, blog, media
from db.conf import TORTOISE_ORM

app = FastAPI(debug=True)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(blog.router, prefix="/blog", tags=["blog"])
app.include_router(media.router, prefix="/media", tags=["media"])


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


register_tortoise(app, config=TORTOISE_ORM)
