from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from src.models import UserRole
from src.bot.keyboards import KeyboardFactory

class MessageHandlers:
    """Xabar handerlari"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xabar handerlari - har bir foydalanuvchi uchun alohida"""
        user = update.effective_user
        text = update.message.text
        
        # Foydalanuvchi roli olish
        user_role = await self.bot.user_service.get_user_role(user.id)
        
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
            await self.settings_command(update, context)
        elif context.user_data.get('creating_test'):
            # Test yaratish logikasi
            await self._handle_test_creation(update, context, text)
        else:
            await update.message.reply_text("❓ Tushunarsiz xabar. /help komandasi bilan yordam oling.")
    
    async def create_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test yaratish komandasi - faqat o'qituvchilar uchun"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.TEACHER:
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
        """Mavjud testlar - qisqa ma'lumot bilan"""
        tests = await self.bot.test_service.get_available_tests()
        
        if not tests:
            await update.message.reply_text("📝 Hozirda mavjud testlar yo'q.")
            return
        
        text = "📝 Mavjud testlar:\n\n"
        for i, test in enumerate(tests, 1):
            text += f"{i}. 📋 {test.title}\n"
            text += f"   👨‍🏫 {test.teacher.first_name}\n"
            text += f"   📊 {test.passing_score}% o'tish balli\n\n"
        
        reply_markup = KeyboardFactory.get_test_keyboard(tests)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def my_tests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening testlarim - faqat o'qituvchilar uchun"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        tests = await self.bot.test_service.get_teacher_tests(db_user.id)
        
        if not tests:
            await update.message.reply_text("📝 Sizda hali testlar yo'q. Yangi test yarating!")
            return
        
        text = "📋 Mening testlarim:\n\n"
        for i, test in enumerate(tests, 1):
            text += f"{i}. 📝 {test.title}\n"
            text += f"   📊 Holat: {test.status.value}\n"
            text += f"   📂 Toifa: {test.category}\n\n"
        
        reply_markup = KeyboardFactory.get_test_keyboard(tests)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test natijalari - faqat o'qituvchilar uchun"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        await update.message.reply_text("📊 Test natijalari funksiyasi ishlab chiqilmoqda...")
    
    async def my_results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening natijalarim - faqat o'quvchilar uchun"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
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
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sozlamalar - har bir foydalanuvchi uchun alohida"""
        user = update.effective_user
        user_settings = await self.bot.user_service.get_user_settings(user.id)
        
        if not user_settings:
            await update.message.reply_text("❌ Foydalanuvchi sozlamalari topilmadi!")
            return
        
        settings_text = f"""
⚙️ Foydalanuvchi sozlamalari

👤 Foydalanuvchi: {user.first_name}
🆔 Telegram ID: {user.id}
🎭 Rol: {user_settings.role}
🌐 Til: {user_settings.language}
🎨 Tema: {user_settings.theme}
�� Bildirishnomalar: {'✅ Yoqilgan' if user_settings.notifications else '❌ Ochrirlgan'}

