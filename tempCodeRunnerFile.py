import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database import init_db

from handlers.start import router as start_router
from handlers.add_product import router as add_router
from handlers.sell import router as sell_router
from handlers.search import router as search_router
from handlers.report import router as report_router

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(add_router)
dp.include_router(sell_router)
dp.include_router(search_router)
dp.include_router(report_router)


async def main():
    init_db()
    print("🚀 Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())