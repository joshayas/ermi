import sqlite3
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text.contains("Report"))
async def report(message: Message):
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("database/shop.db")
    cur = conn.cursor()

    # 1. Fetch sales using correct column names
    cur.execute("SELECT product_name, qty, total FROM sales WHERE date=?", (today,))
    sales_data = cur.fetchall()

    # 2. Fetch expenses
    cur.execute("SELECT title, amount FROM expenses WHERE date=?", (today,))
    expenses_data = cur.fetchall()

    conn.close()

    if not sales_data and not expenses_data:
        await message.answer(f"📅 <b>Report for {today}</b>\n\n📭 No business activity logged today.")
        return

    total_sales = sum([item[2] for item in sales_data])
    total_expenses = sum([item[1] for item in expenses_data])
    net_profit = total_sales - total_expenses

    text = f"📊 <b>DAILY BUSINESS REPORT</b>\n📅 Date: <code>{today}</code>\n\n"

    if sales_data:
        text += "🛒 <b>Sales Breakdown:</b>\n"
        for item in sales_data:
            text += f" • {item[0]} (x{item[1]}) → {item[2]} \n"
        text += f"<b>Total Revenue:</b> {total_sales}\n\n"
    else:
        text += "🛒 <b>Sales Breakdown:</b> No sales logged.\n\n"

    if expenses_data:
        text += "💸 <b>Expenses Logged:</b>\n"
        for item in expenses_data:
            text += f" • {item[0]} → -{item[1]}\n"
        text += f"<b>Total Expenses:</b> {total_expenses}\n\n"

    # Financial Summary Line
    emoji = "📈" if net_profit >= 0 else "📉"
    text += f"───────────────────\n{emoji} <b>Net Balance: {net_profit}</b>"

    await message.answer(text)