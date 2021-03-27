import enum

from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    login = fields.CharField(max_length=63, unique=True)
    password = fields.CharField(max_length=127)


class Message(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now=True)
    author = fields.ForeignKeyField(
        "blog.User", related_name="messages", on_delete=fields.CASCADE,
    )


class AttachmentKind(enum.IntEnum):
    text = 1
    media = 2
    link = 3


class Attachment(Model):
    id = fields.IntField(pk=True)
    kind: AttachmentKind = fields.IntEnumField(AttachmentKind)
    data = fields.TextField()
    message = fields.ForeignKeyField(
        "blog.Message", related_name="attachments", on_delete=fields.CASCADE, null=True,
    )


class Like(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "blog.User", related_name="likes", on_delete=fields.CASCADE,
    )
    message = fields.ForeignKeyField(
        "blog.Message", related_name="likes", on_delete=fields.CASCADE,
    )
