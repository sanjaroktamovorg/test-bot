# Test Bot - Loyiha Holati

## ✅ Bajarilgan ishlar

### 1. Loyiha strukturasi
- ✅ Modullashtirilgan arxitektura
- ✅ Src papkasi tuzilishi
- ✅ Konfiguratsiya fayllari

### 2. Database
- ✅ SQLAlchemy modellar
- ✅ User, Test, Question, Answer, TestResult jadvallari
- ✅ Database yaratish scripti
- ✅ SQLite database ishlaydi

### 3. Telegram Bot
- ✅ python-telegram-bot integratsiyasi
- ✅ Asosiy komandalar (/start, /help, /register)
- ✅ O'qituvchi va o'quvchi rollari
- ✅ Inline keyboard tugmalari

### 4. Servislar
- ✅ UserService - foydalanuvchilar boshqaruvi
- ✅ TestService - testlar boshqaruvi
- ✅ Database ulanish

### 5. Git va Versiya boshqaruvi
- ✅ Git repository
- ✅ .gitignore
- ✅ Commit history

## 🔄 Keyingi qadamlar

### 1. Test yaratish funksiyasi
- [ ] O'qituvchi test yaratish
- [ ] Savollar qo'shish
- [ ] Javoblar qo'shish

### 2. Test ishlash funksiyasi
- [ ] O'quvchi testni boshlash
- [ ] Savollarga javob berish
- [ ] Natija hisoblash

### 3. API integratsiyasi
- [ ] FastAPI endpointlar
- [ ] Webhook integratsiyasi
- [ ] REST API

### 4. Web sayt
- [ ] React frontend
- [ ] Admin panel
- [ ] Dashboard

## 🚀 Ishga tushirish

```bash
# 1. Loyihani klonlash
git clone <repository_url>
cd test-bot

# 2. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 3. Database yaratish
python3 create_database.py

# 4. Bot tokenini sozlash
# .env faylida TELEGRAM_BOT_TOKEN ni o'rnating

# 5. Botni ishga tushirish
python3 main.py
```

## �� Loyiha strukturasi

```
test-bot/
├── src/
│   ├── bot/          # Telegram bot
│   ├── api/          # API moduli (keyinchalik)
│   ├── database/     # Database
│   ├── models/       # Data modellar
│   ├── services/     # Biznes logika
│   └── utils/        # Yordamchi funksiyalar
├── config/           # Konfiguratsiya
├── logs/             # Log fayllar
├── backups/          # Backup fayllar
├── tests/            # Testlar
├── main.py           # Asosiy dastur
├── requirements.txt  # Python kutubxonalar
└── README.md         # Loyiha ma'lumoti
```

## 🎯 Asosiy funksiyalar

### O'qituvchilar uchun:
- Testlar yaratish
- Savollar qo'shish
- Natijalarni ko'rish

### O'quvchilar uchun:
- Mavjud testlarni ko'rish
- Testlarni ishlash
- Natijalarni ko'rish

## 🔧 Texnologiyalar

- **Backend:** Python 3.9+
- **Telegram Bot:** python-telegram-bot
- **Database:** SQLAlchemy + SQLite
- **API:** FastAPI (keyinchalik)
- **Frontend:** React (keyinchalik)
