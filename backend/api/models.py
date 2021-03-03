import datetime
import enum

from typing import Optional

from fastapi_utils.api_model import APIModel
from pydantic import Field


class LoginInput(APIModel):
    login: str
    password: str


class LoginResponse(APIModel):
    status: int = Field(200, example=200)
    token: Optional[str] = None


class RegistrationInput(APIModel):
    login: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)


class RegistrationResponse(APIModel):
    status: int = Field(201, example=201)
    details: str = "Success"


class Meta(APIModel):
    next: Optional[str]
    prev: Optional[str]


class AuthorMessage(APIModel):
    id: int
    login: str


class Message(APIModel):
    id: int
    title: str
    created_at: datetime.datetime
    author: AuthorMessage


class MessagesResponse(APIModel):
    meta: Meta
    objects: list[Message]


class Preview(APIModel):
    url: str
    image: Optional[str] = Field(None, description="Ссылка на картинку (preview)")
    title: Optional[str] = Field(None, description="Краткое описание ссылки")


class DetailMessage(Message):
    media_links: list[str] = Field(
        description="Список ссылок для скачивания загружаемых объектов"
    )
    previews: list[Preview]
    text: Optional[str]
    like_count: int


class UploadMediaResponse(APIModel):
    status: int
    name: str


class CheckResponse(APIModel):
    login: Optional[str]


class CreateMessageInput(APIModel):
    title: str = Field(..., description="Заголовок сообщения")
    text: Optional[str] = Field(..., description="Текст сообщения")
    links: list[str] = Field(..., description="Список ссылок")
    media_items: list[str] = Field(..., description="Список имён загруженных объектов")


class CreateMessageResponse(APIModel):
    status: int = Field(200, example=200)
    message_id: int = Field(..., example=456)


class LikeState(str, enum.Enum):
    like = "like"
    unlike = "unlike"
    self = "self"  # prevent yourself from being liked
    error = "error/unknown"


class LikeResponse(APIModel):
    state: LikeState = Field(..., description="Состояние после операции")
    status: int
