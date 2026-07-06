import sqlite3
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text.contains("Stock"))
async def view_stock(message: Message):
    conn = sqlite3.connect("database/shop.db")
    cur = conn.cursor()
    cur.execute("SELECT name, category, price, stock FROM products")
    items = cur.fetchall()
    conn.close()

    if not items:
        await message.answer("📦 Shop inventory is completely empty.")
        return

    text = "📦 <b>CURRENT INVENTORY STOCK</b>\n\n"
    for item in items:
        status = "🟢" if item[3] > 5 else ("🟡" if item[3] > 0 else "🔴 Out of Stock")
        text += f"{status} <b>{item[0]}</b> ({item[1]})\n💰 Price: {item[2]} | Stock: <b>{item[3]}</b>\n\n"

    await message.answer(text)