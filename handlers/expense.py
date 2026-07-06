import sqlite3
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.menu import main_menu

router = Router()

class ExpenseSG(StatesGroup):
    waiting_for_title = State()
    waiting_for_amount = State()

cancel_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Cancel Action")]], resize_keyboard=True)

@router.message(F.text.contains("Expense"))
async def expense_start(message: Message, state: FSMContext):
    await state.set_state(ExpenseSG.waiting_for_title)
    await message.answer("💸 Enter what the expense is for (e.g., Rent, Utility):", reply_markup=cancel_kb)

@router.message(ExpenseSG.waiting_for_title)
async def expense_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ExpenseSG.waiting_for_amount)
    await message.answer("💰 Enter total cost/amount paid:", reply_markup=cancel_kb)

@router.message(ExpenseSG.waiting_for_amount)
async def expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("❌ Enter a valid number.")
        return

    data = await state.get_data()
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("database/shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (title, amount, date) VALUES (?, ?, ?)", (data["title"], amount, today))
    conn.commit()
    conn.close()

    await state.clear()
    await message.answer(f"✅ Logged Expense: {data['title']} (-{amount})", reply_markup=main_menu)