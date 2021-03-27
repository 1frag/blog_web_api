import asyncio
from tortoise import Tortoise

from db import conf
from db.models.blog import User, Attachment, Model, Like, Message


async def init():
    await Tortoise.init(config=conf.TORTOISE_ORM)
