"""
Работа с базой данных (SQLite через aiosqlite).
На старте храним пользователей и флаг активации.
Структура заложена так, чтобы легко расширяться (сессии, статистика)
и при необходимости мигрировать на Postgres.
"""
import aiosqlite

from config import config


async def init_db() -> None:
    """Создаёт таблицы, если их ещё нет. Вызывается при старте бота."""
    async with aiosqlite.connect(config.db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                activated   INTEGER NOT NULL DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Задел под Этап 4 — учёт сессий рассылок.
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                platform    TEXT,
                limit_count INTEGER,
                sent        INTEGER NOT NULL DEFAULT 0,
                replies     INTEGER NOT NULL DEFAULT 0,
                status      TEXT NOT NULL DEFAULT 'created',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


async def ensure_user(user_id: int, username: str | None) -> None:
    """Добавляет пользователя, если его ещё нет."""
    async with aiosqlite.connect(config.db_path) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username),
        )
        await db.commit()


async def is_activated(user_id: int) -> bool:
    async with aiosqlite.connect(config.db_path) as db:
        async with db.execute(
            "SELECT activated FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return bool(row and row[0])


async def set_activated(user_id: int) -> None:
    async with aiosqlite.connect(config.db_path) as db:
        await db.execute(
            "UPDATE users SET activated = 1 WHERE user_id = ?", (user_id,)
        )
        await db.commit()
