# Test Bot - Changelog

## [v0.9.32] - 2025-01-27

### ✅ "Orqaga" tugmasi to'liq yangilandi
- **Eski tugmalar olib tashlandi** - Eski asosiy tugmalar to'plami to'liq olib tashlandi
- **Yangi minimal menyu** - Yangi soddalashtirilgan menyu bilan almashtirildi
- **Barcha "Orqaga" tugmalari** - Endi barcha "Orqaga" tugmalari yangi menyuga qaytadi
- **Foydalanuvchi tajribasi** - Yaxshilangan va optimallashtirilgan

### 🔧 Yangi funksiyalar
- **get_back_keyboard()** - Foydalanuvchi roliga qarab asosiy menyuga qaytish
- **Profil tahrirlash** - "Orqaga" tugmasi asosiy menyuga qaytadi
- **Test qidirish** - Xatolikda asosiy menyuga qaytish
- **Barcha funksiyalar** - Yangi minimal menyu bilan ishlaydi

### 📊 Holat
- Bot to'liq ishlayapti ✅
- "Orqaga" tugmasi yangilandi ✅
- Eski tugmalar olib tashlandi ✅
- Yangi menyu bilan ishlaydi ✅

---

## [v0.9.31] - 2025-01-27

### ✅ Asosiy menular soddalashtirildi
- **O'quvchilar menyusi** - Faqat kerakli tugmalar qoldirildi
- **O'qituvchilar menyusi** - Minimal va samimiy interfeys
- **Ortiqcha tugmalar** - "Yordam" va "O'quvchilar" olib tashlandi
- **Foydalanuvchi tajribasi** - Yaxshilangan va optimallashtirilgan

### 🔧 Yangi menyu tuzilishi
- **O'quvchilar:**
  - 📝 Mavjud testlar | 📊 Mening natijalarim
  - 🏆 Reyting | ⚙️ Sozlamalar

- **O'qituvchilar:**
  - 📝 Test yaratish | 📋 Mening testlarim
  - 📊 Natijalar | ⚙️ Sozlamalar

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Menular soddalashtirildi ✅
- Foydalanuvchi tajribasi yaxshilandi ✅
- Interfeys optimallashtirildi ✅

---

## [v0.9.30] - 2025-01-27

### ✅ Profil rasmini qabul qilish va ko'rsatish funksiyasi qo'shildi
- **Rasm qabul qilish** - Profil rasmini yuklash va saqlash
- **Profil ko'rishda rasm** - Saqlangan rasm profil ko'rishda ko'rsatiladi
- **Yordamchi hisobotlar** - Barcha profil maydonlari uchun ma'lumot
- **Xatoliklar tuzatildi** - Rasm qabul qilishda xatoliklar bartaraf etildi

### 🔧 Yangi funksiyalar
- **handle_photo()** - Rasm qabul qilish va saqlash
- **Profil ko'rishda rasm** - reply_photo() bilan rasm ko'rsatish
- **Yordamchi hisobotlar** - Har bir maydon uchun ma'lumot
- **Rasm validatsiyasi** - Rasm mavjudligini tekshirish

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Profil rasmi qabul qilinadi ✅
- Profil ko'rishda rasm ko'rsatiladi ✅
- Yordamchi hisobotlar ishlaydi ✅

---

## [v0.9.29] - 2025-01-27

### ✅ Database schemasi yangilandi va xatoliklar tuzatildi
- **Database yangilandi** - user_settings jadvaliga yangi ustunlar qo'shildi
- **Sozlamalar tugmasi tuzatildi** - endi to'liq ishlaydi
- **O'quvchilar menyusi** - "O'quv materiallari" tugmasi olib tashlandi
- **Profil funksiyalari** - to'liq test qilindi va ishlaydi

### 🔧 Database o'zgarishlari
- **user_settings jadvaliga qo'shildi:**
  - profile_photo (TEXT)
  - full_name (TEXT)
  - age (INTEGER)
  - about (TEXT)
  - experience (INTEGER)
  - specialization (TEXT)

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Database yangilangan ✅
- Sozlamalar tugmasi ishlaydi ✅
- O'quvchilar menyusi soddalashtirildi ✅

