import asyncio

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

def get_cancel_keyboard():
    buttons = [
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# Xabar ostidagi tugmalar (Inline Keyboard)
def get_inline_menu():
    buttons = [
        [InlineKeyboardButton(text="Bizning sayt", callback_data="site_soon")],

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
        "Tayyorlanmoqda >>>> Tez kunda ",
        reply_markup=get_inline_menu()  # Inline tugmani shu yerda ko'rsatamiz
    )

@dp.message(F.text=="📞 Aloqa")
async def contact(message:Message):
    await message.answer(
        "Biz bog'lanish uchun @xojiyevdavron ga yozing",
        reply_markup=get_cancel_keyboard()
    )

@dp.message(F.text=="⬅️ Bosh menyuga qaytish")
async def back_to_main_menu(message:Message):
    await message.answer(
        "Siz asosiy menyuga qaytdingiz:",
        reply_markup=get_main_menu()
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
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    await state.update_data(phone=phone_number)
    user_data = await state.get_data()

    name = user_data.get("name")
    phone = user_data.get("phone")

    # Foydalanuvchiga tekshirish uchun ko'rsatamiz
    await message.answer(
        f"Kiritgan ma'lumotlaringiz to'g'rimi? 🤔\n\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}\n\n"
        f"Hamma ma'lumot to'g'ri bo'lsa, tasdiqlang. Admin guruhiga yuboriladi.",
        reply_markup=get_confirmation_menu()  # Tasdiqlash tugmalari
    )



@dp.callback_query(F.data == "site_soon")
async def process_site_soon(callback: CallbackQuery):
    # Foydalanuvchining ekraniga kichkina ogohlantirish oynasi chiqaradi
    await callback.answer(
        "Saytimiz hozirda yaratilmoqda, tez kunda ishga tushadi! 🚀",
        show_alert=True
    )


ADMIN_ID = 6240885361  # Bu yerga o'zingizning telegram ID raqamingizni yozasiz


@dp.callback_query(F.data == "register_confirm")
async def confirm_registration(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # Xotiradan ma'lumotlarni olamiz
    user_data = await state.get_data()
    name = user_data.get("name")
    phone = user_data.get("phone")

    # Agar foydalanuvchi juda kech bossa va xotira o'chib ketgan bo'lsa tekshiramiz
    if not name or not phone:
        await callback.message.answer("Xatolik: Ma'lumotlar topilmadi. Qaytadan ro'yxatdan o'ting.")
        await state.clear()
        return

    # 1. Adminga xabar yuborish
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 Yangi ro'yxatdan o'tgan foydalanuvchi:\n\n"
             f"👤 Ism: {name}\n"
             f"📞 Telefon: {phone}\n"
             f"🆔 Telegram: @{callback.from_user.username or 'Mavjud emas'}"
    )

    # 2. Foydalanuvchining o'ziga javob qaytarish
    await callback.message.edit_text("Ma'lumotlaringiz adminga muvaffaqiyatli yuborildi! 🎉")

    # Asosiy menyuni qaytarib qo'yamiz
    await callback.message.answer("Asosiy menyu:", reply_markup=get_main_menu())

    # Jarayonni yakunlab, xotirani tozalaymiz
    await state.clear()
    await callback.answer()


@dp.callback_query(F.data == "register_cancel")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Ro'yxatdan o'tish bekor qilindi. ❌")
    await callback.message.answer("Asosiy menyu:", reply_markup=get_main_menu())

    # Xotirani o'chiramiz
    await state.clear()
    await callback.answer()




# Botni ishga tushirish
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())