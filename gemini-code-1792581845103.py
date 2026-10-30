import asyncio
import os
from io import BytesIO
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import google.generativeai as genai
from PIL import Image

# Tokenlarni muhit o'zgaruvchilaridan (Environment Variables) olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Gemini AI ni sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# /start buyrug'i
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Salom! Men tarjimon botman 🤖\n"
        "Menga istalgan tildagi matn bor rasmni yuboring, "
        "men uni o'qib, o'zbek tiliga tarjima qilib beraman!"
    )

# Rasmlarni qabul qilish va tarjima qilish
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    waiting_msg = await message.answer("⏳ Rasm qabul qilindi, tahlil qilinmoqda va tarjima qilinmoqda...")
    
    try:
        # Eng sifatli rasm hajmini olish
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        
        # Rasmni yuklab olish
        file_bytes = await bot.download_file(file_info.file_path)
        
        # PIL yordamida rasmni ochish
        image = Image.open(BytesIO(file_bytes.read()))
        
        # Gemini uchun prompt (vazifa)
        prompt = (
            "Bu rasmdagi matnni aniqlang va uni o'zbek tiliga tarjima qiling. "
            "Javobni quyidagi tartibda yozing:\n"
            "📄 **Topilgan matn (asl tilda):**\n[matn]\n\n"
            "🌐 **O'zbekcha tarjimasi:**\n[tarjima]"
        )
        
        # Gemini orqali javob olish
        response = model.generate_content([prompt, image])
        
        # Kutish xabarini o'chirish va natijani yuborish
        await bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)
        await message.answer(response.text)
        
    except Exception as e:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=waiting_msg.message_id,
            text=f"❌ Xatolik yuz berdi: {str(e)}"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
