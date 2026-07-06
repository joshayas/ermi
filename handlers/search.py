import sqlite3
from rapidfuzz import process
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

# Define an FSM state for searching
class SearchSG(StatesGroup):
    waiting_for_query = State()


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

    cur.execute("""
        SELECT name, category, subcategory, price, stock, photo
        FROM products
        WHERE name=?
    """, (name,))

    data = cur.fetchone()
    conn.close()
    return data


# Trigger search and move user into the FSM state
@router.message(F.text.contains("Search"))
async def search_start(message: Message, state: FSMContext):
    await state.set_state(SearchSG.waiting_for_query)
    await message.answer("🔎 Type product name:")


# This handler will ONLY trigger if the user is explicitly in the search state
@router.message(SearchSG.waiting_for_query)
async def search_handler(message: Message, state: FSMContext):
    if not message.text:
        return

    products = get_all_products()

    if not products:
        await message.answer("❌ No products found")
        await state.clear()  # Safely exit state
        return

    result = process.extract(message.text, products, limit=1)

    # rapidfuzz returns a list of tuples: [(name, score, index), ...]
    if not result:
        await message.answer("❌ No match found")
        await state.clear()
        return

    best = result[0][0]
    product = get_product(best)

    if not product:
        await message.answer("❌ Product not found")
        await state.clear()
        return

    name, category, subcategory, price, stock, photo = product

    text = f"""
📦 <b>PRODUCT</b>

Name: {name}
Category: {category}
Subcategory: {subcategory}
Price: {price}
Stock: {stock}
"""

    # Clear state so the user can interact with other menu options normally again
    await state.clear()

    if photo:
        await message.answer_photo(photo, caption=text)
    else:
        await message.answer(text)