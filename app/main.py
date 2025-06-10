import asyncio
from aiogram import Bot, Dispatcher
from config_reader import BOT_TOKEN
from commands import router


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
