import asyncio
import logging
import datetime
import os
import json
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

# Ma'lumotlarni saqlash fayli
DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "all_users": [], "videos": {
        "top_videos": None,
        "cartoons": None,
        "extreme_videos": None
    }}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Ma'lumotlarni yuklash
data = load_data()

class UserState(StatesGroup):
    main_menu = State()
    vip_menu = State()

class AdminState(StatesGroup):
    waiting_for_broadcast_msg = State()
    waiting_for_video = State()

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
        [InlineKeyboardButton(text="📹 Video qo'shish", callback_data="admin_add_video")],
        [InlineKeyboardButton(text="⬅️ Chiqish", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_video_categories_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Топ Видео", callback_data="set_top_videos")],
        [InlineKeyboardButton(text="Мультфильмы", callback_data="set_cartoons")],
        [InlineKeyboardButton(text="Самые Жёсткие", callback_data="set_extreme_videos")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Handlers ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_id not in data["all_users"]:
        data["all_users"].append(user_id)
    
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "daily_views": 0,
            "last_view_date": str(datetime.date.today()),
            "is_vip": False,
            "vip_expires": None
        }
    
    if data["users"][user_id]["last_view_date"] != str(datetime.date.today()):
        data["users"][user_id]["daily_views"] = 0
        data["users"][user_id]["last_view_date"] = str(datetime.date.today())
    
    save_data(data)
    await message.answer("Привет! Добро пожаловать в наш бот!", reply_markup=get_main_keyboard())
    await state.set_state(UserState.main_menu)

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        await message.answer("Admin paneliga xush kelibsiz!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("Kechirasiz, bu bo'lim faqat adminlar uchun.")

@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if str(callback.from_user.id) == str(ADMIN_ID):
        await callback.message.edit_text("Admin paneliga xush kelibsiz!", reply_markup=get_admin_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if str(callback.from_user.id) == str(ADMIN_ID):
        count = len(data["all_users"])
        await callback.message.edit_text(f"📊 Bot foydalanuvchilari soni: {count} ta", reply_markup=get_admin_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "admin_add_video")
async def admin_add_video(callback: types.CallbackQuery):
    if str(callback.from_user.id) == str(ADMIN_ID):
        await callback.message.edit_text("Qaysi kategoriya uchun video qo'shmoqchisiz?", reply_markup=get_video_categories_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("set_"))
async def set_video_category(callback: types.CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) == str(ADMIN_ID):
        category = callback.data.replace("set_", "")
        await state.update_data(category=category)
        await callback.message.edit_text(f"Endi '{category}' uchun video yuboring (yoki video havolasini yozing):")
        await state.set_state(AdminState.waiting_for_video)
    await callback.answer()

@dp.message(AdminState.waiting_for_video)
async def process_video_upload(message: types.Message, state: FSMContext):
    if str(message.from_user.id) == str(ADMIN_ID):
        state_data = await state.get_data()
        category = state_data['category']
        
        if message.video:
            data["videos"][category] = message.video.file_id
        elif message.text and (message.text.startswith("http")):
            data["videos"][category] = message.text
        else:
            await message.answer("Iltimos, video yuboring yoki URL manzilini yozing.")
            return

        save_data(data)
        await message.answer(f"✅ '{category}' uchun video muvaffaqiyatli saqlandi!", reply_markup=get_admin_keyboard())
        await state.clear()

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
        for user_id in data["all_users"]:
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
    user_id = str(callback.from_user.id)
    
    if user_id not in data["users"]:
        data["users"][user_id] = {"daily_views": 0, "last_view_date": str(datetime.date.today()), "is_vip": False}
        if user_id not in data["all_users"]:
            data["all_users"].append(user_id)

    if data["users"][user_id]["is_vip"] or data["users"][user_id]["daily_views"] < 3:
        video_content = data["videos"].get(callback.data)
        
        if not video_content:
            await callback.message.answer("⚠️ К сожалению, видео в этой категории еще не добавлено админом.")
            await callback.answer()
            return

        data["users"][user_id]["daily_views"] += 1
        save_data(data)
        
        try:
            await callback.message.answer_video(
                video=video_content,
                caption=f"Вот ваше видео по запросу '{callback.data}'.\nПросмотров сегодня: {data['users'][user_id]['daily_views']}/3"
            )
        except Exception as e:
            logging.error(f"Video yuborishda xato: {e}")
            await callback.message.answer(f"⚠️ Ошибка при отправке видео. Возможно, файл или ссылка недействительны.")
    else:
        await callback.message.answer("Вы исчерпали лимит просмотров на сегодня (3/3). Оформите VIP подписку!")
    await callback.answer()

@dp.callback_query(F.data == "vip_subscribe")
async def show_vip_options(callback: types.CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    status = "У вас нет активной VIP подписки."
    if data["users"].get(user_id, {}).get("is_vip"):
        status = f"Ваша VIP подписка активna do {data['users'][user_id]['vip_expires']}."
    
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
    user_id = str(message.from_user.id)
    data["users"][user_id]["is_vip"] = True
    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    data["users"][user_id]["vip_expires"] = expires.strftime('%Y-%m-%d')
    save_data(data)
    await message.answer(f"Спасибо за покупку! VIP активна до {data[user_id]['vip_expires']}.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
