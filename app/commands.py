from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Абоба!")

@router.message(Command("reply"))
async def cmd_reply(message: types.Message):
    await message.reply("Чего тебе надобно?")

@router.message(Command("aboba"))
async def cmd_aboba(message: types.Message):
    photo = FSInputFile("pictures/aboba.png")
    await message.answer_photo(photo, caption="Абоба :)")

@router.message(Command("gael"))
async def cmd_gael(message: types.Message):
    photo = FSInputFile("pictures/gnomegael.jpg")
    await message.answer_photo(photo, caption="Отдай свою тёмную душу!")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Приветствие\n"
        "/reply - Ответить на сообщение\n"
        "/aboba - Отправить картинку с лягушкой\n"
        "/gael - Отправить картинку с гномом\n"
        "/help - Показать это сообщение"
    )
    await message.answer(help_text)

@router.message()
async def unknown_command(message: types.Message):
    if message.text and message.text.startswith('/'):
        await message.reply("Неизвестная команда. Используйте /help, чтобы увидеть список команд.")
