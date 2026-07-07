import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiohttp import web  # Imported to handle Render's port binding

from config import BOT_TOKEN
from database import init_db

# Routers
from handlers.start import router as start_router
from handlers.add_product import router as add_router
from handlers.sell import router as sell_router
from handlers.search import router as search_router
from handlers.report import router as report_router
from handlers.stock import router as stock_router      # Added
from handlers.expense import router as expense_router  # Added

# --- Render Port Binding Handler ---
async def handle_home(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_home)
    
    # Render passes the port dynamically via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"🌐 Web server listening on port {port}")
    await site.start()

# --- Main Execution ---
# --- Main Execution ---
async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Register all working routers
    dp.include_router(start_router)
    dp.include_router(add_router)
    dp.include_router(sell_router)
    dp.include_router(search_router)
    dp.include_router(report_router)
    dp.include_router(stock_router)    
    dp.include_router(expense_router)  

    init_db()
    
    print("🚀 Starting web server and Telegram bot concurrently...")
    
    # Run BOTH the web server and the bot pooling at the same time
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())