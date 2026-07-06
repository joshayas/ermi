from aiogram import Router, F
from aiogram.types import Message
from keyboards.menu import main_menu

router = Router()

@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🏪 <b>MiniShop POS System</b>\n\nChoose option:",
        reply_markup=main_menu
    )