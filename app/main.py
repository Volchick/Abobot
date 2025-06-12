import asyncio
from aiogram import Bot, Dispatcher
from app.config_reader import BOT_TOKEN
from app.commands import router
from app.database import async_session_maker
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
