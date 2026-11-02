
import asyncio
import os
from io import BytesIO

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from google import genai
from google.genai import types as gemini_types

# ==================================
# API VA BOT SOZLAMALARI
# ==================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN kiritilmagan!")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY kiritilmagan!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"


# ==================================
# START BUYRUG'I
# ==================================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Salom! Men AI tarjimon botman 🤖\n\n"
        "Istalgan tildagi matn yozilgan rasmni yuboring.\n"
        "Men matnni o'qib, o'zbek tiliga tarjima qilib beraman! 🌍"
    )


# ==================================
# RASMDAGI MATNNI TARJIMA QILISH
# ==================================

@dp.message(F.photo)
async def handle_photo(message: types.Message):

    waiting_msg = await message.answer(
        "⏳ Rasm qabul qilindi!\n"
        "Iltimos, biroz kuting..."
    )

    try:
        photo = message.photo[-1]

        # Telegram'dan rasmni yuklab olish
        file_info = await bot.get_file(photo.file_id)

        image_buffer = BytesIO()

        await bot.download_file(
            file_info.file_path,
            destination=image_buffer
        )

        image_bytes = image_buffer.getvalue()

        # Gemini uchun topshiriq
        prompt = """
        Ushbu rasmdagi matnlarni aniqlang.

        1. Barcha matnlarni asl tilida yozing.
        2. Matnlarni o'zbek tiliga to'liq tarjima qiling.
        3. Asl matnning ma'nosini saqlang.
        4. O'qib bo'lmaydigan joylarni taxmin qilmang.
        5. Matnning birorta qismini tashlab ketmang.

        JAVOB:

        📄 TOPILGAN ASL MATN:

        🌐 O'ZBEKCHA TARJIMA:
        """

        # Gemini AI orqali tahlil
        image_part = gemini_types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )

        response = await client.aio.models.generate_content(
            model=MODEL,
            contents=[prompt, image_part]
        )

        result = response.text

        if not result:
            raise ValueError("AI javob qaytarmadi.")

        # Kutish xabarini o'chirish
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=waiting_msg.message_id
        )

        # Natijani yuborish
        for i in range(0, len(result), 4000):
            await message.answer(result[i:i + 4000])

    except Exception as e:
        error = f"❌ Xatolik: {str(e)}"

        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=waiting_msg.message_id,
                text=error[:4000]
            )
        except Exception:
            await message.answer(error[:4000])


# ==================================
# BOTNI ISHGA TUSHIRISH
# ==================================

async def main():
    print("AI TARJIMON BOT ISHGA TUSHDI!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await client.aio.aclose()


if __name__ == "__main__":
    asyncio.run(main())
