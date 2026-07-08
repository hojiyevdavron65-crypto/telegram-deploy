import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

TOKEN = "8713021157:AAE-IW2HesesHRAThkJiQJ7UUWX_yP3dE2Y"

# Serverda nima bo'layotganini ko'rib turish uchun loglarni yoqamiz
logging.basicConfig(level=logging.INFO)

dp = Dispatcher()


# 1. FSM uchun holatlar (States) yaratib olamiz (Ro'yxatdan o'tish uchun)
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()


# --- TUGMALAR (KEYBOARDS) ---

# Oddiy pastki tugmalar (Reply Keyboard)
def get_main_menu():
    buttons = [
        [KeyboardButton(text="📝 Ro'yxatdan o'tish"), KeyboardButton(text="ℹ️ Biz haqimizda")],
        [KeyboardButton(text="📞 Aloqa")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# Xabar ostidagi tugmalar (Inline Keyboard)
def get_inline_menu():
    buttons = [
        [InlineKeyboardButton(text="Bizning sayt", url="https://aiogram.dev")],
        [InlineKeyboardButton(text="Tasdiqlash ✅", callback_data="confirm_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- HANDLERLAR (FUNKSIYALAR) ---

# /start buyrug'i kelganda menyuni ko'rsatamiz
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Salom {message.from_user.full_name}! Server muvaffaqiyatli ishlayapti. "
        f"Quyidagi menyudan biror bo'limni tanlang:",
        reply_markup=get_main_menu()
    )


# "Biz haqimizda" tugmasi bosilganda (Matnli handler)
@dp.message(F.text == "ℹ️ Biz haqimizda")
async def about_handler(message: Message):
    await message.answer(
        "Bu aiogram 3.x kutubxonasida yaratilgan professional bot prototipi.",
        reply_markup=get_inline_menu()  # Inline tugmani shu yerda ko'rsatamiz
    )


# --- FSM (KETMA-KET MA'LUMOT OLISH) JARYONI ---

# Foydalanuvchi "Ro'yxatdan o'tish" tugmasini bossa, jarayonni boshlaymiz
@dp.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_register(message: Message, state: FSMContext):
    await message.answer("Sizni ro'yxatdan o'tkazamiz. Iltimos, ismingizni kiriting:")
    # Botni foydalanuvchidan ism kutish holatiga o'tkazamiz
    await state.set_state(Registration.waiting_for_name)


# Ism kiritilganda ishlaydiyan handler
@dp.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    # Kiritilgan ismni xotiraga saqlaymiz
    await state.update_data(name=message.text)

    await message.answer("Rahmat! Endi telefon raqamingizni kiriting:")
    # Keyingi holatga o'tamiz
    await state.set_state(Registration.waiting_for_phone)


# Telefon raqam kiritilganda ishlaydigan handler
@dp.message(Registration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    # Telefon raqamni saqlaymiz
    await state.update_data(phone=message.text)

    # Barcha saqlangan ma'lumotlarni olamiz
    user_data = await state.get_data()

    name = user_data.get("name")
    phone = user_data.get("phone")

    await message.answer(
        f"Muvaffaqiyatli ro'yxatdan o'tdingiz! 🎉\n\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}"
    )
    # FSM jarayonini yakunlaymiz va xotirani tozalaymiz
    await state.clear()


# --- INLINE TUGMA BOSILGANDA (CALLBACK QUERY) ---
@dp.callback_query(F.data == "confirm_action")
async def process_confirm(callback: CallbackQuery):
    # Inline tugma bosilganda bildirishnoma ko'rsatamiz
    await callback.answer("Amal tasdiqlandi!", show_alert=True)


# Botni ishga tushirish
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())