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



TOKEN = "Tokeningizni_shu_yerga_yozing"

dp = Dispatcher()


# 1. FSM uchun holatlar (States)
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

# Telefon raqamni yuborish tugmasi (Sizda tushib qolgan edi)
def get_phone_keyboard():
    buttons = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# Xabar ostidagi tugmalar (Inline Keyboard)
def get_inline_menu():
    buttons = [
        [InlineKeyboardButton(text="Bizning sayt", callback_data="site_soon")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Tasdiqlash uchun Inline tugma (Sizda tushib qolgan funksiya)
def get_confirmation_menu():
    buttons = [
        [
            InlineKeyboardButton(text="Ha, yuborilsin ✅", callback_data="register_confirm"),
            InlineKeyboardButton(text="Yo'q, bekor qilish ❌", callback_data="register_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- HANDLERLAR (FUNKSIYALAR) ---

# /start buyrug'i
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Salom {message.from_user.full_name}! Server muvaffaqiyatli ishlayapti. "
        f"Quyidagi menyudan biror bo'limni tanlang:",
        reply_markup=get_main_menu()
    )


# "Biz haqimizda" tugmasi
@dp.message(F.text == "ℹ️ Biz haqimizda")
async def about_handler(message: Message):
    await message.answer(
        "Tayyorlanmoqda >>>> Tez kunda ",
        reply_markup=get_inline_menu()
    )

# "Aloqa" tugmasi
@dp.message(F.text == "📞 Aloqa")
async def contact(message: Message):
    await message.answer(
        "Biz bilan bog'lanish uchun @xojiyevdavron ga yozing",
        reply_markup=get_cancel_keyboard()
    )

# Bosh menyuga qaytish tugmasi
@dp.message(F.text == "⬅️ Bosh menyuga qaytish")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()  # Har qanday holatni tozalaymiz
    await message.answer(
        "Siz asosiy menyuga qaytdingiz:",
        reply_markup=get_main_menu()
    )


# --- FSM JARAYONI ---

# Ro'yxatdan o'tishni boshlash
@dp.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_register(message: Message, state: FSMContext):
    await message.answer(
        "Sizni ro'yxatdan o'tkazamiz. Iltimos, ismingizni kiriting:",
        reply_markup=get_cancel_keyboard()  # Ism kiritayotganda ham qaytish imkoni bo'lsin
    )
    await state.set_state(Registration.waiting_for_name)


# Ism kiritilganda
@dp.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Rahmat! Endi pastdagi tugma orqali telefon raqamingizni yuboring:",
        reply_markup=get_phone_keyboard()  # Maxsus kontakt tugmasi ko'rsatiladi
    )
    await state.set_state(Registration.waiting_for_phone)


# Telefon raqam kiritilganda
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

    await message.answer(
        f"Kiritgan ma'lumotlaringiz to'g'rimi? 🤔\n\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}\n\n"
        f"Hamma ma'lumot to'g'ri bo'lsa, tasdiqlang. Admin guruhiga yuboriladi.",
        reply_markup=get_confirmation_menu()
    )


# --- CALLBACK HANDLERLAR ---

@dp.callback_query(F.data == "site_soon")
async def process_site_soon(callback: CallbackQuery):
    await callback.answer(
        "Saytimiz hozirda yaratilmoqda, tez kunda ishga tushadi! 🚀",
        show_alert=True
    )


ADMIN_ID = 6240885361  # Admin ID raqami


@dp.callback_query(F.data == "register_confirm")
async def confirm_registration(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    name = user_data.get("name")
    phone = user_data.get("phone")

    if not name or not phone:
        await callback.message.answer("Xatolik: Ma'lumotlar topilmadi. Qaytadan ro'yxatdan o'ting.")
        await state.clear()
        return

    # Adminga yuborish
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 Yangi ro'yxatdan o'tgan foydalanuvchi:\n\n"
             f"👤 Ism: {name}\n"
             f"📞 Telefon: {phone}\n"
             f"🆔 Telegram: @{callback.from_user.username or 'Mavjud emas'}"
    )

    await callback.message.edit_text("Ma'lumotlaringiz adminga muvaffaqiyatli yuborildi! 🎉")
    await callback.message.answer("Asosiy menyu:", reply_markup=get_main_menu())
    await state.clear()
    await callback.answer()


@dp.callback_query(F.data == "register_cancel")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Ro'yxatdan o'tish bekor qilindi. ❌")
    await callback.message.answer("Asosiy menyu:", reply_markup=get_main_menu())
    await state.clear()
    await callback.answer()


# Botni ishga tushirish
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())