import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import ChatJoinRequest, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# ТОКЕН БОТА (лучше передавать через переменные окружения Render)
TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 1. Обработка заявки на вступление в канал
@dp.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    user_id = update.from_user.id
    chat_id = update.chat.id
    
    # Текст с вашими условиями
    text = (
        "Привет! 👋 Чтобы попасть в канал, ознакомься с условиями:\n\n"
        "1. Быть вежливым.\n"
        "2. Не спамить.\n"
        "3. Не нарушать правила сообщества.\n\n"
        "Нажимая кнопку ниже, ты подтверждаешь свое согласие."
    )
    
    # Кнопка подтверждения (в callback_data передаем ID чата, чтобы одобрить именно этот канал)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я соглашаюсь", callback_data=f"accept_{chat_id}")]
    ])
    
    try:
        await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

# 2. Обработка нажатия на кнопку "Я соглашаюсь"
@dp.callback_query(F.data.startswith("accept_"))
async def approve_user(callback: CallbackQuery):
    user_id = callback.from_user.id
    # Вытаскиваем ID чата из callback_data
    chat_id = int(callback.data.split("_")[1])
    
    try:
        # Одобряем заявку пользователя в канал
        await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        
        # Редактируем сообщение, убирая кнопку
        await callback.message.edit_text("🎉 Вы успешно согласились с условиями и добавлены в канал!")
    except Exception as e:
        await callback.message.edit_text("❌ Ссылка устарела или произошла ошибка. Попробуйте подать заявку снова.")
        print(f"Ошибка одобрения: {e}")
        
    await callback.answer()

# --- ВЕБ-СЕРВЕР ДЛЯ ОБХОДА СПЯЩЕГО РЕЖИМА RENDER ---
async def handle_ping(request):
    return web.Response(text="Бот работает!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render выдает порт динамически в переменную PORT
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    # Запускаем веб-сервер и бота одновременно
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
