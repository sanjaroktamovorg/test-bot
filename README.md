# Test Bot - O'quvchilar uchun test tizimi

## Loyiha haqida
Bu loyiha o'quvchilar va o'qituvchilar uchun test tizimi bo'lib, Telegram bot orqali ishlaydi.

## Asosiy funksiyalar
- **O'quvchilar:** Testlarni ishlash, natijalarni ko'rish
- **O'qituvchilar:** Testlar tuzish, natijalarni boshqarish

## Texnologiyalar
- Python 3.9+
- FastAPI (API uchun)
- python-telegram-bot (Telegram bot)
- SQLAlchemy (Database)
- SQLite/PostgreSQL

## O'rnatish
1. `pip install -r requirements.txt`
2. `.env.example` ni `.env` ga nusxalang va sozlang
3. `python main.py` ni ishga tushiring

## Loyiha strukturasi
```
test-bot/
├── src/
│   ├── bot/          # Telegram bot moduli
│   ├── api/          # API moduli
│   ├── database/     # Database moduli
│   ├── models/       # Data modellar
│   ├── services/     # Biznes logika
│   └── utils/        # Yordamchi funksiyalar
├── config/           # Konfiguratsiya
├── logs/             # Log fayllar
├── backups/          # Backup fayllar
└── tests/            # Testlar
```
