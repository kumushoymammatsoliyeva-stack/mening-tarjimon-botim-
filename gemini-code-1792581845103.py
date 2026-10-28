import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Telegram'dagi @BotFather bergan tokeningizni shu tirnoq ichiga yozasiz
BOT_TOKEN =import os


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start bosilganda ishlaydi
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Men tarjimon botman. Menga xabar yuboring!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
