# Changelog

Указание `zero_offset` в `createdAt` сообщения

Переименовал `./backend/api/chat.py` -> `./backend/api/blog.py`

Переместил все опции для `minio` в `settings.minio`

Использование `minio_data` в `docker-compose`

Удалён метод __/media/download__. Теперь в деталях сообщения приходит ссылка на скачивание из minio.
