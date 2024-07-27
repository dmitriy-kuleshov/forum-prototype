from os import environ
from fastapi import FastAPI
from sqlalchemy import desc, select

from posts import posts_table
from users import users_table
import databases

# берем параметры БД из переменных окружения
DB_USER = environ.get("DB_USER", "user")
DB_PASSWORD = environ.get("DB_PASSWORD", "password")
DB_HOST = environ.get("DB_HOST", "localhost")
DB_NAME = "async-blogs"
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)
# создаем объект database, который будет использоваться для выполнения запросов
database = databases.Database(SQLALCHEMY_DATABASE_URL)

app = FastAPI()


@app.on_event("startup")
async def startup():
    # когда приложение запускается устанавливаем соединение с БД
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    # когда приложение останавливается разрываем соединение с БД
    await database.disconnect()


@app.get("/")
async def read_root():
    query = (
        select(
            posts_table.c.id,
            posts_table.c.created_at,
            posts_table.c.title,
            posts_table.c.content,
            posts_table.c.user_id,
            users_table.c.name.label("user_name"),
        )
            .select_from(posts_table.join(users_table))
            .order_by(desc(posts_table.c.created_at))
    )
    results = await database.fetch_all(query)
    return results