---

## [v0.9.28] - 2025-01-27

### ✅ Profil ma'lumotlari to'liq funksional qilindi
- **Bazaga saqlash** - Profil ma'lumotlari UserSettings jadvaliga saqlanadi
- **Profil ko'rish** - Barcha kiritilgan ma'lumotlar profil ko'rishda ko'rsatiladi
- **O'quvchilar uchun** - Rasm kiritish funksiyasi olib tashlandi
- **Ma'lumotlar validatsiyasi** - Yosh va tajriba uchun cheklovlar

### 🔧 Texnik o'zgarishlar
- **UserSettings modeli yangilandi** - Profil maydonlari qo'shildi:
  - profile_photo (profil rasmi URL)
  - full_name (to'liq ism-familya)
  - age (yosh)
  - about (haqida)
  - experience (tajriba)
  - specialization (mutaxassislik)
- **UserService yangilandi** - Profil ma'lumotlarini saqlash va olish metodlari
- **Message handlers yangilandi** - Profil tahrirlash va ko'rish funksiyalari

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Profil ma'lumotlari saqlanadi ✅
- Profil ko'rish to'liq ishlaydi ✅
- O'quvchilar uchun rasm kiritish yo'q ✅

---

## [v0.9.27] - 2025-01-27

### ✅ Profil tugmasi tuzatildi va asosiy menyu soddalashtirildi
- **Profil tugmasi olib tashlandi** - Asosiy menyudan profil tugmasi olib tashlandi
- **Sozlamalar ichida qoldirildi** - Profil faqat sozlamalar bo'limida
- **TestService statistika metodlari** - Yo'q bo'lgan metodlar qo'shildi
- **Xatoliklar tuzatildi** - Profil funksiyalari to'liq ishlaydi

### 🔧 Texnik o'zgarishlar
- **KeyboardFactory yangilandi** - Asosiy menyudan profil tugmasi olib tashlandi
- **TestService to'ldirildi** - Statistika metodlari qo'shildi:
  - get_teacher_tests_count
  - get_teacher_active_tests_count  
  - get_teacher_total_results
  - get_student_completed_tests_count
  - get_student_average_score
  - get_student_best_score

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Profil funksiyasi ishlayapti ✅
- Asosiy menyu soddalashtirildi ✅
- Barcha statistikalar ishlayapti ✅

---

## [v0.9.26] - 2025-01-27

### ✅ Profil tugmasi ishlaydigan qilindi
- **Asosiy menyuga qo'shildi** - Profil tugmasi har ikki foydalanuvchi turi uchun
- **Profil tahrirlash funksiyasi** - O'quvchilar va o'qituvchilar uchun alohida maydonlar
- **Ma'lumotlar validatsiyasi** - Yosh va tajriba uchun cheklovlar
- **Interaktiv tahrirlash** - Har bir maydon uchun alohida oynalar

### 🎯 Yangi funksiyalar
- **👤 Profil tugmasi** - Asosiy menyuda profil ko'rish
- **✏️ Profil tahrirlash** - Shaxsiy ma'lumotlarni kiritish va yangilash
- **O'quvchilar uchun** - Fotosurat, ism-familya, yosh
- **O'qituvchilar uchun** - Fotosurat, ism-familya, yosh, haqida, tajriba, mutaxassislik fani

### 🔧 Texnik o'zgarishlar
- **KeyboardFactory yangilandi** - Asosiy menyuga profil tugmasi qo'shildi
- **Message handlers yangilandi** - Profil tahrirlash funksiyalari
- **Validatsiya qo'shildi** - Yosh va tajriba uchun cheklovlar
- **Sozlamalar paneli** - "Tema" olib tashlandi

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Profil tugmasi ishlayapti ✅
- Profil tahrirlash ishlayapti ✅
- Validatsiya ishlayapti ✅

### 🎯 Afzalliklari
- **Qulaylik** - Profil ma'lumotlarini oson kiritish
- **Xavfsizlik** - Ma'lumotlar validatsiyasi
- **Aniqlik** - Har bir foydalanuvchi turi uchun alohida maydonlar
- **Soddalik** - Interaktiv va tushunarli interfeys

---

## [v0.9.25] - 2025-01-27

### ✅ Sozlamalar paneli soddalashtirildi
- **Barcha foydalanuvchilar uchun bir xil tugmalar** - O'qituvchi va o'quvchi uchun bir xil sozlamalar
- **Soddalashtirilgan tugmalar** - Profil, Til o'zgartirish, Bildirishnomalar, Orqaga
- **Tema o'zgartirish olib tashlandi** - Hozircha kerak emas

### 🎯 Yangi funksiyalar
- **👤 Profil tugmasi** - Foydalanuvchi profil ma'lumotlari va statistikasi
- **📊 Batafsil statistika** - Har bir foydalanuvchi turiga qarab batafsil statistika
- **/ver komandasi** - Bot versiyasi va texnik ma'lumotlarni ko'rsatish

### 🔧 Texnik o'zgarishlar
- **F-string xatoliklari tuzatildi** - Backslash muammolari hal qilindi
- **Message handlers yangilandi** - Profil va statistika funksiyalari qo'shildi
- **Command handlers yangilandi** - /ver komandasi qo'shildi
- **Bot.py yangilandi** - /ver komandasi handler qo'shildi

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Sozlamalar paneli soddalashtirildi ✅
- Profil funksiyasi ishlayapti ✅
- /ver komandasi ishlayapti ✅

### 🎯 Afzalliklari
- **Soddalik** - Barcha foydalanuvchilar uchun bir xil sozlamalar
- **Qulaylik** - Profil ma'lumotlari va statistika ko'rish
- **Aniqlik** - Bot versiyasi va texnik ma'lumotlar
- **Xavfsizlik** - F-string xatoliklari tuzatildi

---

## [v0.9.5] - 2025-08-20

### ✅ Test yaratish jarayoni to'liq soddalashtirildi
- **ABCD format** - Test nomidan keyin to'g'ridan-to'g'ri ABCD formatida javoblar
- **Soddalashtirilgan jarayon** - Faqat test turi, toifa, nom va ABCD javoblar
- **100 tagacha savol** - Bir vaqtda 100 tagacha savol kiritish mumkin
- **Avtomatik test yaratish** - ABCD formatini parse qilib test yaratish

### 🎯 Yangi funksiyalar
- **ABCD format parsing** - abcdabcd... yoki 1a2b3c4d... formatlarini qo'llab-quvvatlash
- **Qisqa ma'lumotlar** - Mavjud testlar bo'limida qisqa ma'lumotlar
- **Ommaviy test yaratish** - Ommaviy testlar yaratish muammosi hal qilindi
- **Enum xatoliklari** - TestStatus va TestType enum xatoliklari tuzatildi

### 🔧 Texnik o'zgarishlar
- **TestCreationService** yangilandi - ABCD format parsing qo'shildi
- **Message handlers** yangilandi - soddalashtirilgan test yaratish
- **Database enum** tuzatildi - .value qo'shildi
- **Error handling** yaxshilandi - xatoliklar to'g'ri ko'rsatiladi

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Test yaratish jarayoni ✅
- Ommaviy testlar yaratiladi ✅
- ABCD format to'g'ri ishlayapti ✅

### 🎯 Afzalliklari
- **Tezlik** - Test yaratish juda tez va oson
- **Qulaylik** - ABCD format bilan test yaratish
- **Aniqlik** - Qisqa va tushunarli ma'lumotlar
- **Xavfsizlik** - Xatoliklar to'g'ri boshqariladi

---

## [v0.9.4] - 2025-08-20

### ✅ Test yaratish jarayoni soddalashtirildi
- **Soddalashtirilgan jarayon** - Faqat kerakli sozlamalar so'raladi
- **Test nomi** - Test nomini kiritish
- **Savollar soni** - Testdagi savollar sonini belgilash
- **Savol va javoblar** - Har bir savol va javob variantlarini kiritish

### 🎯 Yangi funksiyalar
- **Test turi tanlash** - Oddiy test, DTM, Milliy sertifikat, Ochiq test
- **Test toifasi** - Ommaviy va shaxsiy testlar
- **Savollar qo'shish** - Testga savol va javoblar qo'shish
- **Avtomatik test yaratish** - Barcha savollar kiritilgandan keyin

### 🔧 Texnik o'zgarishlar
- **TestCreationService** qayta yozildi
- **Message handlers** yangilandi
- **Multi-step conversation** soddalashtirildi
- **Database modellar** to'g'rilandi

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Test yaratish jarayoni ✅
- Database to'g'ri ishlayapti ✅
- Telegram API bilan bog'lanish ✅

---

## [v0.9.3] - 2025-08-20

### ✅ Har bir foydalanuvchi uchun alohida sozlamalar
- **UserSettings modeli** - Har bir foydalanuvchi uchun alohida sozlamalar
- **Telegram ID asosida** - Har bir akkaunt uchun alohida rol va sozlamalar
- **Rol saqlash** - Har bir foydalanuvchi o'z roli bilan saqlanadi
- **Sozlamalar saqlash** - Til, tema, bildirishnomalar va boshqa sozlamalar

### �� Yangi funksiyalar
- **Dashboard ko'rsatish** - Ro'yxatdan o'tgandan keyin to'g'ridan-to'g'ri dashboard
- **Rol tanlash** - O'qituvchi yoki o'quvchi sifatida ro'yxatdan o'tish
- **Sozlamalar paneli** - Foydalanuvchi sozlamalarini ko'rish va o'zgartirish
- **Alohida ma'lumotlar** - Har bir foydalanuvchi o'z testlari va natijalari bilan

### 🔧 Texnik o'zgarishlar
- **UserSettings modeli** qo'shildi
- **UserService** yangilandi - har bir foydalanuvchi uchun alohida
- **Callback handerlari** yangilandi - dashboard ko'rsatish
- **Command handerlari** yangilandi - to'g'ridan-to'g'ri dashboard
- **Database strukturasi** yangilandi

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Har bir foydalanuvchi alohida ✅
- Database to'g'ri ishlayapti ✅
- Telegram API bilan bog'lanish ✅

### 🎯 Afzalliklari
- **Xavfsizlik** - Har bir foydalanuvchi o'z ma'lumotlari bilan
- **Qulaylik** - Ro'yxatdan o'tgandan keyin to'g'ridan-to'g'ri dashboard
- **Aniqlik** - Har bir foydalanuvchi o'z roli va sozlamalari bilan
- **Kengaytirish** - Yangi sozlamalar oson qo'shiladi

---

## [v0.9.2] - 2025-08-20

### ✅ Test yaratish jarayoni soddalashtirildi
- **Soddalashtirilgan jarayon** - Faqat kerakli sozlamalar so'raladi
- **Test nomi** - Test nomini kiritish
- **Savollar soni** - Testdagi savollar sonini belgilash
- **Savol va javoblar** - Har bir savol va javob variantlarini kiritish

### 🎯 Yangi funksiyalar
- **Test turi tanlash** - Oddiy test, DTM, Milliy sertifikat, Ochiq test
- **Test toifasi** - Ommaviy va shaxsiy testlar
- **Savollar qo'shish** - Testga savol va javoblar qo'shish
- **Avtomatik test yaratish** - Barcha savollar kiritilgandan keyin

### �� Texnik o'zgarishlar
- **TestCreationService** qayta yozildi
- **Message handlers** yangilandi
- **Multi-step conversation** soddalashtirildi
- **Database modellar** to'g'rilandi

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Test yaratish jarayoni ✅
- Database to'g'ri ishlayapti ✅
- Telegram API bilan bog'lanish ✅

---

## [v0.9.1] - 2025-08-20

### ✅ Test yaratish jarayoni soddalashtirildi
- **Soddalashtirilgan jarayon** - Faqat kerakli sozlamalar so'raladi
- **Test nomi** - Test nomini kiritish
- **Savollar soni** - Testdagi savollar sonini belgilash
- **Savol va javoblar** - Har bir savol va javob variantlarini kiritish

### 🎯 Yangi funksiyalar
- **Test turi tanlash** - Oddiy test, DTM, Milliy sertifikat, Ochiq test
- **Test toifasi** - Ommaviy va shaxsiy testlar
- **Savollar qo'shish** - Testga savol va javoblar qo'shish
- **Avtomatik test yaratish** - Barcha savollar kiritilgandan keyin

### 🔧 Texnik o'zgarishlar
- **TestCreationService** qayta yozildi
- **Message handlers** yangilandi
- **Multi-step conversation** soddalashtirildi
- **Database modellar** to'g'rilandi

### 📊 Holat
- Bot to'liq ishlayapti ✅
- Test yaratish jarayoni ✅
- Database to'g'ri ishlayapti ✅
- Telegram API bilan bog'lanish ✅

---

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

## [v0.8.1] - 2025-08-20

### ✅ Arxitektura qayta tuzildi
- **Bot modullarga ajratildi** - Katta fayl kichik modullarga bo'lindi
- **Keyboard Factory** - Barcha keyboardlar alohida modulda
- **Handler modullari** - Command, Message, Callback handerlari alohida
- **Kod tuzilishi** - Toza va tushunarli arxitektura

### 📁 Yangi fayl strukturasi
```
src/bot/
├── keyboards/
│   ├── __init__.py
│   └── keyboard_factory.py
├── handlers/
│   ├── __init__.py
│   ├── command_handlers.py
│   ├── message_handlers.py
│   └── callback_handlers.py
└── bot.py (asosiy fayl)
```

### 🔧 Texnik o'zgarishlar
- Bot fayli 631 qatordan 91 qatorga qisqartirildi
- Har bir handler alohida faylda
- Keyboard yaratish factory pattern bilan
- Import tizimi optimallashtirildi

### 🎯 Afzalliklari
- **Oson saqlash** - Har bir modul alohida
- **Qayta ishlatish** - Modullar boshqa joyda ishlatilishi mumkin
- **Testlash** - Har bir modul alohida testlash mumkin
- **Kengaytirish** - Yangi funksiyalar oson qo'shiladi

---

## [v0.8.0] - 2025-08-20

### ✅ Test yaratish tizimi qo'shildi
- **Test turi tanlash** - Oddiy test, DTM, Milliy sertifikat, Ochiq test
- **Test toifasi** - Ommaviy va shaxsiy testlar
- **Fan tanlash** - Test uchun fan belgilash
- **Test ma'lumotlari** - Nomi, tavsif, vaqt chegarasi

### 🎯 Yangi funksiyalar
- **Reply Keyboard Markup** - Asosiy menyu tugmalari
- **Inline Keyboard** - Test variantlari uchun
- **Multi-step conversation** - Test yaratish jarayoni
- **Test kod yaratish** - Shaxsiy testlar uchun

### 📊 Holat
- Bot ishga tushdi ✅
- Database ishlayapti ✅
- Test yaratish jarayoni ✅
- Telegram API bilan bog'lanish ✅

---

## [v0.7.0] - 2025-08-20

### ✅ Asosiy tuzilma yaratildi
- **Database modellar** - User, Test, Question, Answer, TestResult
- **Service layer** - UserService, TestService, TestCreationService
- **Bot framework** - python-telegram-bot
- **Database** - SQLite with SQLAlchemy

### 🎯 Asosiy funksiyalar
- **Foydalanuvchi ro'yxatdan o'tish** - /register
- **Asosiy menyu** - O'qituvchi/O'quvchi tanlash
- **Database operatsiyalari** - CRUD operatsiyalari
- **Logging** - Loguru bilan

### �� Holat
- Bot ishga tushdi ✅
- Database ishlayapti ✅
- Asosiy funksiyalar ✅
- Telegram API bilan bog'lanish ✅

---

## [v0.6.0] - 2025-08-20

### ✅ Loyiha asoslari yaratildi
- **Loyiha strukturasi** - Modullarga ajratilgan
- **Dependencies** - requirements.txt
- **Environment** - .env.example
- **Git repository** - Version control

### 🎯 Asosiy komponentlar
- **src/** - Asosiy kod papkasi
- **models/** - Database modellar
- **services/** - Business logic
- **bot/** - Telegram bot
- **database/** - Database connection

### 📊 Holat
- Loyiha strukturasi ✅
- Dependencies ✅
- Git repository ✅
- README va dokumentatsiya ✅
