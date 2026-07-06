import sqlite3
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.buttons import categories_kb
from keyboards.menu import main_menu

router = Router()

# Universal Reply Cancel Interceptor
@router.message(F.text.contains("Cancel Action"))
async def process_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🛑 Action cancelled.", reply_markup=main_menu)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Cancel Action")]],
    resize_keyboard=True
)

class AddProductSG(StatesGroup):
    category = State()
    subcategory = State()
    name = State()
    price = State()
    stock = State()
    photo = State()

SUBCATEGORIES = {
    "Food": ["Biscuits", "Chocolate", "Candy", "Chips", "Juice", "Soft Drinks", "Bottled Water", "Canned Food", "Spices", "Other"],
    "Soap": ["Bar Soap", "Liquid Soap", "Toothpaste", "Body Soap", "Face Soap", "Other"],
    "Jewelry": ["Necklaces", "Ring", "Earring", "Other"],
    "Cosmetics": ["Lotion", "Shampoo", "Conditioner", "Hair Oil", "Hair Cream", "Hair Gel", "Lipstick", "Other"],
    "Sanitation": ["Bleach", "Tissue", "Cleaner", "Other"],
    "Toys": ["Cars", "Dolls", "Other"],
    "Clothes": ["Underwear", "Bra", "Socks", "Other"],
    "Perfume": ["Perfume", "Deodorant", "Other"],
    "Hair": ["Wig", "Extension", "Other"],
    "Other": ["Other"]
}

@router.message(F.text.contains("Add Product"))
async def add_start(message: Message, state: FSMContext):
    await state.set_state(AddProductSG.category)
    await message.answer("📂 Select Category:", reply_markup=categories_kb)

# Catching Category Inline Click
@router.callback_query(AddProductSG.category, F.data.startswith("cat_"))
async def add_category(callback: CallbackQuery, state: FSMContext):
    selected_cat = callback.data.split("_")[1]
    await state.update_data(category=selected_cat)
    await state.set_state(AddProductSG.subcategory)
    
    # Generate dynamic subcategory inline buttons
    subs = SUBCATEGORIES.get(selected_cat, ["Other"])
    buttons = []
    row = []
    for sub in subs:
        row.append(InlineKeyboardButton(text=sub, callback_data=f"sub_{sub}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    sub_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(f"📁 Category: <b>{selected_cat}</b>\nSelect Subcategory:", reply_markup=sub_kb)
    await callback.answer()

# Catching Subcategory Inline Click
@router.callback_query(AddProductSG.subcategory, F.data.startswith("sub_"))
async def add_subcategory(callback: CallbackQuery, state: FSMContext):
    selected_sub = callback.data.split("_")[1]
    await state.update_data(subcategory=selected_sub)
    await state.set_state(AddProductSG.name)
    
    await callback.message.answer("✏️ Enter Product Name:", reply_markup=cancel_kb)
    await callback.message.delete()  # Clean up inline message
    await callback.answer()

@router.message(AddProductSG.name)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProductSG.price)
    await message.answer("💰 Enter Price:", reply_markup=cancel_kb)

@router.message(AddProductSG.price)
async def add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await state.set_state(AddProductSG.stock)
        await message.answer("📦 Enter Stock:", reply_markup=cancel_kb)
    except ValueError:
        await message.answer("❌ Enter valid numerical price.", reply_markup=cancel_kb)

@router.message(AddProductSG.stock)
async def add_stock(message: Message, state: FSMContext):
    try:
        stock = int(message.text)
        await state.update_data(stock=stock)
        await state.set_state(AddProductSG.photo)
        await message.answer("📷 Send Product Photo:", reply_markup=cancel_kb)
    except ValueError:
        await message.answer("❌ Enter valid stock integer.", reply_markup=cancel_kb)

@router.message(AddProductSG.photo, F.photo)
async def save_product(message: Message, state: FSMContext):
    data = await state.get_data()
    
    conn = sqlite3.connect("database/shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, subcategory, price, stock, photo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["name"], data["category"], data["subcategory"], data["price"], data["stock"], message.photo[-1].file_id))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer("✅ Product saved successfully!", reply_markup=main_menu)