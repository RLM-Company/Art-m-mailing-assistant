"""
Обработчики основных команд и логики активации.

Логика активации (как в примере-скриншоте):
1. Пользователь пишет /start (или любое сообщение) → бот просит токен.
2. Пользователь присылает токен.
3. Если токен совпадает с ACTIVATION_TOKEN — активируем и показываем функционал.
4. После активации работают команды и (позже) ИИ-функции.
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

import texts
from config import config
from models import database as db

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, command: CommandObject) -> None:
    """
    /start без аргументов — приветствие/активация.
    /start рассылки WB 200 — запуск функции (если активирован).
    """
    await db.ensure_user(message.from_user.id, message.from_user.username)

    args = command.args  # всё, что после /start

    # Если есть аргументы — это попытка запустить функцию.
    if args:
        if not await db.is_activated(message.from_user.id):
            await message.answer(texts.NEED_ACTIVATION)
            return
        await _handle_function_launch(message, args)
        return

    # /start без аргументов
    if await db.is_activated(message.from_user.id):
        await message.answer(texts.ALREADY_ACTIVATED)
        await message.answer(texts.ABOUT)
    else:
        await message.answer(texts.GREETING)


async def _handle_function_launch(message: Message, args: str) -> None:
    """
    Разбирает строку запуска функции.
    Сейчас поддержан только сценарий 'рассылки <платформа> <лимит>'.
    """
    parts = args.split()

    # ожидаем: рассылки WB 200
    if len(parts) >= 3 and parts[0].lower() in ("рассылки", "рассылка", "mailing"):
        platform = parts[1]
        try:
            limit = int(parts[2])
        except ValueError:
            await message.answer(texts.MAILING_BAD_FORMAT)
            return
        await message.answer(texts.mailing_accepted(platform=platform, limit=limit))
        return

    await message.answer(texts.MAILING_BAD_FORMAT)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(texts.HELP)


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not await db.is_activated(message.from_user.id):
        await message.answer(texts.NEED_ACTIVATION)
        return
    # Заглушка Этапа 1 — реальные цифры появятся с движком рассылок.
    await message.answer(texts.stats_message())


@router.message(F.text)
async def handle_text(message: Message) -> None:
    """
    Любой текст без команды.
    - Если пользователь не активирован — считаем это попыткой ввести токен.
    - Если активирован — пока заглушка (на Этапе 2 здесь будет ИИ).
    """
    await db.ensure_user(message.from_user.id, message.from_user.username)

    if not await db.is_activated(message.from_user.id):
        # Пробуем как токен активации.
        if message.text.strip() == config.activation_token:
            await db.set_activated(message.from_user.id)
            await message.answer(texts.TOKEN_OK)
            await message.answer(texts.ABOUT)
        else:
            await message.answer(texts.TOKEN_WRONG)
        return

    # Активирован, но это просто текст — ИИ ещё не подключён.
    await message.answer(texts.AI_NOT_READY)
