TORTOISE_ORM = {
    "connections": {"default": "postgres://user:difficult_pwd@db:5432/db_name"},
    "apps": {
        "blog": {
            "models": ["db.models.blog", "aerich.models"],
            "default_connection": "default",
        },
    },
}
