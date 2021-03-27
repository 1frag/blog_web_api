-- upgrade --
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "login" VARCHAR(63) NOT NULL UNIQUE,
    "password" VARCHAR(127) NOT NULL
);
CREATE TABLE IF NOT EXISTS "message" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "author_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "attachment" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "kind" SMALLINT NOT NULL,
    "data" TEXT NOT NULL,
    "message_id" INT REFERENCES "message" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "attachment"."kind" IS 'text: 1\nmedia: 2\nlink: 3';
CREATE TABLE IF NOT EXISTS "like" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "message_id" INT NOT NULL REFERENCES "message" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
