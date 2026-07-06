from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inline Keyboard for Main Categories
categories_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Food 🍏", callback_data="cat_Food"), InlineKeyboardButton(text="Cosmetics 💄", callback_data="cat_Cosmetics")],
        [InlineKeyboardButton(text="Soap 🧼", callback_data="cat_Soap"), InlineKeyboardButton(text="Sanitation 🧻", callback_data="cat_Sanitation")],
        [InlineKeyboardButton(text="Jewelry 💎", callback_data="cat_Jewelry"), InlineKeyboardButton(text="Toys 🧸", callback_data="cat_Toys")],
        [InlineKeyboardButton(text="Clothes 👕", callback_data="cat_Clothes"), InlineKeyboardButton(text="Perfume 🧪", callback_data="cat_Perfume")],
        [InlineKeyboardButton(text="Hair 💈", callback_data="cat_Hair"), InlineKeyboardButton(text="Other 📦", callback_data="cat_Other")]
    ]
)