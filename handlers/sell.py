import sqlite3
from datetime import datetime
from rapidfuzz import process
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.menu import main_menu

router = Router()

# ─── UNIVERSAL CANCEL INTERCEPTOR ─────────────────────────────────────
@router.message(F.text.contains("Cancel Action"))
async def process_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🛑 Action cancelled. Returned to main menu.", reply_markup=main_menu)

# ─── NAVIGATION KEYBOARD ──────────────────────────────────────────────
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Cancel Action")]],
    resize_keyboard=True
)

class SellProductSG(StatesGroup):
    waiting_for_name = State()
    waiting_for_qty = State()

def get_all_products():
    conn = sqlite3.connect("database/shop.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM products")
    data = [i[0] for i in cur.fetchall()]
    conn.close()
    return data

def get_product(name):
    conn = sqlite3.connect("database/shop.db")
    cur = conn.cursor()
    cur.execute("SELECT name, price, stock FROM products WHERE name=?", (name,))
    data = cur.fetchone()
    conn.close()
    return data

@router.message(F.text.contains("Sell"))
async def sell_start(message: Message, state: FSMContext):
    await state.set_state(SellProductSG.waiting_for_name)
    await message.answer("🛒 Enter the name of the product being sold:", reply_markup=cancel_kb)

@router.message(SellProductSG.waiting_for_name)
async def sell_name(message: Message, state: FSMContext):
    products = get_all_products()
    if not products:
        await message.answer("❌ No products available in the shop database.", reply_markup=main_menu)
        await state.clear()
        return

    result = process.extract(message.text, products, limit=1)
    if not result:
        await message.answer("❌ No matching product found. Try again.", reply_markup=cancel_kb)
        return

    best_match = result[0][0]
    product = get_product(best_match)
    
    if not product:
        await message.answer("❌ Product details missing.", reply_markup=main_menu)
        await state.clear()
        return

    name, price, stock = product
    if stock <= 0:
        await message.answer(f"❌ '{name}' is completely out of stock!", reply_markup=main_menu)
        await state.clear()
        return

    await state.update_data(prod_name=name, prod_price=price, current_stock=stock)
    await state.set_state(SellProductSG.waiting_for_qty)
    await message.answer(
        f"Selected: <b>{name}</b>\nPrice: {price} | Stock: {stock}\n\n🔢 Enter Quantity:", 
        reply_markup=cancel_kb
    )

@router.message(SellProductSG.waiting_for_qty)
async def sell_qty(message: Message, state: FSMContext):
    try:
        qty = int(message.text)
        if qty <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Please enter a valid positive number.", reply_markup=cancel_kb)
        return

    data = await state.get_data()
    prod_name = data["prod_name"]
    price = data["prod_price"]
    current_stock = data["current_stock"]

    if qty > current_stock:
        await message.answer(f"❌ Not enough stock! You only have {current_stock} available.", reply_markup=cancel_kb)
        return

    total_cost = price * qty
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("database/shop.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (qty, prod_name))
    cursor.execute("""
        INSERT INTO sales (product_name, qty, total, date)
        VALUES (?, ?, ?, ?)
    """, (prod_name, qty, total_cost, today))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer(
        f"✅ Sale logged successfully!\n\n📦 <b>Receipt:</b>\n"
        f"Product: {prod_name}\n"
        f"Qty: {qty} × {price}\n"
        f"💰 Total: {total_cost}",
        reply_markup=main_menu
    )