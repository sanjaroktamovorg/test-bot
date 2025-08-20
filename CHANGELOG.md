# Test Bot - Changelog

## [v0.9] - 2025-08-20

### ✅ Database yangilandi
- **Yangi ustunlar qo'shildi** - test_type, category, subject, test_code
- **Database jadvali qayta yaratildi** - Yangi schema bilan
- **Test turi tizimi** - SIMPLE, DTM, NATIONAL_CERTIFICATE, OPEN
- **Test toifasi** - PUBLIC, PRIVATE
- **Maxsus kod tizimi** - Shaxsiy testlar uchun

### 🔧 Texnik o'zgarishlar
- Database migration to'liq amalga oshirildi
- Yangi modellar to'g'ri ishlayapti
- Bot polling rejimida ishlayapti
- Xatoliklar bartaraf etildi

### 🎯 Yangi funksiyalar
- **Test turi tanlash** - Oddiy test, DTM, Milliy sertifikat, Ochiq test
- **Test toifasi** - Ommaviy va shaxsiy testlar
- **Maxsus kod** - Shaxsiy testlar uchun maxsus kod
- **Fan tanlash** - Test uchun fan belgilash

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Database to'g'ri ishlayapti ✅
- Modullar to'g'ri ishlayapti ✅
- Telegram API bilan bog'lanish ✅

---

## [v0.6] - 2025-08-20

### ✅ Qo'shilgan funksiyalar
- **Test turlari tizimi** - 4 xil test turi
  - 📝 Oddiy test (to'liq ishlaydi)
  - 🏛️ DTM test (ishlab chiqilmoqda)
  - 🏆 Milliy sertifikat test (ishlab chiqilmoqda)
  - 📖 Ochiq (variantsiz) test (ishlab chiqilmoqda)

- **Test toifalari** - 10 xil toifa
  - 📐 Matematika, ⚡ Fizika
  - 🧪 Kimyo, 🌿 Biologiya
  - 📚 Tarix, 🌍 Geografiya
  - 📖 Adabiyot, 🗣️ Til
  - 💻 Informatika, 📋 Boshqa

- **Yangi test yaratish jarayoni**
  - Test turi tanlash (Reply keyboard)
  - Test toifasi tanlash (Reply keyboard)
  - Test ma'lumotlari kiritish
  - Avtomatik test yaratish

- **Reply Keyboard Markup**
  - O'qituvchilar uchun asosiy tugmalar
  - O'quvchilar uchun asosiy tugmalar
  - Test turi va toifasi tanlash tugmalari

### 🔧 Texnik o'zgarishlar
- Yangi modellar qo'shildi: `TestType`, `TestCategory`
- `TestCreationService` yangilandi
- Bot handerlari qayta yozildi
- Database strukturasi yangilandi

### 🐛 Tuzatilgan xatoliklar
- Indentation xatoliklari tuzatildi
- Import xatoliklari bartaraf etildi
- Database yaratish muammolari hal qilindi

### 📁 Fayl strukturasi
```
src/
├── models/
│   ├── test_types.py (YANGI)
│   ├── user.py
│   ├── test.py (yangilandi)
│   └── result.py
├── services/
│   ├── test_creation_service.py (yangilandi)
│   ├── test_taking_service.py
│   └── user_service.py
└── bot/
    └── bot.py (qayta yozildi)
```

## [v0.5] - 2025-08-20

### ✅ Qo'shilgan funksiyalar
- Asosiy bot strukturasi
- Database modellar
- User va Test servislari
- Reply keyboard va inline buttonlar

## [v0.1] - 2025-08-20

### ✅ Qo'shilgan funksiyalar
- Loyiha asosiy strukturasi
- Telegram bot integratsiyasi
- SQLAlchemy database
- Git versiya boshqaruvi

---

## Keyingi rejalar (v0.7+)

### 🚧 Ishlab chiqilmoqda
- Test ishlash funksiyasi
- Savollar qo'shish
- Natija ko'rish
- Reyting tizimi

### 📋 Rejalashtirilgan
- DTM test turlari
- Milliy sertifikat testlar
- Ochiq testlar
- Web sayt integratsiyasi
- API endpointlar
