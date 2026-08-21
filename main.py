import asyncio
from aiogram import Bot, Dispatcher
from config import API_BOT
from handlers.start import _router
from database.db import init_db
async def _run_tg_bot():
    _tg_bot = Bot(API_BOT)
    _dp = Dispatcher()
    _dp.include_router(_router)
    await init_db()
    print("бот запущен и ждет соо")
    try:
        await _dp.start_polling(_tg_bot)
    except Exception as error:
        print(f"произошла ошибка у бота: {error}, перезапуск через 5 сек")
    finally:
        await _tg_bot.session.close()
        print("сессия бота окончена")
if __name__=="__main__":
    try:
        asyncio.run(_run_tg_bot())
    except KeyboardInterrupt:
        print("бот остановлен пользователем")

