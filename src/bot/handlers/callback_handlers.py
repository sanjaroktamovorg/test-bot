from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.models import UserRole
from src.bot.keyboards import KeyboardFactory

class CallbackHandlers:
    """Callback handerlari"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback handerlari"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "register":
            await self.register_callback(update, context)
        elif data == "role_teacher":
            await self.role_teacher_callback(update, context)
        elif data == "role_student":
            await self.role_student_callback(update, context)
        elif data == "back_to_menu":
            await self.back_to_menu_callback(update, context)
        elif data.startswith("take_test_"):
            test_id = int(data.split("_")[2])
            await self.take_test_callback(update, context, test_id)
        elif data.startswith("view_teacher_test_"):
            test_id = int(data.split("_")[3])
            await self.view_teacher_test_callback(update, context, test_id)
        elif data.startswith("view_result_"):
            result_id = int(data.split("_")[2])
            await self.view_result_callback(update, context, result_id)
        elif data == "back_to_my_tests":
            await self.back_to_my_tests_callback(update, context)
        elif data == "available_tests":
            await self.available_tests_menu_callback(update, context)
        elif data == "public_tests":
            await self.public_tests_callback(update, context)
        elif data == "search_test":
            await self.search_test_callback(update, context)
        elif data == "my_results":
            await self.my_results_callback(update, context)
        else:
            await query.edit_message_text("❌ Noma'lum callback!")
    
    async def register_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ro'yxatdan o'tish callback"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchini database ga saqlash
        db_user = await self.bot.user_service.register_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if db_user:
            keyboard = [
                [InlineKeyboardButton("👨‍🏫 O'qituvchi", callback_data="role_teacher")],
                [InlineKeyboardButton("👨‍🎓 O'quvchi", callback_data="role_student")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "✅ Ro'yxatdan o'tdingiz! Iltimos, rolingizni tanlang:",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("❌ Ro'yxatdan o'tishda xatolik yuz berdi!")
    
    async def role_teacher_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """O'qituvchi roli tanlash - to'g'ridan-to'g'ri dashboard"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli o'zgartirish
        success = await self.bot.user_service.update_user_role(user.id, UserRole.TEACHER)
        
        if success:
            # To'g'ridan-to'g'ri o'qituvchi dashboard ko'rsatish
            menu_text = f"""
🏠 O'qituvchi Dashboard

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: 👨‍🏫 O'qituvchi
🆔 Telegram ID: {user.id}

Quyidagi tugmalardan birini tanlang:
            """
            
            reply_markup = KeyboardFactory.get_main_keyboard(UserRole.TEACHER)
            await query.edit_message_text(menu_text, reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ Rol o'zgartirishda xatolik yuz berdi!")
    
    async def role_student_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """O'quvchi roli tanlash - to'g'ridan-to'g'ri dashboard"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli o'zgartirish
        success = await self.bot.user_service.update_user_role(user.id, UserRole.STUDENT)
        
        if success:
            # To'g'ridan-to'g'ri o'quvchi dashboard ko'rsatish
            menu_text = f"""
🏠 O'quvchi Dashboard

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: 👨‍🎓 O'quvchi
🆔 Telegram ID: {user.id}

Quyidagi tugmalardan birini tanlang:
            """
            
            reply_markup = KeyboardFactory.get_main_keyboard(UserRole.STUDENT)
            await query.edit_message_text(menu_text, reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ Rol o'zgartirishda xatolik yuz berdi!")
    
    async def back_to_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Asosiy menyuga qaytish"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli olish
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if not user_role:
            await query.edit_message_text("❌ Avval ro'yxatdan o'ting! /register")
            return
        
        role_text = "👨‍🏫 O'qituvchi" if user_role == UserRole.TEACHER else "👨‍🎓 O'quvchi"
        
        menu_text = f"""
🏠 Asosiy menyu

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: {role_text}
🆔 Telegram ID: {user.id}

Quyidagi tugmalardan birini tanlang:
        """
        
        # Inline keyboard yaratish
        if user_role == UserRole.TEACHER:
            keyboard = [
                [InlineKeyboardButton("📝 Test yaratish", callback_data="create_test")],
                [InlineKeyboardButton("📋 Mening testlarim", callback_data="my_tests")],
                [InlineKeyboardButton("📊 Natijalar", callback_data="results")],
                [InlineKeyboardButton("👥 O'quvchilar", callback_data="students")]
            ]
        else:  # STUDENT
            keyboard = [
                [InlineKeyboardButton("📝 Mavjud testlar", callback_data="available_tests")],
                [InlineKeyboardButton("📊 Mening natijalarim", callback_data="my_results")],
                [InlineKeyboardButton("🏆 Reyting", callback_data="rating")],
                [InlineKeyboardButton("📚 O'quv materiallari", callback_data="materials")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(menu_text, reply_markup=reply_markup)
    
    async def take_test_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_id: int):
        """Test ishlash callback"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli tekshirish
        user_role = await self.bot.user_service.get_user_role(user.id)
        if user_role != UserRole.STUDENT:
            await query.edit_message_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Test ma'lumotlarini olish
        test = await self.bot.test_service.get_test_by_id(test_id)
        if not test:
            await query.edit_message_text("❌ Test topilmadi!")
            return
        
        # Test faol ekanligini tekshirish
        if test.status != "active":
            await query.edit_message_text("❌ Bu test hali faol emas!")
            return
        
        # Foydalanuvchi ma'lumotlarini olish
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await query.edit_message_text("❌ Foydalanuvchi topilmadi!")
            return
        
        # Test sessiyasini boshlash
        test_session = await self.bot.test_taking_service.start_test_session(test_id, db_user.id)
        if not test_session:
            await query.edit_message_text("❌ Test sessiyasi boshlanmadi!")
            return
        
        # Test ma'lumotlarini context ga saqlash
        context.user_data['current_test'] = {
            'test_id': test_id,
            'session_id': test_session.id,
            'current_question': 0,
            'answers': {},
            'start_time': test_session.start_time
        }
        
        # Birinchi savolni ko'rsatish
        await self.show_test_question(update, context, 0)
    
    async def view_result_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, result_id: int):
        """Natija ko'rish callback"""
        query = update.callback_query
        await query.edit_message_text("📊 Natija ko'rish funksiyasi ishlab chiqilmoqda...")
    
    async def view_teacher_test_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_id: int):
        """O'qituvchi test batafsilliklari callback"""
        query = update.callback_query
        
        # Test ma'lumotlarini olish
        test = await self.bot.test_service.get_test_by_id(test_id)
        if not test:
            await query.edit_message_text("❌ Test topilmadi!")
            return
        
        # Test statistikalarini olish - relationship o'rniga service ishlatish
        test_questions = await self.bot.test_service.get_test_questions(test.id)
        questions_count = len(test_questions)
        
        # Results sonini olish uchun ham service ishlatish
        test_results = await self.bot.test_service.get_test_results(test.id)
        results_count = len(test_results)
        
        # Test holatini o'zbek tilida ko'rsatish
        status_text = {
            "draft": "📝 Qoralama",
            "active": "✅ Faol",
            "inactive": "❌ Faol emas"
        }.get(test.status, test.status)
        
        # Test toifasini o'zbek tilida ko'rsatish
        category_text = {
            "public": "🌍 Ommaviy",
            "private": "🔒 Shaxsiy"
        }.get(test.category, test.category)
        
        # Batafsil ma'lumotlar
        test_details = f"""
📋 Test batafsilliklari

📝 Nomi: {test.title}
📄 Tavsif: {test.description or "Tavsif yo'q"}
📊 Holat: {status_text}
📂 Toifa: {category_text}
📚 Fan: {test.subject or "Aniqlanmagan"}
⏱️ Vaqt chegarasi: {test.time_limit or "Cheklanmagan"} daqiqa
🎯 O'tish balli: {test.passing_score or "Aniqlanmagan"}%
📊 Savollar soni: {questions_count}
📈 Natijalar soni: {results_count}
📅 Yaratilgan: {test.created_at.strftime('%d.%m.%Y %H:%M')}
🔄 Yangilangan: {test.updated_at.strftime('%d.%m.%Y %H:%M') if test.updated_at else "Yangilanmagan"}
        """
        
        # Tugmalar
        keyboard = [
            [InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"edit_test_{test_id}")],
            [InlineKeyboardButton("📊 Natijalar", callback_data=f"view_test_results_{test_id}")],
            [InlineKeyboardButton("📝 Savollar", callback_data=f"view_test_questions_{test_id}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_my_tests")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(test_details, reply_markup=reply_markup)
    
    async def available_tests_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mavjud testlar menyusi"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli tekshirish
        user_role = await self.bot.user_service.get_user_role(user.id)
        if user_role != UserRole.STUDENT:
            await query.edit_message_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        text = "📝 Mavjud testlar:\n\nQaysi turdagi testlarni ko'rmoqchisiz?"
        
        keyboard = [
            [InlineKeyboardButton("🌍 Ommaviy testlar", callback_data="public_tests")],
            [InlineKeyboardButton("🔍 Testni qidirish", callback_data="search_test")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def public_tests_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ommaviy testlar ro'yxati"""
        query = update.callback_query
        
        # Faqat ommaviy testlarni olish
        tests = await self.bot.test_service.get_public_tests()
        
        if not tests:
            await query.edit_message_text("📝 Hozircha ommaviy testlar mavjud emas.")
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
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def search_test_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test qidirish"""
        query = update.callback_query
        
        # Test qidirish holatini context ga saqlash
        context.user_data['searching_test'] = True
        
        text = "🔍 Test qidirish:\n\nIltimos, test kodini yoki nomini kiriting:"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="available_tests")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def back_to_my_tests_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening testlarim ro'yxatiga qaytish"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli tekshirish
        user_role = await self.bot.user_service.get_user_role(user.id)
        if user_role != UserRole.TEACHER:
            await query.edit_message_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        # Testlar ro'yxatini olish
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        tests = await self.bot.test_service.get_teacher_tests(db_user.id)
        
        if not tests:
            await query.edit_message_text("📝 Sizda hali testlar yo'q. Yangi test yarating!")
            return
        
        text = "📋 Mening testlarim:\n\nKerakli testni tanlang va batafsil ma'lumotlarni ko'ring:"
        reply_markup = KeyboardFactory.get_teacher_tests_keyboard(tests)
        
        await query.edit_message_text(text, reply_markup=reply_markup)

    async def my_results_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening natijalarim callback"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli tekshirish
        user_role = await self.bot.user_service.get_user_role(user.id)
        if user_role != UserRole.STUDENT:
            await query.edit_message_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Foydalanuvchi ma'lumotlarini olish
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await query.edit_message_text("❌ Foydalanuvchi topilmadi!")
            return
        
        # Natijalarni olish
        results = await self.bot.test_service.get_student_results(db_user.id)
        
        if not results:
            await query.edit_message_text("📊 Sizda hali test natijalari yo'q.")
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
        await query.edit_message_text(text, reply_markup=reply_markup)
