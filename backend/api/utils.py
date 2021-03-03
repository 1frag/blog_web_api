import asyncio
import logging

import bcrypt
import filetype
import httpx

from filetype.types import IMAGE, VIDEO
from linkpreview import link_preview


def get_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def check_password(decrypted_password: str, encrypted_password: str) -> bool:
    return bcrypt.checkpw(decrypted_password.encode(), encrypted_password.encode())


def build_meta(limit, offset, total):
    def build_url(new_offset):
        return f"?limit={limit}&offset={new_offset}"

    return {
        "next": None if offset + limit >= total else build_url(offset + limit),
        "prev": None if offset == 0 else build_url(max(0, offset - limit)),
    }


def get_valid_type(filename: str):
    valid_types = list(IMAGE + VIDEO)
    return filetype.match(filename, valid_types)


class PreviewFetcher:
    def __init__(self):
        self.client = None

    async def _get_preview(self, url: str):
        try:
            resp = await self.client.get(url)
            content = (await resp.aread()).decode()
            preview = link_preview(url, content)
            return {
                "title": preview.title,
                "image": preview.image,
                "url": url,
            }
        except Exception as e:
            logging.warning(repr(e))
            return {"url": url}

    async def __call__(self, links):
        async with httpx.AsyncClient() as self.client:
            return await asyncio.gather(*map(self._get_preview, links))
