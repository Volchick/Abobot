from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from sqlalchemy import select
from app.models import User, Message, Dialog
from app.database import async_session_maker
from datetime import datetime


router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Абоба!")

@router.message(Command("reply"))
async def cmd_reply(message: types.Message):
    await message.reply("Чего тебе надобно?")

@router.message(Command("aboba"))
async def cmd_aboba(message: types.Message):
    photo = FSInputFile("app/pictures/aboba.png")
    await message.answer_photo(photo, caption="Абоба :)")

@router.message(Command("gael"))
async def cmd_gael(message: types.Message):
    photo = FSInputFile("app/pictures/gnomegael.jpg")
    await message.answer_photo(photo, caption="Отдай свою тёмную душу!")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Приветствие\n"
        "/reply - Ответить на сообщение\n"
        "/aboba - Отправить картинку с лягушкой\n"
        "/gael - Отправить картинку с гномом\n"
        "/re_chat - Показать последние 10 сообщений в диалоге\n"
        "/help - Показать это сообщение"
    )
    await message.answer(help_text)

@router.message(Command("re_chat"))
async def cmd_re_chat(message: types.Message):
    userid = message.from_user.id
    async with async_session_maker() as session:
        # Получаем пользователя
        result = await session.execute(select(User).where(User.telegram_id == userid))
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Нет сохранённых сообщений.")
            return

        # Получаем диалог
        result = await session.execute(select(Dialog).where(Dialog.user_id == userid))
        dialog = result.scalar_one_or_none()
        if not dialog:
            await message.answer("Нет сохранённых сообщений.")
            return

        # Получаем последние 10 сообщений в обратном порядке
        result = await session.execute(
            select(Message)
            .where(Message.dialog_id == dialog.id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        messages = result.scalars().all()
        if not messages:
            await message.answer("Нет сохранённых сообщений.")
            return

        # Формируем текст
        text = "\n\n".join(
            f"{msg.created_at.strftime('%d.%m.%Y %H:%M:%S')}: {msg.text}" for msg in messages
        )
        await message.answer(f"Последние сообщения:\n\n{text}")

@router.message()
async def save_message(message: types.Message):
    userid = message.from_user.id
    text = message.text
    if not text or text.startswith('/'):
        return  # Не сохраняем команды и пустые сообщения

    async with async_session_maker() as session:
        # Ищем или создаём пользователя
        result = await session.execute(select(User).where(User.telegram_id == userid))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=userid)
            session.add(user)
            await session.flush()

        # Ищем или создаём диалог
        result = await session.execute(select(Dialog).where(Dialog.user_id == userid))
        dialog = result.scalar_one_or_none()
        if not dialog:
            dialog = Dialog(user_id=userid)
            session.add(dialog)
            await session.flush()

        # Сохраняем сообщение
        msg = Message(dialog_id=dialog.id, text=text, created_at=datetime.now())
        session.add(msg)
        await session.commit()



@router.message()
async def unknown_command(message: types.Message):
    if message.text and message.text.startswith('/'):
        await message.reply("Неизвестная команда. Используйте /help, чтобы увидеть список команд.")
