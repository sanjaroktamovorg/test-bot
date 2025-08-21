from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
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
            await self.available_tests_menu_command(update, context)
        elif text == "📊 Mening natijalarim":
            await self.my_results_command(update, context)
        elif text == "🌍 Ommaviy testlar":
            await self.public_tests_command(update, context)
        elif text == "🔍 Testni qidirish":
            await self.search_test_command(update, context)
        elif text == "🏆 Reyting":
            await update.message.reply_text("🏆 O'quvchilar reytingi funksiyasi ishlab chiqilmoqda...")
        elif text == "📚 O'quv materiallari":
            await update.message.reply_text("📚 O'quv materiallari funksiyasi ishlab chiqilmoqda...")
        elif text == "❓ Yordam":
            await self.bot.command_handlers.help_command(update, context)
        elif text == "⚙️ Sozlamalar":
            await self.settings_command(update, context)
        elif text == "🔙 Orqaga":
            await update.message.reply_text("🏠 Asosiy menyuga qaytdingiz.", reply_markup=KeyboardFactory.get_main_keyboard(user_role))
        elif context.user_data.get('creating_test'):
            # Test yaratish logikasi
            await self._handle_test_creation(update, context, text)
        elif context.user_data.get('searching_test'):
            # Test qidirish logikasi
            await self._handle_test_search(update, context, text)
        elif context.user_data.get('taking_test'):
            # Test ishlash logikasi
            await self._handle_test_answers(update, context, text)
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
            # Teacher ma'lumotlarini alohida olish
            teacher = await self.bot.user_service.get_user_by_id(test.teacher_id)
            teacher_name = teacher.first_name if teacher else "Noma'lum"
            
            text += f"{i}. 📋 {test.title}\n"
            text += f"   👨‍🏫 {teacher_name}\n"
            text += f"   📊 {test.passing_score or 'Belgilanmagan'}% o'tish balli\n\n"
        
        reply_markup = KeyboardFactory.get_test_keyboard(tests)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def available_tests_menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mavjud testlar menyusi - ReplyKeyboardMarkup bilan"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        text = "📝 Mavjud testlar:\n\nQaysi turdagi testlarni ko'rmoqchisiz?"
        
        keyboard = [
            [KeyboardButton("🌍 Ommaviy testlar"), KeyboardButton("🔍 Testni qidirish")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def public_tests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ommaviy testlar - ReplyKeyboardMarkup bilan"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Faqat ommaviy testlarni olish
        tests = await self.bot.test_service.get_public_tests()
        
        if not tests:
            await update.message.reply_text("📝 Hozircha ommaviy testlar mavjud emas.")
            return
        
        text = "🌍 Ommaviy testlar:\n\n"
        for i, test in enumerate(tests, 1):
            # Teacher ma'lumotlarini alohida olish
            teacher = await self.bot.user_service.get_user_by_id(test.teacher_id)
            teacher_name = teacher.first_name if teacher else "Noma'lum"
            
            text += f"{i}. 📋 {test.title}\n"
            text += f"   👨‍🏫 {teacher_name}\n"
            text += f"   📊 {test.passing_score or 'Belgilanmagan'}% o'tish balli\n\n"
        
        reply_markup = KeyboardFactory.get_test_keyboard(tests)
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def search_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test qidirish - ReplyKeyboardMarkup bilan"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Test qidirish holatini context ga saqlash
        context.user_data['searching_test'] = True
        
        text = "🔍 Test qidirish:\n\nIltimos, test kodini yoki nomini kiriting:"
        
        keyboard = [
            [KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def my_tests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening testlarim - faqat o'qituvchilar uchun"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        # Foydalanuvchi ma'lumotlarini olish
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
            return
        
        # Testlarni olish - teacher_id bo'yicha
        tests = await self.bot.test_service.get_teacher_tests(db_user.id)
        

        
        if not tests:
            await update.message.reply_text("📝 Sizda hali testlar yo'q. Yangi test yarating!")
            return
        
        text = "📋 Mening testlarim:\n\nKerakli testni tanlang va batafsil ma'lumotlarni ko'ring:"
        
        reply_markup = KeyboardFactory.get_teacher_tests_keyboard(tests)
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
            # Test ma'lumotlarini alohida olish
            test = await self.bot.test_service.get_test_by_id(result.test_id)
            test_title = test.title if test else "Noma'lum test"
            
            text += f"📝 {test_title}\n"
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
            f"📋 Qo'llab-quvvatlanadigan formatlar:\n"
            f"• ABCDABCD... (katta harflar)\n"
            f"• abcdabcd... (kichik harflar)\n"
            f"• 1A2B3C4D... (raqam + katta harf)\n"
            f"• 1a2b3c4d... (raqam + kichik harf)\n\n"
            f"📝 Misollar:\n"
            f"ABCDABCDABCD\n"
            f"abcdabcdabcd\n"
            f"1A2B3C4D5A6B7C8D\n"
            f"1a2b3c4d5a6b7c8d\n\n"
            f"💡 Har bir harf bitta savolning to'g'ri javobini bildiradi\n"
            f"💡 100 tagacha savol kiritish mumkin",
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
                # Testni faollashtirish
                await self.bot.test_creation_service.activate_test(test.id)
                
                # Savollar sonini hisoblash - yaratilgan testdan olish
                test_questions = await self.bot.test_service.get_test_questions(test.id)
                questions_count = len(test_questions)
                
                await update.message.reply_text(
                    f"✅ Test muvaffaqiyatli yaratildi va faollashtirildi!\n\n"
                    f"📝 Nomi: {test.title}\n"
                    f"📊 Savollar soni: {questions_count}\n"
                    f"📂 Toifa: {test.category}\n"
                    f"🆔 Test ID: {test.id}\n"
                    f"📊 Holat: ✅ Faol\n\n"
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
    
    async def _handle_test_answers(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test javoblarini qabul qilish"""
        if text == '🔙 Orqaga':
            # Test ishlash holatini to'xtatish
            context.user_data['taking_test'] = False
            context.user_data['current_test'] = {}
            
            await update.message.reply_text(
                "❌ Test bekor qilindi!",
                reply_markup=KeyboardFactory.get_main_keyboard(UserRole.STUDENT)
            )
            return
        
        try:
            # Test ma'lumotlarini olish
            current_test = context.user_data.get('current_test', {})
            test_id = current_test.get('test_id')
            session_id = current_test.get('session_id')
            
            if not test_id or not session_id:
                await update.message.reply_text("❌ Test ma'lumotlari topilmadi!")
                return
            
            # Test ma'lumotlarini olish
            test = await self.bot.test_service.get_test_by_id(test_id)
            if not test:
                await update.message.reply_text("❌ Test topilmadi!")
                return
            
            # Test savollarini olish
            test_questions = await self.bot.test_service.get_test_questions(test_id)
            questions_count = len(test_questions)
            
            # Javoblarni parse qilish
            parsed_answers = await self.bot.test_creation_service.parse_abcd_format(text)
            
            if not parsed_answers:
                await update.message.reply_text(
                    "❌ Javoblar formatini to'g'ri kiriting!\n\n"
                    "💡 Qo'llab-quvvatlanadigan formatlar:\n"
                    "• ABCDABCD... (katta harflar)\n"
                    "• abcdabcd... (kichik harflar)\n"
                    "• 1A2B3C4D... (raqam + katta harf)\n"
                    "• 1a2b3c4d... (raqam + kichik harf)\n\n"
                    "📝 Misol: abcdabcdabcd"
                )
                return
            
            # Javoblar sonini tekshirish
            if len(parsed_answers) != questions_count:
                await update.message.reply_text(
                    f"❌ Javoblar soni noto'g'ri!\n\n"
                    f"📊 Testda {questions_count} ta savol bor\n"
                    f"📝 Siz {len(parsed_answers)} ta javob kiritdingiz\n\n"
                    f"💡 To'g'ri sonida javob kiriting!"
                )
                return
            
            # Javoblarni saqlash
            context.user_data['current_test']['answers'] = parsed_answers
            
            # Testni tugatish va natijalarni hisoblash
            await self._finish_test(update, context, test, parsed_answers, questions_count)
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Xatolik yuz berdi: {str(e)}\n\n"
                f"Iltimos, javoblarni qayta kiriting!"
            )
    
    async def _finish_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test, answers, questions_count):
        """Testni tugatish va natijalarni hisoblash"""
        try:
            # Test savollarini olish
            test_questions = await self.bot.test_service.get_test_questions(test.id)
            
            # To'g'ri javoblarni hisoblash
            correct_answers = 0
            total_score = 0
            max_score = 0
            
            for i, question in enumerate(test_questions):
                max_score += question.points
                
                # Savolning to'g'ri javobini olish
                question_answers = await self.bot.test_service.get_question_answers(question.id)
                correct_answer = None
                
                for answer in question_answers:
                    if answer.is_correct:
                        correct_answer = answer.answer_text
                        break
                
                if correct_answer and i < len(answers):
                    # Foydalanuvchi javobini tekshirish
                    user_answer = answers[i]['correct_answer']
                    
                    if user_answer.upper() == correct_answer.upper():
                        correct_answers += 1
                        total_score += question.points
            
            # Foizni hisoblash
            percentage = (correct_answers / questions_count) * 100 if questions_count > 0 else 0
            
            # Natijani saqlash
            current_test = context.user_data.get('current_test', {})
            session_id = current_test.get('session_id')
            user = update.effective_user
            db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
            
            # Test natijasini saqlash
            test_result = await self.bot.test_service.submit_test_result(
                test_id=test.id,
                student_id=db_user.id,
                score=total_score,
                max_score=max_score,
                answers_data={'answers': answers}
            )
            
            # Test ishlash holatini to'xtatish
            context.user_data['taking_test'] = False
            context.user_data['current_test'] = {}
            
            # Natija xabarini yuborish
            if percentage >= (test.passing_score or 0):
                result_text = "🎉 Tabriklaymiz! Testni o'tdingiz!"
            else:
                result_text = "😔 Afsus! Testni o'ta olmadingiz."
            
            result_message = f"""
✅ Test tugatildi!

📋 Test: {test.title}
📊 Savollar soni: {questions_count}
✅ To'g'ri javoblar: {correct_answers}/{questions_count}
📈 Ball: {total_score}/{max_score}
📊 Foiz: {percentage:.1f}%

🎯 O'tish balli: {test.passing_score or 'Aniqlanmagan'}%
{result_text}
            """
            
            keyboard = [
                [InlineKeyboardButton("📊 Batafsil natija", callback_data=f"view_result_{test_result.id}")],
                [InlineKeyboardButton("📝 Boshqa test", callback_data="available_tests")],

            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(result_message, reply_markup=reply_markup)
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Test tugatishda xatolik: {str(e)}",
                reply_markup=KeyboardFactory.get_main_keyboard(UserRole.STUDENT)
            )
    
    async def _handle_test_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test qidirish logikasi"""
        if text == '🔙 Orqaga':
            # Test qidirish holatini to'xtatish
            context.user_data['searching_test'] = False
            
            # Mavjud testlar menyusiga qaytish - ReplyKeyboardMarkup bilan
            keyboard = [
                [KeyboardButton("🌍 Ommaviy testlar"), KeyboardButton("🔍 Testni qidirish")],
                [KeyboardButton("🔙 Orqaga")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
            
            await update.message.reply_text(
                "📝 Mavjud testlar:\n\nQaysi turdagi testlarni ko'rmoqchisiz?",
                reply_markup=reply_markup
            )
            return
        
        # Test qidirish
        try:
            # Avval test kodini tekshirish
            test = await self.bot.test_service.get_test_by_code(text)
            
            if not test:
                # Test nomi bo'yicha qidirish
                test = await self.bot.test_service.search_test_by_title(text)
            
            if test:
                # Test topildi
                if test.status == "active":
                    # Test ma'lumotlarini ko'rsatish
                    teacher = await self.bot.user_service.get_user_by_id(test.teacher_id)
                    teacher_name = teacher.first_name if teacher else "Noma'lum"
                    
                    test_info = f"""
🔍 Test topildi!

📝 Nomi: {test.title}
📄 Tavsif: {test.description or "Tavsif yo'q"}
👨‍🏫 O'qituvchi: {teacher_name}
📂 Toifa: {'🌍 Ommaviy' if test.category == 'public' else '🔒 Shaxsiy'}
⏱️ Vaqt chegarasi: {test.time_limit or "Cheklanmagan"} daqiqa
🎯 O'tish balli: {test.passing_score or "Aniqlanmagan"}%
🆔 Test kodi: {test.test_code or "Yo'q"}
                    """
                    
                    keyboard = [
                        [InlineKeyboardButton("📝 Testni boshlash", callback_data=f"take_test_{test.id}")],
                        [InlineKeyboardButton("🔍 Boshqa test qidirish", callback_data="search_test")],
                        [InlineKeyboardButton("🔙 Orqaga", callback_data="available_tests")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(test_info, reply_markup=reply_markup)
                    
                    # Qidirish holatini to'xtatish
                    context.user_data['searching_test'] = False
                else:
                    await update.message.reply_text(
                        "❌ Bu test hali faol emas!",
                        reply_markup=KeyboardFactory.get_back_keyboard()
                    )
            else:
                await update.message.reply_text(
                    f"❌ \"{text}\" nomli yoki kodli test topilmadi!\n\n"
                    f"🔍 Qayta urinib ko'ring yoki boshqa test qidiring.",
                    reply_markup=KeyboardFactory.get_back_keyboard()
                )
                
        except Exception as e:
            await update.message.reply_text(
                f"❌ Qidirishda xatolik yuz berdi: {str(e)}",
                reply_markup=KeyboardFactory.get_back_keyboard()
            )
