# Telegram Bot Template (External Video Support)

Ushbu bot Telegram Stars to'lov tizimi, kunlik limit va tashqi URL orqali video yuborish funksiyasiga ega.

## Yangilanishlar:
1. `answer_video` funksiyasi qo'shildi, endi bot haqiqiy videolarni yuboradi.
2. `VIDEOS` lug'ati orqali videolarni tashqi URL manzillardan (masalan, mp4 formatidagi to'g'ridan-to'g'ri havolalar) yuborish imkoniyati yaratildi.

## Sozlash:
1. `main.py` ichidagi `VIDEOS` lug'atiga o'zingiz xohlagan videolarning to'g'ridan-to'g'ri havolalarini (.mp4) qo'ying.
2. `BOT_TOKEN` va `ADMIN_ID` muhit o'zgaruvchilarini sozlang.
3. Kutubxonalarni o'rnating: `pip install -r requirements.txt`
4. Botni ishga tushiring: `python main.py`

## Muhim eslatma:
Telegram orqali video yuborishda, agar URL manzil to'g'ridan-to'g'ri video faylga (.mp4) yo'naltirilgan bo'lsa, bot uni yuklab yubora oladi. Ba'zi kattaroq hajmli yoki maxsus himoyalangan saytlardagi videolarni avval Telegram'ga yuklab, keyin `file_id` orqali ishlatish tavsiya etiladi.
