# Тестовое задание в KODE

## Общее описание задачи
Реализовать API сервис для "блога" сообщений. С возможностью чтение,
создания новых, удаления (авторами) сообщений.

## Реализованные endpoints
### auth
* __/auth/login__ - получить access token от сервиса
* __/auth/registration__ - зарегистрировать нового пользователя
* __/auth/check__ - проверить авторизацию

### chat
* _GET, POST_ __/chat/messages__ - получить / создать сообщения
* __/chat/messages/like__ - поставить / убрать лайк

### media
* __/media/upload__ - загрузить media файл
* __/media/download__ - скачать media файл

## Запуск
```bash
nohup docker-compose up -d --build > /dev/null 2>&1 &
```
