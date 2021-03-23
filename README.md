# Тестовое задание в KODE

## Общее описание задачи
Реализовать API сервис для "блога" сообщений. С возможностью чтения,
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

## Запуск
```bash
docker-compose up -d --build
```

## HTTPS
Чтобы работать по `https`, вначале необходимо запустить `init-letsencrypt.sh`

[Подробнее](https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71)
