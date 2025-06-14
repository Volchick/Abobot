from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from sqlalchemy import select, desc
from app.models import User, Message, Dialog
from app.database import async_session_maker
from app.config_reader import GPT_TOKEN, GPT_CONTEXT
from datetime import datetime
from openai import AsyncOpenAI, AuthenticationError, RateLimitError


router = Router()
client = AsyncOpenAI(api_key=GPT_TOKEN)
user_histories = {}

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
        "/gpt_start - Включить режим общения с ChatGPT\n"
        "/gpt_stop - Выключить режим общения с ChatGPT\n"
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

@router.message(Command("gpt_start"))
async def cmd_chatgpt(message: types.Message):
    userid = message.from_user.id
    user_histories[userid] = [
        {"role": "system", "content": GPT_CONTEXT}
    ]
    await message.answer("Режим общения с ChatGPT активирован. Для выхода напишите /gpt_stop.")

@router.message(Command("gpt_stop"))
async def cmd_chatgpt_stop(message: types.Message):
    userid = message.from_user.id
    if userid in user_histories:
        user_histories.pop(userid)
        await message.answer("Режим общения с ChatGPT выключен.")
    else:
        await message.answer("Режим общения с ChatGPT не был активирован.")

@router.message()
async def chatgpt_and_save(message: types.Message):
    userid = message.from_user.id
    text = message.text
    known_commands = {"/start", "/reply", "/aboba", "/gael", "/help", "/re_chat", "/gpt_start", "/gpt_stop"}
    if text and text.startswith("/") and text.split()[0] not in known_commands:
        await message.answer("Неизвестная команда. Напишите /help для списка доступных команд.")
        return
    if not text or text.startswith('/'):
        return

    # Сохраняем сообщение пользователя в базу
    async with async_session_maker() as session:
        # Получаем или создаём пользователя
        result = await session.execute(select(User).where(User.telegram_id == userid))
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=userid)
            session.add(user)
            await session.flush()

        # Получаем или создаём диалог
        result = await session.execute(select(Dialog).where(Dialog.user_id == userid))
        dialog = result.scalar_one_or_none()
        if not dialog:
            dialog = Dialog(user_id=userid)
            session.add(dialog)
            await session.flush()

        # Сохраняем сообщение пользователя
        msg = Message(dialog_id=dialog.id, text=text, created_at=datetime.now())
        session.add(msg)
        await session.commit()

    # Если режим ChatGPT не активен — просто сохраняем сообщение
    if userid not in user_histories:
        return

    # Проверка на выход из режима
    if text.lower() in ("выход", "exit", "/stop"):
        user_histories.pop(userid, None)
        await message.answer("Режим чата завершён.")
        return

    # Добавляем сообщение в историю и отправляем в ChatGPT
    user_histories[userid].append({"role": "user", "content": text})
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=user_histories[userid],
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
        await message.answer(answer)
        user_histories[userid].append({"role": "assistant", "content": answer})
    except AuthenticationError:
        await message.answer("Ошибка: неверный API-ключ OpenAI.")
        user_histories.pop(userid, None)
    except RateLimitError:
        await message.answer("Ошибка: превышен лимит запросов к OpenAI API.")
        user_histories.pop(userid, None)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        user_histories.pop(userid, None)