📊 Test sozlamalari:
📝 Default test turi: {user_settings.default_test_type}
📂 Default toifa: {user_settings.default_test_category}
📚 Default fan: {user_settings.default_subject or 'Belgilanmagan'}
        """
        
        keyboard = [
            [KeyboardButton("🔄 Rol o'zgartirish")],
            [KeyboardButton("🌐 Til o'zgartirish")],
            [KeyboardButton("🎨 Tema o'zgartirish")],
            [KeyboardButton("🔔 Bildirishnomalar")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(settings_text, reply_markup=reply_markup)
    
    async def _handle_test_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test yaratish jarayonini boshqarish - Soddalashtirilgan"""
        step = context.user_data.get('test_creation_step', 'select_type')
        user = update.effective_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if step == 'select_type':
            await self._handle_test_type_selection(update, context, text)
        elif step == 'select_category':
            await self._handle_test_category_selection(update, context, text)
        elif step == 'enter_title':
            await self._handle_test_title_entry(update, context, text, db_user)
        elif step == 'enter_abcd_answers':
            await self._handle_abcd_answers_entry(update, context, text, db_user)
    
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
                "📝 Endi test nomini kiriting:\n\n"
                "Misol: Algebra testi, Fizika testi, Tarix testi...",
                reply_markup=KeyboardFactory.get_back_keyboard()
            )
            context.user_data['test_creation_step'] = 'enter_title'
        else:
            await update.message.reply_text(
                "❌ Iltimos, quyidagi tugmalardan birini tanlang:",
                reply_markup=KeyboardFactory.get_test_category_keyboard()
            )
    
    async def _handle_test_title_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, db_user):
        """Test nomini kiritish"""
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Test yaratish uchun toifani tanlang:",
                reply_markup=KeyboardFactory.get_test_category_keyboard()
            )
            context.user_data['test_creation_step'] = 'select_category'
            return
        
        context.user_data['test_data']['title'] = text
        
        await update.message.reply_text(
            f"📝 Test nomi: {text}\n\n"
            f"Endi savollar va javoblarni ABCD formatida kiriting:\n\n"
            f"📋 Formatlar:\n"
            f"• abcdabcdabcd... (100 tagacha)\n"
            f"• 1a2b3c4d5a... (raqamli format)\n\n"
            f"📝 Misol:\n"
            f"abcdabcdabcd\n"
            f"yoki\n"
            f"1a2b3c4d5a6b7c8d\n\n"
            f"💡 A = 1-savol to'g'ri javobi\n"
            f"💡 B = 2-savol to'g'ri javobi\n"
            f"💡 C = 3-savol to'g'ri javobi\n"
            f"💡 D = 4-savol to'g'ri javobi",
            reply_markup=KeyboardFactory.get_back_keyboard()
        )
        context.user_data['test_creation_step'] = 'enter_abcd_answers'
    
    async def _handle_abcd_answers_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, db_user):
        """ABCD formatida javoblarni kiritish"""
        if text == '🔙 Orqaga':
            await update.message.reply_text(
                "📝 Endi test nomini kiriting:\n\n"
                "Misol: Algebra testi, Fizika testi, Tarix testi...",
                reply_markup=KeyboardFactory.get_back_keyboard()
            )
            context.user_data['test_creation_step'] = 'enter_title'
            return
        
        try:
            # Test yaratish
            test_data = context.user_data['test_data']
            test = await self.bot.test_creation_service.create_simple_test(test_data, db_user.id)
            
            # ABCD formatida savollar qo'shish
            success = await self.bot.test_creation_service.create_test_with_abcd_answers(test.id, text)
            
            if success:
                # Savollar sonini hisoblash
                questions_count = len(text.replace('\n', '').replace(' ', ''))
                
                await update.message.reply_text(
                    f"✅ Test muvaffaqiyatli yaratildi!\n\n"
                    f"📝 Nomi: {test.title}\n"
                    f"📊 Savollar soni: {questions_count}\n"
                    f"📂 Toifa: {test.category}\n"
                    f"🆔 Test ID: {test.id}\n\n"
                    f"📋 Test \"Mening testlarim\" bo'limida ko'rinadi!",
                    reply_markup=KeyboardFactory.get_main_keyboard(UserRole.TEACHER)
                )
                
                context.user_data['creating_test'] = False
                context.user_data['test_creation_step'] = None
                context.user_data['test_data'] = {}
            else:
                await update.message.reply_text(
                    "❌ Test yaratishda xatolik yuz berdi!",
                    reply_markup=KeyboardFactory.get_back_keyboard()
                )
                
        except Exception as e:
            await update.message.reply_text(
                f"❌ Xatolik: {str(e)}\n\n"
                f"Iltimos, ABCD formatini to'g'ri kiriting!",
                reply_markup=KeyboardFactory.get_back_keyboard()
            )
