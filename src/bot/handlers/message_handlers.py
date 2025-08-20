from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from src.models import UserRole
from src.bot.keyboards import KeyboardFactory

class MessageHandlers:
    """Xabar handerlari"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
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
            await self.bot.command_handlers.help_command(update, context)
        elif text == "⚙️ Sozlamalar":
            await update.message.reply_text("⚙️ Sozlamalar funksiyasi ishlab chiqilmoqda...")
        elif context.user_data.get('creating_test'):
            # Test yaratish logikasi
            await self._handle_test_creation(update, context, text)
        else:
            await update.message.reply_text("❓ Tushunarsiz xabar. /help komandasi bilan yordam oling.")
    
    async def create_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test yaratish komandasi"""
        user = update.effective_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        await update.message.reply_text(
            "📝 Test yaratish uchun avval test turini tanlang:",
            reply_markup=KeyboardFactory.get_test_type_keyboard()
        )
        context.user_data['creating_test'] = True
        context.user_data['test_creation_step'] = 'select_type'
        context.user_data['test_data'] = {}
    
    async def available_tests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mavjud testlar"""
        tests = await self.bot.test_service.get_available_tests()
        
        if not tests:
            await update.message.reply_text("📝 Hozirda mavjud testlar yo'q.")
            return
        
        text = "📝 Mavjud testlar:\n\n"
        for test in tests:
            text += f"📋 {test.title}\n"
            text += f"👨‍🏫 {test.teacher.first_name}\n"
            text += f"⏱️ {test.time_limit} daqiqa\n"
            text += f"📊 {test.passing_score}% o'tish balli\n\n"
        
        reply_markup = KeyboardFactory.get_test_keyboard(tests)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def my_tests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening testlarim"""
        user = update.effective_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        tests = await self.bot.test_service.get_teacher_tests(db_user.id)
        
        if not tests:
            await update.message.reply_text("📝 Sizda hali testlar yo'q. Yangi test yarating!")
            return
        
        text = "📋 Mening testlarim:\n\n"
        for test in tests:
            text += f"📝 {test.title}\n"
            text += f"📊 Holat: {test.status.value}\n"
            text += f"⏱️ {test.time_limit} daqiqa\n\n"
        
        reply_markup = KeyboardFactory.get_test_keyboard(tests)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test natijalari"""
        user = update.effective_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        await update.message.reply_text("📊 Test natijalari funksiyasi ishlab chiqilmoqda...")
    
    async def my_results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening natijalarim"""
        user = update.effective_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        results = await self.bot.test_service.get_student_results(db_user.id)
        
        if not results:
            await update.message.reply_text("📊 Sizda hali test natijalari yo'q.")
            return
        
        text = "📊 Mening natijalarim:\n\n"
        for result in results:
            text += f"📝 {result.test.title}\n"
            text += f"📊 Ball: {result.score}/{result.max_score}\n"
            text += f"📈 Foiz: {result.percentage:.1f}%\n\n"
        
        reply_markup = KeyboardFactory.get_results_keyboard(results)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def _handle_test_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test yaratish jarayonini boshqarish"""
        step = context.user_data.get('test_creation_step', 'select_type')
        user = update.effective_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if step == 'select_type':
            await self._handle_test_type_selection(update, context, text)
        elif step == 'select_category':
            await self._handle_test_category_selection(update, context, text)
        elif step == 'select_subject':
            await self._handle_test_subject_selection(update, context, text)
        elif step == 'enter_details':
            await self._handle_test_details_entry(update, context, text, db_user)
    
    async def _handle_test_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test turi tanlash"""
        from src.models.test_types import TestType
        
        test_type_map = {
            '📝 Oddiy test': TestType.SIMPLE,
            '🏛️ DTM test': TestType.DTM,
            '🏆 Milliy sertifikat test': TestType.NATIONAL_CERT,
            '📖 Ochiq (variantsiz) test': TestType.OPEN
        }
        
        if text == '🔙 Orqaga':
            await self.bot.command_handlers.menu_command(update, context)
            context.user_data['creating_test'] = False
            return
        
        if text in test_type_map:
            test_type = test_type_map[text]
            context.user_data['test_data']['test_type'] = test_type.value
            
            if test_type == TestType.SIMPLE:
                # Oddiy test uchun toifa tanlash
                await update.message.reply_text(
                    "📝 Oddiy test yaratish uchun toifani tanlang:",
                    reply_markup=KeyboardFactory.get_test_category_keyboard()
                )
                context.user_data['test_creation_step'] = 'select_category'
            else:
                # Boshqa test turlari uchun xabar
                await update.message.reply_text(
                    f"🚧 {text} yaratish funksiyasi ishlab chiqilmoqda!\n\n"
                    f"Iltimos, oddiy test yaratishni sinab ko'ring yoki keyinroq qaytib keling.",
                    reply_markup=KeyboardFactory.get_test_type_keyboard()
                )
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=KeyboardFactory.get_test_type_keyboard()
            )
    
    async def _handle_test_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test toifasi tanlash"""
        from src.models.test_types import TestCategory
        
        category_map = {
            '🌍 Ommaviy test': TestCategory.PUBLIC,
            '🔒 Shaxsiy test': TestCategory.PRIVATE
        }
        
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Test yaratish uchun avval test turini tanlang:",
                reply_markup=KeyboardFactory.get_test_type_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_type'
            return
        
        if text in category_map:
            category = category_map[text]
            context.user_data['test_data']['category'] = category.value
            
            await update.message.reply_text(
                "📝 Endi test fanini tanlang:",
                reply_markup=KeyboardFactory.get_test_subject_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_subject'
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=KeyboardFactory.get_test_category_keyboard()
            )
    
    async def _handle_test_subject_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test fani tanlash"""
        from src.models.test_types import TestSubject
        
        subject_map = {
            '📐 Matematika': TestSubject.MATHEMATICS,
            '⚡ Fizika': TestSubject.PHYSICS,
            '🧪 Kimyo': TestSubject.CHEMISTRY,
            '🌿 Biologiya': TestSubject.BIOLOGY,
            '📚 Tarix': TestSubject.HISTORY,
            '🌍 Geografiya': TestSubject.GEOGRAPHY,
            '📖 Adabiyot': TestSubject.LITERATURE,
            '🗣️ Til': TestSubject.LANGUAGE,
            '💻 Informatika': TestSubject.COMPUTER_SCIENCE,
            '📋 Boshqa': TestSubject.OTHER
        }
        
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Test yaratish uchun toifani tanlang:",
                reply_markup=KeyboardFactory.get_test_category_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_category'
            return
        
        if text in subject_map:
            subject = subject_map[text]
            context.user_data['test_data']['subject'] = subject.value
            
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
                reply_markup=KeyboardFactory.get_back_keyboard()
            )
            context.user_data['test_creation_step'] = 'enter_details'
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=KeyboardFactory.get_test_subject_keyboard()
            )
    
    async def _handle_test_details_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, db_user):
        """Test ma'lumotlarini kiritish"""
        from src.models.test_types import TestCategory
        
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Test yaratish uchun fanini tanlang:",
                reply_markup=KeyboardFactory.get_test_subject_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_subject'
            return
        
        try:
            # Test ma'lumotlarini parse qilish
            test_data = context.user_data['test_data']
            parsed_data = await self.bot.test_creation_service.parse_test_data(text)
            
            # Barcha ma'lumotlarni birlashtirish
            final_data = {**test_data, **parsed_data}
            
            # Test yaratish
            test = await self.bot.test_creation_service.create_test_from_data(final_data, db_user.id)
            
            # Natija xabarini tayyorlash
            result_text = f"✅ Test muvaffaqiyatli yaratildi!\n\n"
            result_text += f"📝 Nomi: {test.title}\n"
            result_text += f"📊 Turi: {test.test_type}\n"
            result_text += f"📂 Toifasi: {test.category}\n"
            result_text += f"📚 Fani: {test.subject}\n"
            result_text += f"⏱️ Vaqt: {test.time_limit} daqiqa\n"
            result_text += f"📈 O'tish balli: {test.passing_score}%\n\n"
            result_text += f"Test ID: {test.id}\n"
            
            # Shaxsiy test uchun maxsus kod
            if test.category == TestCategory.PRIVATE.value:
                result_text += f"🔑 Maxsus kod: {test.test_code}\n"
                result_text += f"🔗 Havola: https://t.me/your_bot?start=test_{test.test_code}"
            
            await update.message.reply_text(
                result_text,
                reply_markup=KeyboardFactory.get_main_keyboard(db_user.role)
            )
            
            context.user_data['creating_test'] = False
            context.user_data['test_creation_step'] = None
            context.user_data['test_data'] = {}
            
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")
            context.user_data['creating_test'] = False
