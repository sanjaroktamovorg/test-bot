import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from src.database import Database
from src.models import User, UserRole
from src.models.test_types import TestType, TestCategory
from src.services.user_service import UserService
from src.services.test_creation_service import TestCreationService
from src.services.test_taking_service import TestTakingService
from src.services.test_service import TestService

load_dotenv()

class TestBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN topilmadi!")
        
        self.db = Database()
        self.user_service = UserService(self.db)
        self.test_service = TestService(self.db)
        self.test_creation_service = TestCreationService(self.db)
        self.test_taking_service = TestTakingService(self.db)
        
        # Bot yaratish
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Bot handerlarni sozlash"""
        # Asosiy komandalar
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("register", self.register_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        
        # O'qituvchi komandalari
        self.application.add_handler(CommandHandler("create_test", self.create_test_command))
        self.application.add_handler(CommandHandler("my_tests", self.my_tests_command))
        self.application.add_handler(CommandHandler("results", self.results_command))
        
        # O'quvchi komandalari
        self.application.add_handler(CommandHandler("available_tests", self.available_tests_command))
        self.application.add_handler(CommandHandler("my_results", self.my_results_command))
        
        # Callback handerlari
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Xabar handerlari
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def _get_main_keyboard(self, user_role: UserRole):
        """Asosiy reply keyboard"""
        if user_role == UserRole.TEACHER:
            keyboard = [
                [KeyboardButton("📝 Test yaratish"), KeyboardButton("📋 Mening testlarim")],
                [KeyboardButton("📊 Natijalar"), KeyboardButton("👥 O'quvchilar")],
                [KeyboardButton("❓ Yordam"), KeyboardButton("⚙️ Sozlamalar")]
            ]
        else:  # STUDENT
            keyboard = [
                [KeyboardButton("📝 Mavjud testlar"), KeyboardButton("📊 Mening natijalarim")],
                [KeyboardButton("🏆 Reyting"), KeyboardButton("📚 O'quv materiallari")],
                [KeyboardButton("❓ Yordam"), KeyboardButton("⚙️ Sozlamalar")]
            ]
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    def _get_test_type_keyboard(self):
        """Test turi tanlash uchun reply keyboard"""
        keyboard = [
            [KeyboardButton("📝 Oddiy test")],
            [KeyboardButton("🏛️ DTM test")],
            [KeyboardButton("🏆 Milliy sertifikat test")],
            [KeyboardButton("📖 Ochiq (variantsiz) test")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    def _get_test_category_keyboard(self):
        """Test toifasi tanlash uchun reply keyboard"""
        keyboard = [
            [KeyboardButton("📐 Matematika"), KeyboardButton("⚡ Fizika")],
            [KeyboardButton("🧪 Kimyo"), KeyboardButton("🌿 Biologiya")],
            [KeyboardButton("📚 Tarix"), KeyboardButton("🌍 Geografiya")],
            [KeyboardButton("📖 Adabiyot"), KeyboardButton("🗣️ Til")],
            [KeyboardButton("💻 Informatika"), KeyboardButton("📋 Boshqa")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    def _get_test_keyboard(self, tests):
        """Testlar uchun inline keyboard"""
        keyboard = []
        for test in tests:
            keyboard.append([InlineKeyboardButton(
                f"📝 {test.title}", 
                callback_data=f"take_test_{test.id}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    def _get_results_keyboard(self, results):
        """Natijalar uchun inline keyboard"""
        keyboard = []
        for result in results:
            keyboard.append([InlineKeyboardButton(
                f"📊 {result.test.title} - {result.percentage:.1f}%", 
                callback_data=f"view_result_{result.id}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komandasi"""
        user = update.effective_user
        
        # Foydalanuvchini tekshirish
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            # Ro'yxatdan o'tmagan foydalanuvchi
            welcome_text = f"""
🎓 Test Bot ga xush kelibsiz, {user.first_name}!

Bu bot orqali:
📝 O'qituvchilar testlar tuzishi
📊 O'quvchilar testlarni ishlashi
📈 Natijalarni ko'rish mumkin

Boshlash uchun ro'yxatdan o'ting.
            """
            
            keyboard = [
                [InlineKeyboardButton("📝 Ro'yxatdan o'tish", callback_data="register")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        else:
            # Ro'yxatdan o'tgan foydalanuvchi
            await self.menu_command(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yordam komandasi"""
        help_text = """
🤖 Test Bot - Yordam

📋 Mavjud komandalar:

👤 Umumiy:
/start - Botni ishga tushirish
/help - Yordam
/register - Ro'yxatdan o'tish
/menu - Asosiy menyu

👨‍🏫 O'qituvchilar uchun:
📝 Test yaratish - Yangi test yaratish
📋 Mening testlarim - Mening testlarim
📊 Natijalar - Test natijalari
👥 O'quvchilar - O'quvchilar ro'yxati

👨‍🎓 O'quvchilar uchun:
📝 Mavjud testlar - Mavjud testlar
📊 Mening natijalarim - Mening natijalarim
🏆 Reyting - O'quvchilar reytingi
        """
        await update.message.reply_text(help_text)
    
    async def register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ro'yxatdan o'tish"""
        user = update.effective_user
        
        # Foydalanuvchini database ga saqlash
        db_user = await self.user_service.register_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if db_user:
            keyboard = [
                [InlineKeyboardButton("👨‍🏫 O'qituvchi", callback_data="role_teacher")],
                [InlineKeyboardButton("👨‍�� O'quvchi", callback_data="role_student")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ Ro'yxatdan o'tdingiz! Iltimos, rolingizni tanlang:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("❌ Ro'yxatdan o'tishda xatolik yuz berdi!")
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Asosiy menyu"""
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text("❌ Avval ro'yxatdan o'ting! /register")
            return
        
        role_text = "👨‍🏫 O'qituvchi" if db_user.role == UserRole.TEACHER else "👨‍🎓 O'quvchi"
        
        menu_text = f"""
🏠 Asosiy menyu

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: {role_text}

Quyidagi tugmalardan birini tanlang:
        """
        
        reply_markup = self._get_main_keyboard(db_user.role)
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    
    async def create_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test yaratish komandasi"""
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        await update.message.reply_text(
            "📝 Test yaratish uchun avval test turini tanlang:",
            reply_markup=self._get_test_type_keyboard()
        )
        context.user_data['creating_test'] = True
        context.user_data['test_creation_step'] = 'select_type'
        context.user_data['test_data'] = {}
    
    async def available_tests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mavjud testlar"""
        tests = await self.test_service.get_available_tests()
        
        if not tests:
            await update.message.reply_text("📝 Hozirda mavjud testlar yo'q.")
            return
        
        text = "📝 Mavjud testlar:\n\n"
        for test in tests:
            text += f"📋 {test.title}\n"
            text += f"👨‍🏫 {test.teacher.first_name}\n"
            text += f"⏱️ {test.time_limit} daqiqa\n"
            text += f"📊 {test.passing_score}% o'tish balli\n\n"
        
        reply_markup = self._get_test_keyboard(tests)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def my_tests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening testlarim"""
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        tests = await self.test_service.get_teacher_tests(db_user.id)
        
        if not tests:
            await update.message.reply_text("📝 Sizda hali testlar yo'q. Yangi test yarating!")
            return
        
        text = "📋 Mening testlarim:\n\n"
        for test in tests:
            text += f"📝 {test.title}\n"
            text += f"📊 Holat: {test.status.value}\n"
            text += f"⏱️ {test.time_limit} daqiqa\n\n"
        
        reply_markup = self._get_test_keyboard(tests)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test natijalari"""
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        await update.message.reply_text("📊 Test natijalari funksiyasi ishlab chiqilmoqda...")
    
    async def my_results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening natijalarim"""
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        results = await self.test_service.get_student_results(db_user.id)
        
        if not results:
            await update.message.reply_text("📊 Sizda hali test natijalari yo'q.")
            return
        
        text = "📊 Mening natijalarim:\n\n"
        for result in results:
            text += f"📝 {result.test.title}\n"
            text += f"📊 Ball: {result.score}/{result.max_score}\n"
            text += f"📈 Foiz: {result.percentage:.1f}%\n\n"
        
        reply_markup = self._get_results_keyboard(results)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tugma bosish handerlari"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "register":
            await self.register_command(update, context)
        elif query.data.startswith("role_"):
            role = query.data.split("_")[1]
            await self._set_user_role(query, role)
        elif query.data.startswith("take_test_"):
            test_id = int(query.data.split("_")[2])
            await self._start_test(query, test_id)
        elif query.data == "back_to_menu":
            await self._back_to_menu(query, context)
        elif query.data.startswith("view_result_"):
            result_id = int(query.data.split("_")[2])
            await self._view_result(query, result_id)
    
    async def _set_user_role(self, query, role):
        """Foydalanuvchi roli o'rnatish"""
        user = query.from_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if db_user:
            user_role = UserRole.TEACHER if role == "teacher" else UserRole.STUDENT
            await self.user_service.update_user_role(db_user.id, user_role)
            
            role_text = "👨‍🏫 O'qituvchi" if role == "teacher" else "👨‍🎓 O'quvchi"
            await query.edit_message_text(f"✅ Rolingiz o'rnatildi: {role_text}")
            
            # Asosiy menyuni ko'rsatish
            keyboard = self._get_main_keyboard(user_role)
            await query.message.reply_text("🏠 Asosiy menyu:", reply_markup=keyboard)
    
    async def _start_test(self, query, test_id):
        """Testni boshlash"""
        user = query.from_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.STUDENT:
            await query.edit_message_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Testni boshlash logikasi
        await query.edit_message_text(f"📝 Test boshlanmoqda... Test ID: {test_id}")
    
    async def _back_to_menu(self, query, context):
        """Menyuga qaytish"""
        await self.menu_command(context, context)
    
    async def _view_result(self, query, result_id):
    
    async def _handle_test_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test yaratish jarayonini boshqarish"""
        step = context.user_data.get('test_creation_step', 'select_type')
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if step == 'select_type':
            await self._handle_test_type_selection(update, context, text)
        elif step == 'select_category':
            await self._handle_test_category_selection(update, context, text)
        elif step == 'enter_details':
            await self._handle_test_details_entry(update, context, text, db_user)
        
    async def _handle_test_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test turi tanlash"""
        test_type_map = {
            '📝 Oddiy test': TestType.SIMPLE,
            '🏛️ DTM test': TestType.DTM,
            '🏆 Milliy sertifikat test': TestType.NATIONAL_CERT,
            '📖 Ochiq (variantsiz) test': TestType.OPEN
        }
        
        if text == '🔙 Orqaga':
            await self.menu_command(update, context)
            context.user_data['creating_test'] = False
            return
        
        if text in test_type_map:
            test_type = test_type_map[text]
            context.user_data['test_data']['test_type'] = test_type.value
            
            if test_type == TestType.SIMPLE:
                # Oddiy test uchun toifa tanlash
                await update.message.reply_text(
                    "📝 Oddiy test yaratish uchun toifani tanlang:",
                    reply_markup=self._get_test_category_keyboard()
                )
                context.user_data['test_creation_step'] = 'select_category'
            else:
                # Boshqa test turlari uchun xabar
                await update.message.reply_text(
                    f"🚧 {text} yaratish funksiyasi ishlab chiqilmoqda!\n\n"
                    f"Iltimos, oddiy test yaratishni sinab ko'ring yoki keyinroq qaytib keling.",
                    reply_markup=self._get_test_type_keyboard()
                )
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=self._get_test_type_keyboard()
            )
    
    async def _handle_test_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test toifasi tanlash"""
        category_map = {
            '📐 Matematika': TestCategory.MATHEMATICS,
            '⚡ Fizika': TestCategory.PHYSICS,
            '🧪 Kimyo': TestCategory.CHEMISTRY,
            '🌿 Biologiya': TestCategory.BIOLOGY,
            '📚 Tarix': TestCategory.HISTORY,
            '🌍 Geografiya': TestCategory.GEOGRAPHY,
            '📖 Adabiyot': TestCategory.LITERATURE,
            '🗣️ Til': TestCategory.LANGUAGE,
            '💻 Informatika': TestCategory.COMPUTER_SCIENCE,
            '📋 Boshqa': TestCategory.OTHER
        }
        
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Test yaratish uchun avval test turini tanlang:",
                reply_markup=self._get_test_type_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_type'
            return
        
        if text in category_map:
            category = category_map[text]
            context.user_data['test_data']['category'] = category.value
            
            await update.message.reply_text(
                "📝 Endi test ma'lumotlarini kiriting:\n\n"
                "Quyidagi formatda yuboring:\n\n"
                "Test nomi: [Test nomi]\n"
                "Tavsif: [Test tavsifi]\n"
                "Vaqt chegarasi: [daqiqalarda]\n"
                "O'tish balli: [foizda]\n\n"
                "Misol:\n"
                "Test nomi: Algebra testi\n"
                "Tavsif: Kvadrat tenglamalar\n"
                "Vaqt chegarasi: 30\n"
                "O'tish balli: 70",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
            )
            context.user_data['test_creation_step'] = 'enter_details'
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=self._get_test_category_keyboard()
            )
    
    async def _handle_test_details_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, db_user):
        """Test ma'lumotlarini kiritish"""
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Oddiy test yaratish uchun toifani tanlang:",
                reply_markup=self._get_test_category_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_category'
            return
        
        try:
            # Test ma'lumotlarini parse qilish
            test_data = context.user_data['test_data']
            parsed_data = await self.test_creation_service.parse_test_data(text)
            
            # Barcha ma'lumotlarni birlashtirish
            final_data = {**test_data, **parsed_data}
            
            # Test yaratish
            test = await self.test_creation_service.create_test_from_data(final_data, db_user.id)
            
            await update.message.reply_text(
                f"✅ Test muvaffaqiyatli yaratildi!\n\n"
                f"📝 Nomi: {test.title}\n"
                f"📊 Turi: {test.test_type}\n"
                f"📂 Toifasi: {test.category}\n"
                f"⏱️ Vaqt: {test.time_limit} daqiqa\n"
                f"📈 O'tish balli: {test.passing_score}%\n\n"
                f"Test ID: {test.id}",
                reply_markup=self._get_main_keyboard(db_user.role)
            )
            
            context.user_data['creating_test'] = False
            context.user_data['test_creation_step'] = None
            context.user_data['test_data'] = {}
            
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")
            context.user_data['creating_test'] = False
        """Natijani ko'rish"""
    
    async def _handle_test_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test yaratish jarayonini boshqarish"""
        step = context.user_data.get('test_creation_step', 'select_type')
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if step == 'select_type':
            await self._handle_test_type_selection(update, context, text)
        elif step == 'select_category':
            await self._handle_test_category_selection(update, context, text)
        elif step == 'enter_details':
            await self._handle_test_details_entry(update, context, text, db_user)
        
    async def _handle_test_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test turi tanlash"""
        test_type_map = {
            '📝 Oddiy test': TestType.SIMPLE,
            '🏛️ DTM test': TestType.DTM,
            '🏆 Milliy sertifikat test': TestType.NATIONAL_CERT,
            '📖 Ochiq (variantsiz) test': TestType.OPEN
        }
        
        if text == '🔙 Orqaga':
            await self.menu_command(update, context)
            context.user_data['creating_test'] = False
            return
        
        if text in test_type_map:
            test_type = test_type_map[text]
            context.user_data['test_data']['test_type'] = test_type.value
            
            if test_type == TestType.SIMPLE:
                # Oddiy test uchun toifa tanlash
                await update.message.reply_text(
                    "📝 Oddiy test yaratish uchun toifani tanlang:",
                    reply_markup=self._get_test_category_keyboard()
                )
                context.user_data['test_creation_step'] = 'select_category'
            else:
                # Boshqa test turlari uchun xabar
                await update.message.reply_text(
                    f"🚧 {text} yaratish funksiyasi ishlab chiqilmoqda!\n\n"
                    f"Iltimos, oddiy test yaratishni sinab ko'ring yoki keyinroq qaytib keling.",
                    reply_markup=self._get_test_type_keyboard()
                )
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=self._get_test_type_keyboard()
            )
    
    async def _handle_test_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test toifasi tanlash"""
        category_map = {
            '📐 Matematika': TestCategory.MATHEMATICS,
            '⚡ Fizika': TestCategory.PHYSICS,
            '🧪 Kimyo': TestCategory.CHEMISTRY,
            '🌿 Biologiya': TestCategory.BIOLOGY,
            '📚 Tarix': TestCategory.HISTORY,
            '🌍 Geografiya': TestCategory.GEOGRAPHY,
            '📖 Adabiyot': TestCategory.LITERATURE,
            '🗣️ Til': TestCategory.LANGUAGE,
            '💻 Informatika': TestCategory.COMPUTER_SCIENCE,
            '📋 Boshqa': TestCategory.OTHER
        }
        
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Test yaratish uchun avval test turini tanlang:",
                reply_markup=self._get_test_type_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_type'
            return
        
        if text in category_map:
            category = category_map[text]
            context.user_data['test_data']['category'] = category.value
            
            await update.message.reply_text(
                "📝 Endi test ma'lumotlarini kiriting:\n\n"
                "Quyidagi formatda yuboring:\n\n"
                "Test nomi: [Test nomi]\n"
                "Tavsif: [Test tavsifi]\n"
                "Vaqt chegarasi: [daqiqalarda]\n"
                "O'tish balli: [foizda]\n\n"
                "Misol:\n"
                "Test nomi: Algebra testi\n"
                "Tavsif: Kvadrat tenglamalar\n"
                "Vaqt chegarasi: 30\n"
                "O'tish balli: 70",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
            )
            context.user_data['test_creation_step'] = 'enter_details'
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=self._get_test_category_keyboard()
            )
    
    async def _handle_test_details_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, db_user):
        """Test ma'lumotlarini kiritish"""
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Oddiy test yaratish uchun toifani tanlang:",
                reply_markup=self._get_test_category_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_category'
            return
        
        try:
            # Test ma'lumotlarini parse qilish
            test_data = context.user_data['test_data']
            parsed_data = await self.test_creation_service.parse_test_data(text)
            
            # Barcha ma'lumotlarni birlashtirish
            final_data = {**test_data, **parsed_data}
            
            # Test yaratish
            test = await self.test_creation_service.create_test_from_data(final_data, db_user.id)
            
            await update.message.reply_text(
                f"✅ Test muvaffaqiyatli yaratildi!\n\n"
                f"📝 Nomi: {test.title}\n"
                f"📊 Turi: {test.test_type}\n"
                f"📂 Toifasi: {test.category}\n"
                f"⏱️ Vaqt: {test.time_limit} daqiqa\n"
                f"📈 O'tish balli: {test.passing_score}%\n\n"
                f"Test ID: {test.id}",
                reply_markup=self._get_main_keyboard(db_user.role)
            )
            
            context.user_data['creating_test'] = False
            context.user_data['test_creation_step'] = None
            context.user_data['test_data'] = {}
            
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")
            context.user_data['creating_test'] = False
        await query.edit_message_text(f"📊 Natija ko'rish... Result ID: {result_id}")
    
    async def _handle_test_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test yaratish jarayonini boshqarish"""
        step = context.user_data.get('test_creation_step', 'select_type')
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if step == 'select_type':
            await self._handle_test_type_selection(update, context, text)
        elif step == 'select_category':
            await self._handle_test_category_selection(update, context, text)
        elif step == 'enter_details':
            await self._handle_test_details_entry(update, context, text, db_user)
        
    async def _handle_test_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test turi tanlash"""
        test_type_map = {
            '📝 Oddiy test': TestType.SIMPLE,
            '🏛️ DTM test': TestType.DTM,
            '🏆 Milliy sertifikat test': TestType.NATIONAL_CERT,
            '📖 Ochiq (variantsiz) test': TestType.OPEN
        }
        
        if text == '🔙 Orqaga':
            await self.menu_command(update, context)
            context.user_data['creating_test'] = False
            return
        
        if text in test_type_map:
            test_type = test_type_map[text]
            context.user_data['test_data']['test_type'] = test_type.value
            
            if test_type == TestType.SIMPLE:
                # Oddiy test uchun toifa tanlash
                await update.message.reply_text(
                    "📝 Oddiy test yaratish uchun toifani tanlang:",
                    reply_markup=self._get_test_category_keyboard()
                )
                context.user_data['test_creation_step'] = 'select_category'
            else:
                # Boshqa test turlari uchun xabar
                await update.message.reply_text(
                    f"🚧 {text} yaratish funksiyasi ishlab chiqilmoqda!\n\n"
                    f"Iltimos, oddiy test yaratishni sinab ko'ring yoki keyinroq qaytib keling.",
                    reply_markup=self._get_test_type_keyboard()
                )
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=self._get_test_type_keyboard()
            )
    
    async def _handle_test_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test toifasi tanlash"""
        category_map = {
            '📐 Matematika': TestCategory.MATHEMATICS,
            '⚡ Fizika': TestCategory.PHYSICS,
            '🧪 Kimyo': TestCategory.CHEMISTRY,
            '🌿 Biologiya': TestCategory.BIOLOGY,
            '📚 Tarix': TestCategory.HISTORY,
            '🌍 Geografiya': TestCategory.GEOGRAPHY,
            '📖 Adabiyot': TestCategory.LITERATURE,
            '🗣️ Til': TestCategory.LANGUAGE,
            '💻 Informatika': TestCategory.COMPUTER_SCIENCE,
            '📋 Boshqa': TestCategory.OTHER
        }
        
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Test yaratish uchun avval test turini tanlang:",
                reply_markup=self._get_test_type_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_type'
            return
        
        if text in category_map:
            category = category_map[text]
            context.user_data['test_data']['category'] = category.value
            
            await update.message.reply_text(
                "📝 Endi test ma'lumotlarini kiriting:\n\n"
                "Quyidagi formatda yuboring:\n\n"
                "Test nomi: [Test nomi]\n"
                "Tavsif: [Test tavsifi]\n"
                "Vaqt chegarasi: [daqiqalarda]\n"
                "O'tish balli: [foizda]\n\n"
                "Misol:\n"
                "Test nomi: Algebra testi\n"
                "Tavsif: Kvadrat tenglamalar\n"
                "Vaqt chegarasi: 30\n"
                "O'tish balli: 70",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
            )
            context.user_data['test_creation_step'] = 'enter_details'
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=self._get_test_category_keyboard()
            )
    
    async def _handle_test_details_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, db_user):
        """Test ma'lumotlarini kiritish"""
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Oddiy test yaratish uchun toifani tanlang:",
                reply_markup=self._get_test_category_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_category'
            return
        
        try:
            # Test ma'lumotlarini parse qilish
            test_data = context.user_data['test_data']
            parsed_data = await self.test_creation_service.parse_test_data(text)
            
            # Barcha ma'lumotlarni birlashtirish
            final_data = {**test_data, **parsed_data}
            
            # Test yaratish
            test = await self.test_creation_service.create_test_from_data(final_data, db_user.id)
            
            await update.message.reply_text(
                f"✅ Test muvaffaqiyatli yaratildi!\n\n"
                f"📝 Nomi: {test.title}\n"
                f"📊 Turi: {test.test_type}\n"
                f"📂 Toifasi: {test.category}\n"
                f"⏱️ Vaqt: {test.time_limit} daqiqa\n"
                f"📈 O'tish balli: {test.passing_score}%\n\n"
                f"Test ID: {test.id}",
                reply_markup=self._get_main_keyboard(db_user.role)
            )
            
            context.user_data['creating_test'] = False
            context.user_data['test_creation_step'] = None
            context.user_data['test_data'] = {}
            
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")
            context.user_data['creating_test'] = False
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xabar handerlari"""
        user = update.effective_user
        text = update.message.text
        
        # Reply keyboard tugmalarini tekshirish
        if text == "📝 Test yaratish":
            await self.create_test_command(update, context)
        elif text == "📋 Mening testlarim":
            await self.my_tests_command(update, context)
        elif text == "📊 Natijalar":
            await self.results_command(update, context)
        elif text == "👥 O'quvchilar":
            await update.message.reply_text("👥 O'quvchilar ro'yxati funksiyasi ishlab chiqilmoqda...")
        elif text == "📝 Mavjud testlar":
            await self.available_tests_command(update, context)
        elif text == "📊 Mening natijalarim":
            await self.my_results_command(update, context)
        elif text == "🏆 Reyting":
            await update.message.reply_text("🏆 O'quvchilar reytingi funksiyasi ishlab chiqilmoqda...")
        elif text == "📚 O'quv materiallari":
            await update.message.reply_text("📚 O'quv materiallari funksiyasi ishlab chiqilmoqda...")
        elif text == "❓ Yordam":
            await self.help_command(update, context)
        elif text == "⚙️ Sozlamalar":
            await update.message.reply_text("⚙️ Sozlamalar funksiyasi ishlab chiqilmoqda...")
        elif context.user_data.get('creating_test'):
            await self._handle_test_creation(update, context, text)
                    return
                
                # Test yaratish
                test = await self.test_creation_service.create_test_from_text(text, db_user.id)
                
                await update.message.reply_text(
                    f"✅ Test muvaffaqiyatli yaratildi!\n\n"
                    f"📝 Nomi: {test.title}\n"
                    f"📊 Holat: {test.status.value}\n"
                    f"⏱️ Vaqt: {test.time_limit} daqiqa\n"
                    f"📈 O'tish balli: {test.passing_score}%\n\n"
                    f"Test ID: {test.id}"
                )
                
                context.user_data['creating_test'] = False
                context.user_data['current_test_id'] = test.id
                
            except Exception as e:
                await update.message.reply_text(f"❌ Xatolik: {str(e)}")
                context.user_data['creating_test'] = False
        else:
            await update.message.reply_text("❓ Tushunarsiz xabar. /help komandasi bilan yordam oling.")
    
    def run(self):
        """Botni ishga tushirish"""
        logging.info("Test Bot ishga tushirilmoqda...")
        self.application.run_polling()
    
    def run_webhook(self, webhook_url: str):
        """Webhook rejimida ishga tushirish"""
        logging.info(f"Test Bot webhook rejimida ishga tushirilmoqda: {webhook_url}")
        self.application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            webhook_url=webhook_url
        )
