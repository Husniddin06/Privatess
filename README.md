# Telegram Bot (Admin Video Management)

Ushbu bot Telegram Stars to'lov tizimi, kunlik limit va admin tomonidan videolarni boshqarish funksiyasiga ega.

## Yangi funksiyalar:
1.  **Admin Panel:** `/admin` buyrug'i orqali kiriladi.
2.  **Video qo'shish:** Endi admin botning o'zidan turib videolarni qo'shishi yoki yangilashi mumkin.
3.  **Ma'lumotlarni saqlash:** Foydalanuvchilar va videolar `bot_data.json` faylida saqlanadi (bot o'chib yonsa ham ma'lumotlar yo'qolmaydi).

## Videolarni qanday qo'shish kerak:
1.  Botga `/admin` deb yozing.
2.  "Video qo'shish" tugmasini bosing.
3.  Kategoriyani tanlang (masalan, "Топ Видео").
4.  Botga videoni yuboring yoki video havolasini (.mp4) yozing.
5.  Tayyor! Endi foydalanuvchilar o'sha videoni ko'ra olishadi.

## Sozlash:
1.  `BOT_TOKEN` va `ADMIN_ID` muhit o'zgaruvchilarini sozlang.
2.  Kutubxonalarni o'rnating: `pip install -r requirements.txt`
3.  Botni ishga tushiring: `python main.py`
