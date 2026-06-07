"""
Точка входа. Запуск:  python bot.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import config
from handlers.commands import router as commands_router
from models.database import init_db, load_codes_if_empty


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    await init_db()
    loaded = await load_codes_if_empty()
    if loaded:
        logging.info("Загружено кодов доступа в базу: %d", loaded)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp.include_router(commands_router)

    logging.info("Бот запущен. Ожидаю сообщения...")
    # drop_pending_updates — игнорируем сообщения, накопившиеся пока бот лежал.
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
