import asyncio
import logging
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Bot tokenini BotFather'dan oling va bu yerga qo'ying
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Bot va dispetcherni ishga tushirish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Foydalanuvchi ma'lumotlarini saqlash (Haqiqiy loyihada ma'lumotlar bazasidan foydalaning)
user_data = {}

# FSM holatlari
class UserState(StatesGroup):
    main_menu = State()
    vip_menu = State()

# --- Tugmalar (Keyboards) ---

def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🔥 Топ Видео", callback_data="top_videos")],
        [InlineKeyboardButton(text="🎥 Мультфильмы", callback_data="cartoons")],
        [InlineKeyboardButton(text="🔞 Самые Жёсткие", callback_data="extreme_videos")],
        [InlineKeyboardButton(text="🌟 VIP Подписка", callback_data="vip_subscribe")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_vip_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Купить VIP (100 Stars)", callback_data="buy_vip")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "daily_views": 0,
            "last_view_date": datetime.date.today(),
            "is_vip": False,
            "vip_expires": None
        }
    
    # Kunlik limitni yangilash (har yangi kunda 0 dan boshlanadi)
    if user_data[user_id]["last_view_date"] != datetime.date.today():
        user_data[user_id]["daily_views"] = 0
        user_data[user_id]["last_view_date"] = datetime.date.today()

    await message.answer("Привет! Добро пожаловать в наш бот!", reply_markup=get_main_keyboard())
    await state.set_state(UserState.main_menu)

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Главное меню:", reply_markup=get_main_keyboard())
    await state.set_state(UserState.main_menu)
    await callback.answer()

@dp.callback_query(lambda c: c.data in ["top_videos", "cartoons", "extreme_videos"])
async def handle_content_request(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # VIP yoki limitni tekshirish
    if user_data[user_id]["is_vip"] or user_data[user_id]["daily_views"] < 3:
        user_data[user_id]["daily_views"] += 1
        # Bu yerda haqiqiy video havolasini yuborish mumkin
        await callback.message.answer(f"Вот ваше видео по запросу '{callback.data}'.\nПросмотров сегодня: {user_data[user_id]['daily_views']}/3")
    else:
        await callback.message.answer("Вы исчерпали лимит просмотров на сегодня (3/3). Оформите VIP подписку для безлимитного доступа!")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "vip_subscribe")
async def show_vip_options(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    status = "У вас нет активной VIP подписки."
    if user_data[user_id]["is_vip"]:
        status = f"Ваша VIP подписка активна до {user_data[user_id]['vip_expires'].strftime('%Y-%m-%d')}."
    
    await callback.message.edit_text(f"VIP Подписка:\n{status}\n\nЦена: 100 Telegram Stars\nПреимущества: Безлимитный просмотр всех видео!", reply_markup=get_vip_keyboard())
    await state.set_state(UserState.vip_menu)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "buy_vip")
async def process_buy_vip(callback: types.CallbackQuery):
    # Telegram Stars orqali to'lov yuborish (XTR valyutasi)
    prices = [LabeledPrice(label="VIP Подписка (30 дней)", amount=100)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="VIP Подписка",
        description="Безлимитный доступ на 30 дней",
        payload="vip_subscription_payload",
        provider_token="", # Telegram Stars uchun bo'sh qoldiriladi
        currency="XTR",
        prices=prices
    )
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["is_vip"] = True
    user_data[user_id]["vip_expires"] = datetime.datetime.now() + datetime.timedelta(days=30)
    await message.answer(f"Спасибо за покупку! Ваша VIP подписка активна до {user_data[user_id]['vip_expires'].strftime('%Y-%m-%d')}.")

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
