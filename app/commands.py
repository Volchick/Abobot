from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from sqlalchemy import select, desc
from app.models import User, Message, Dialog
from app.database import async_session_maker
from datetime import datetime
from sqlalchemy.orm import selectinload


router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    userid = message.from_user.id
    async with async_session_maker() as session:
        # Проверяем, есть ли пользователь
        result = await session.execute(select(User).where(User.telegram_id == userid))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=userid)
            session.add(user)
            await session.flush()  # Получаем user.id

        # Проверяем, есть ли диалог
        result = await session.execute(select(Dialog).where(Dialog.user_id == userid))
        dialog = result.scalar_one_or_none()
        if not dialog:
            dialog = Dialog(user_id=userid)
            session.add(dialog)
            await session.flush()

        # Добавляем приветственное сообщение
        message_obj = Message(dialog_id=dialog.id, text="Абоба!", created_at=datetime.now())
        session.add(message_obj)
        await session.commit()

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

@router.message(Command('re_chat'))
async def re_chat(message: types.Message):
    try:
        if message.from_user:
            user_id = message.from_user.id
        else:
            raise Exception("message.from_user пуст!")
    except ValueError:
        await message.answer("ID должен быть числом.")
        return
    except Exception:
        await message.answer("Сообщение пусто.")
        return

    try:
        async with get_session() as session:
            result = await session.execute(
                text(
                    "SELECT m.text, m.created_at FROM messages m "
                    "JOIN dialogs d ON m.dialog_id = d.id "
                    "WHERE d.user_id = :uid "
                    "ORDER BY m.created_at DESC"
                ),
                {'uid': user_id}
            )
            messages = result.fetchall()
            if not messages:
                await message.answer("У этого пользователя сообщений нет.")
                return
            for text_msg, created in messages:
                dt_str = created.strftime("%d.%m.%Y %H:%M")
                await message.answer(f"🕒 {dt_str}\n📝 {text_msg}")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")


@router.message()
async def unknown_command(message: types.Message):
    if message.text and message.text.startswith('/'):
        await message.reply("Неизвестная команда. Используйте /help, чтобы увидеть список команд.")
