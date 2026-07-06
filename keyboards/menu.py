from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Add Product"), KeyboardButton(text="🛒 Sell")],
        [KeyboardButton(text="🔍 Search"), KeyboardButton(text="📊 Report")],
        [KeyboardButton(text="📦 Stock"), KeyboardButton(text="💸 Expense")]
    ],
    resize_keyboard=True
)