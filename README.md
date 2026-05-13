# Telegram Bot Template (Updated)

Ushbu bot Telegram Stars to'lov tizimi, kunlik limit va video yuborish funksiyasiga ega.

## Video yubormaslik muammosi tuzatildi:
Oldingi versiyada `handle_content_request` funksiyasi faqat matn yuborar edi. Endi u `VIDEOS` lug'atidan video file_id yoki URL manzilini olib, `answer_video` orqali yuboradi.

## Sozlash:
1. `main.py` ichidagi `VIDEOS` lug'atiga o'zingizning video `file_id`laringizni yoki URL manzillaringizni qo'shing.
2. `BOT_TOKEN` va `ADMIN_ID` muhit o'zgaruvchilarini (Environment Variables) sozlang.
3. Kutubxonalarni o'rnating: `pip install -r requirements.txt`
4. Botni ishga tushiring: `python main.py`

## Muhim:
Videolarni yuborish uchun Telegram'ga yuklangan videoning `file_id`sini ishlatish tavsiya etiladi. Bu botning tezroq ishlashini ta'minlaydi.
