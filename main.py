import asyncio
import logging
import datetime
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Tokenlarni muhitdan olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Bot va dispetcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ma'lumotlarni saqlash
user_data = {}
all_users = set()

# Video URL manzillari (Namuna sifatida, foydalanuvchi buni o'zgartirishi mumkin)
# DIQQAT: Telegram ba'zi saytlardan to'g'ridan-to'g'ri URL orqali videoni yuklay olmasligi mumkin.
# Bunday holda videoni file_id orqali yuborish eng yaxshi yo'ldir.
VIDEOS = {
    "top_videos": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4", # Namuna URL
    "cartoons": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4",
    "extreme_videos": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
}

class UserState(StatesGroup):
    main_menu = State()
    vip_menu = State()

class AdminState(StatesGroup):
    waiting_for_broadcast_msg = State()

# --- Keyboards ---
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

def get_admin_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="⬅️ Chiqish", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Handlers ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    all_users.add(user_id)
    
    if user_id not in user_data:
        user_data[user_id] = {
            "daily_views": 0,
            "last_view_date": datetime.date.today(),
            "is_vip": False,
            "vip_expires": None
        }
    
    if user_data[user_id]["last_view_date"] != datetime.date.today():
        user_data[user_id]["daily_views"] = 0
        user_data[user_id]["last_view_date"] = datetime.date.today()

    await message.answer("Привет! Добро пожаловать в наш бот!", reply_markup=get_main_keyboard())
    await state.set_state(UserState.main_menu)

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        await message.answer("Admin paneliga xush kelibsiz!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("Kechirasiz, bu bo'lim faqat adminlar uchun.")

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if str(callback.from_user.id) == str(ADMIN_ID):
        count = len(all_users)
        await callback.message.edit_text(f"📊 Bot foydalanuvchilari soni: {count} ta", reply_markup=get_admin_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) == str(ADMIN_ID):
        await callback.message.edit_text("Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yozing:")
        await state.set_state(AdminState.waiting_for_broadcast_msg)
    await callback.answer()

@dp.message(AdminState.waiting_for_broadcast_msg)
async def process_broadcast(message: types.Message, state: FSMContext):
    if str(message.from_user.id) == str(ADMIN_ID):
        count = 0
        for user_id in all_users:
            try:
                await message.copy_to(chat_id=user_id)
                count += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                logging.error(f"Xabar yuborishda xato (ID: {user_id}): {e}")
        
        await message.answer(f"📢 Xabar {count} ta foydalanuvchiga yuborildi.", reply_markup=get_admin_keyboard())
        await state.clear()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Главное menu:", reply_markup=get_main_keyboard())
    await state.set_state(UserState.main_menu)
    await callback.answer()

@dp.callback_query(F.data.in_(["top_videos", "cartoons", "extreme_videos"]))
async def handle_content_request(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {"daily_views": 0, "last_view_date": datetime.date.today(), "is_vip": False}
        all_users.add(user_id)

    if user_data[user_id]["is_vip"] or user_data[user_id]["daily_views"] < 3:
        user_data[user_id]["daily_views"] += 1
        video_url = VIDEOS.get(callback.data)
        
        try:
            # Video URL orqali yuboriladi
            await callback.message.answer_video(
                video=video_url,
                caption=f"Вот ваше видео по запросу '{callback.data}'.\nПросмотров сегодня: {user_data[user_id]['daily_views']}/3"
            )
        except Exception as e:
            logging.error(f"Video yuborishda xato: {e}")
            await callback.message.answer(f"⚠️ Ошибка при загрузке видео. Возможно, URL недоступен.\nПопробуйте позже.")
    else:
        await callback.message.answer("Вы исчерпали лимит просмотров на сегодня (3/3). Оформите VIP подписку!")
    await callback.answer()

@dp.callback_query(F.data == "vip_subscribe")
async def show_vip_options(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    status = "У вас нет активной VIP подписки."
    if user_data.get(user_id, {}).get("is_vip"):
        status = f"Ваша VIP подписка активna do {user_data[user_id]['vip_expires'].strftime('%Y-%m-%d')}."
    
    await callback.message.edit_text(f"VIP Подписка:\n{status}\n\nЦена: 100 Telegram Stars\nПреимущества: Безлимитный просмотр!", reply_markup=get_vip_keyboard())
    await state.set_state(UserState.vip_menu)
    await callback.answer()

@dp.callback_query(F.data == "buy_vip")
async def process_buy_vip(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="VIP Подписка", amount=100)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="VIP Подписка",
        description="Безлимитный доступ на 30 дней",
        payload="vip_subscription_payload",
        provider_token="", 
        currency="XTR",
        prices=prices
    )
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["is_vip"] = True
    user_data[user_id]["vip_expires"] = datetime.datetime.now() + datetime.timedelta(days=30)
    await message.answer(f"Спасибо за покупku! VIP активна до {user_data[user_id]['vip_expires'].strftime('%Y-%m-%d')}.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
