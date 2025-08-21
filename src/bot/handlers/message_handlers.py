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
        elif text == "👤 Profil":
            await self.profile_command(update, context)
        elif text == "🏆 Reyting":
            await self.rating_command(update, context)
        elif text == "🥇 O'rtacha ball bo'yicha":
            await self.show_rating_by_average_score(update, context)
        elif text == "🏆 Eng yaxshi natija":
            await self.show_rating_by_best_score(update, context)
        elif text == "📊 Eng faol o'quvchilar":
            await self.show_rating_by_tests_count(update, context)
        elif text == "👤 Mening o'rnim":
            await self.show_my_ranking_position(update, context)
        elif text == "📊 Batafsil statistika":
            await self.detailed_stats_command(update, context)
        elif text == "✏️ Profil tahrirlash":
            await self.edit_profile_command(update, context)
        elif text in ["📷 Profil rasmi", "👨‍🏫 Ism-familya", "👨‍🎓 Ism-familya", "🎂 Yosh", "📝 Haqida", "💼 Tajriba", "📚 Mutaxassislik fani"]:
            await self.handle_profile_edit_field(update, context, text)
        elif text == "🔙 Orqaga":
            # Agar test qidirish holatida bo'lsa, uni to'xtatish
            if context.user_data.get('searching_test'):
                context.user_data['searching_test'] = False
            
            # Agar test yaratish holatida bo'lsa, uni to'xtatish
            if context.user_data.get('creating_test'):
                context.user_data['creating_test'] = False
                context.user_data['test_creation_step'] = None
                context.user_data['test_data'] = {}
            
            # Agar test ishlash holatida bo'lsa, uni to'xtatish
            if context.user_data.get('taking_test'):
                context.user_data['taking_test'] = False
                context.user_data['current_test'] = None
                context.user_data['current_question'] = None
                context.user_data['answers'] = {}
            
            # Agar profil tahrirlash holatida bo'lsa, uni to'xtatish
            if context.user_data.get('editing_profile'):
                context.user_data['editing_profile'] = False
                context.user_data['edit_field'] = None
            
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
        elif context.user_data.get('editing_profile'):
            # Profil tahrirlash logikasi
            await self._handle_profile_edit_data(update, context, text)
        else:
            await update.message.reply_text("❓ Tushunarsiz xabar. /help komandasi bilan yordam oling.")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Rasm qabul qilish"""
        user = update.effective_user
        
        # Profil tahrirlash holatida bo'lsa
        if context.user_data.get('editing_profile') and context.user_data.get('edit_field') == "📷 Profil rasmi":
            try:
                # Rasmni olish
                photo = update.message.photo[-1]  # Eng yuqori sifatli rasm
                file = await context.bot.get_file(photo.file_id)
                
                # Rasm URL ni saqlash
                photo_url = file.file_path
                
                # Bazaga saqlash
                success = await self.bot.user_service.update_profile_field(user.id, "profile_photo", photo_url)
                
                if success:
                    await update.message.reply_text(
                        "✅ Profil rasmi muvaffaqiyatli qabul qilindi va saqlandi!\n\n"
                        "📷 Rasm endi profil ko'rishda ko'rsatiladi.",
                        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
                    )
                else:
                    await update.message.reply_text(
                        "❌ Profil rasmini saqlashda xatolik yuz berdi!\n\n"
                        "Iltimos, qayta urinib ko'ring.",
                        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
                    )
                
                # Profil tahrirlash holatini to'xtatish
                context.user_data['editing_profile'] = False
                context.user_data['edit_field'] = None
                
            except Exception as e:
                await update.message.reply_text(
                    f"❌ Rasmni qabul qilishda xatolik: {str(e)}\n\n"
                    "Iltimos, qayta urinib ko'ring.",
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
                )
        else:
            await update.message.reply_text("📷 Bu rasm qabul qilinmadi. Profil rasmini yuklash uchun '✏️ Profil tahrirlash' tugmasini bosing.")
    
    async def create_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test yaratish komandasi - faqat o'qituvchilar uchun - Inline buttonlar bilan"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu funksiya faqat o'qituvchilar uchun!")
            return
        
        # Inline buttonlar bilan test turi tanlash
        text = "📝 Test yaratish uchun avval test turini tanlang:"
        keyboard = [
            [InlineKeyboardButton("📝 Oddiy test", callback_data="create_test_type_simple")],
            [InlineKeyboardButton("🏛️ DTM test", callback_data="create_test_type_dtm")],
            [InlineKeyboardButton("🏆 Milliy sertifikat test", callback_data="create_test_type_national_cert")],
            [InlineKeyboardButton("📖 Ochiq (variantsiz) test", callback_data="create_test_type_open")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
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
        
        # Foydalanuvchi ma'lumotlarini olish
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
            return
        
        # O'qituvchining testlarini olish
        tests = await self.bot.test_service.get_teacher_tests(db_user.id)
        
        if not tests:
            await update.message.reply_text("📝 Sizda hali testlar yo'q. Yangi test yarating!")
            return
        
        text = "📊 Test natijalari:\n\nQaysi testning natijalarini ko'rmoqchisiz?"
        
        # Testlar ro'yxatini yaratish
        keyboard = []
        for test in tests:
            # Har bir test uchun natijalar sonini olish
            results = await self.bot.test_service.get_test_results(test.id)
            results_count = len(results)
            
            keyboard.append([InlineKeyboardButton(
                f"📝 {test.title} ({results_count} natija)", 
                callback_data=f"view_test_results_{test.id}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
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

�� Bildirishnomalar: {'✅ Yoqilgan' if user_settings.notifications else '❌ Ochrirlgan'}
        """
        
        keyboard = [
            [KeyboardButton("👤 Profil")],
            [KeyboardButton("🌐 Til o'zgartirish")],
            [KeyboardButton("🔔 Bildirishnomalar")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(settings_text, reply_markup=reply_markup)
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Profil ma'lumotlari - har bir foydalanuvchi uchun alohida"""
        user = update.effective_user
        user_settings = await self.bot.user_service.get_user_settings(user.id)
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        profile_data = await self.bot.user_service.get_profile_data(user.id)
        
        if not user_settings or not db_user:
            await update.message.reply_text("❌ Foydalanuvchi ma'lumotlari topilmadi!")
            return
        
        # Foydalanuvchi statistikasini olish
        if user_settings.role == "teacher":
            # O'qituvchi statistikasi
            tests_count = await self.bot.test_service.get_teacher_tests_count(db_user.id)
            total_results = await self.bot.test_service.get_teacher_total_results(db_user.id)
            active_tests = await self.bot.test_service.get_teacher_active_tests_count(db_user.id)
            
            # Profil rasmi mavjudligini tekshirish
            profile_photo = profile_data.get('profile_photo')
            photo_text = "📷 Profil rasmi: Mavjud" if profile_photo else "📷 Profil rasmi: Kiritilmagan"
            
            profile_text = f"""
👤 O'qituvchi Profili

👨‍🏫 Ism: {user.first_name} {user.last_name or ''}
🆔 Telegram ID: {user.id}
📧 Username: @{user.username or 'Yoq'}
🎭 Rol: O'qituvchi
📅 Ro'yxatdan o'tgan: {db_user.created_at.strftime('%d.%m.%Y')}

📷 Profil ma'lumotlari:
{photo_text}
👨‍🏫 To'liq ism: {profile_data.get('full_name', 'Kiritilmagan')}
🎂 Yosh: {profile_data.get('age', 'Kiritilmagan')} yosh
📝 Haqida: {profile_data.get('about', 'Kiritilmagan')}
💼 Tajriba: {profile_data.get('experience', 'Kiritilmagan')} yil
📚 Mutaxassislik: {profile_data.get('specialization', 'Kiritilmagan')}

📊 Statistika:
📝 Yaratilgan testlar: {tests_count}
✅ Faol testlar: {active_tests}
📊 Jami natijalar: {total_results}

🌐 Til: {user_settings.language}

🔔 Bildirishnomalar: {'✅ Yoqilgan' if user_settings.notifications else '❌ Ochrirlgan'}
            """
        else:
            # O'quvchi statistikasi
            completed_tests = await self.bot.test_service.get_student_completed_tests_count(db_user.id)
            average_score = await self.bot.test_service.get_student_average_score(db_user.id)
            best_score = await self.bot.test_service.get_student_best_score(db_user.id)
            
            # Profil rasmi mavjudligini tekshirish
            profile_photo = profile_data.get('profile_photo')
            photo_text = "📷 Profil rasmi: Mavjud" if profile_photo else "📷 Profil rasmi: Kiritilmagan"
            
            profile_text = f"""
👤 O'quvchi Profili

👨‍🎓 Ism: {user.first_name} {user.last_name or ''}
🆔 Telegram ID: {user.id}
📧 Username: @{user.username or 'Yoq'}
🎭 Rol: O'quvchi
📅 Ro'yxatdan o'tgan: {db_user.created_at.strftime('%d.%m.%Y')}

📷 Profil ma'lumotlari:
{photo_text}
👨‍🎓 To'liq ism: {profile_data.get('full_name', 'Kiritilmagan')}
🎂 Yosh: {profile_data.get('age', 'Kiritilmagan')} yosh

📊 Statistika:
📝 Bajarilgan testlar: {completed_tests}
📊 O'rtacha ball: {average_score:.1f}%
🏆 Eng yaxshi natija: {best_score:.1f}%

🌐 Til: {user_settings.language}

🔔 Bildirishnomalar: {'✅ Yoqilgan' if user_settings.notifications else '❌ Ochrirlgan'}
            """
        
        keyboard = [
            [KeyboardButton("✏️ Profil tahrirlash")],
            [KeyboardButton("📊 Batafsil statistika")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        # Agar profil rasmi mavjud bo'lsa, uni ham yuborish
        profile_photo = profile_data.get('profile_photo')
        if profile_photo:
            try:
                await update.message.reply_photo(
                    photo=profile_photo,
                    caption=profile_text,
                    reply_markup=reply_markup
                )
            except Exception as e:
                # Agar rasm yuklanishda xatolik bo'lsa, faqat matn yuborish
                await update.message.reply_text(profile_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(profile_text, reply_markup=reply_markup)
    
    async def detailed_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Batafsil statistika - har bir foydalanuvchi uchun alohida"""
        user = update.effective_user
        user_settings = await self.bot.user_service.get_user_settings(user.id)
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if not user_settings or not db_user:
            await update.message.reply_text("❌ Foydalanuvchi ma'lumotlari topilmadi!")
            return
        
        if user_settings.role == "teacher":
            # O'qituvchi batafsil statistikasi
            tests = await self.bot.test_service.get_teacher_tests(db_user.id)
            total_results = await self.bot.test_service.get_teacher_total_results(db_user.id)
            active_tests = await self.bot.test_service.get_teacher_active_tests_count(db_user.id)
            inactive_tests = len(tests) - active_tests
            
            stats_text = f"""
📊 O'qituvchi Batafsil Statistika

👨‍🏫 {user.first_name} {user.last_name or ''}

📝 Testlar:
• Jami testlar: {len(tests)}
• Faol testlar: {active_tests}
• Faol bo'lmagan: {inactive_tests}

📊 Natijalar:
• Jami natijalar: {total_results}
• O'rtacha natijalar/test: {total_results/len(tests) if len(tests) > 0 else 0:.1f}

📋 So'nggi testlar:
            """
            
            # So'nggi 5 ta testni ko'rsatish
            recent_tests = tests[:5]
            for i, test in enumerate(recent_tests, 1):
                test_results = await self.bot.test_service.get_test_results(test.id)
                stats_text += f"{i}. {test.title} ({len(test_results)} natija)\n"
            
            if len(tests) > 5:
                stats_text += f"... va {len(tests) - 5} ta boshqa test\n"
            
        else:
            # O'quvchi batafsil statistikasi
            results = await self.bot.test_service.get_student_results(db_user.id)
            completed_tests = len(results)
            average_score = await self.bot.test_service.get_student_average_score(db_user.id)
            best_score = await self.bot.test_service.get_student_best_score(db_user.id)
            
            # Natijalar bo'yicha tahlil
            passed_tests = sum(1 for r in results if r.percentage >= 60)
            failed_tests = completed_tests - passed_tests
            
            stats_text = f"""
📊 O'quvchi Batafsil Statistika

👨‍🎓 {user.first_name} {user.last_name or ''}

📝 Testlar:
• Bajarilgan testlar: {completed_tests}
• O'tgan testlar: {passed_tests}
• O'tmagan testlar: {failed_tests}
• O'tish foizi: {passed_tests/completed_tests*100 if completed_tests > 0 else 0:.1f}%

📊 Ballar:
• O'rtacha ball: {average_score:.1f}%
• Eng yaxshi natija: {best_score:.1f}%
• Eng past natija: {min([r.percentage for r in results]) if results else 0:.1f}%

📋 So'nggi natijalar:
            """
            
            # So'nggi 5 ta natijani ko'rsatish
            recent_results = results[:5]
            for i, result in enumerate(recent_results, 1):
                test = await self.bot.test_service.get_test_by_id(result.test_id)
                test_title = test.title if test else "Noma'lum test"
                status = "✅ O'tdi" if result.percentage >= 60 else "❌ O'tmadi"
                stats_text += f"{i}. {test_title} - {result.percentage:.1f}% {status}\n"
            
            if len(results) > 5:
                stats_text += f"... va {len(results) - 5} ta boshqa natija\n"
        
        keyboard = [
            [KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(stats_text, reply_markup=reply_markup)
    
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
        """Test nomini kiritish - Inline buttonlar bilan"""
        if text == '🔙 Orqaga':
            # Inline buttonlar bilan toifa tanlashga qaytish
            text = "📝 Test yaratish uchun toifani tanlang:"
            keyboard = [
                [InlineKeyboardButton("🌍 Ommaviy test", callback_data="create_test_category_public")],
                [InlineKeyboardButton("🔒 Shaxsiy test", callback_data="create_test_category_private")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(text, reply_markup=reply_markup)
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
                
                # Test ma'lumotlarini tayyorlash
                test_info = f"✅ Test muvaffaqiyatli yaratildi va faollashtirildi!\n\n"
                test_info += f"📝 Nomi: {test.title}\n"
                test_info += f"📊 Savollar soni: {questions_count}\n"
                test_info += f"📂 Toifa: {test.category}\n"
                test_info += f"🆔 Test ID: {test.id}\n"
                test_info += f"📊 Holat: ✅ Faol\n\n"
                
                # Shaxsiy test uchun maxsus ma'lumotlar
                if test.category == "private":
                    test_info += f"🔐 Shaxsiy test ma'lumotlari:\n"
                    test_info += f"🔢 Maxsus raqam: {test.test_code}\n"
                    test_info += f"🔗 Ulashish havolasi: https://t.me/your_bot_username?start=test_{test.test_code}\n\n"
                    test_info += f"💡 O'quvchilar testni faqat maxsus raqam orqali topa oladi!\n"
                else:
                    test_info += f"🌍 Ommaviy test - barcha o'quvchilar ko'ra oladi!\n"
                
                test_info += f"\n📋 Test \"Mening testlarim\" bo'limida ko'rinadi!"
                
                # Inline buttonlar bilan test ma'lumotlari
                keyboard = [
                    [InlineKeyboardButton("📋 Mening testlarim", callback_data="back_to_my_tests")],
                    [InlineKeyboardButton("📝 Yangi test yaratish", callback_data="create_test_type_simple")],
                    [InlineKeyboardButton("🏠 Asosiy menyu", callback_data="back_to_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(test_info, reply_markup=reply_markup)
                
                context.user_data['creating_test'] = False
                context.user_data['test_creation_step'] = None
                context.user_data['test_data'] = {}
            else:
                await update.message.reply_text(
                    "❌ Test yaratishda xatolik yuz berdi!",
                    reply_markup=KeyboardFactory.get_back_keyboard()
                )
                
        except ValueError as e:
            # Test nomi takrorlanishi xatoligi
            if "allaqachon mavjud" in str(e):
                await update.message.reply_text(
                    f"❌ {str(e)}\n\n"
                    f"📝 Iltimos, boshqa nom kiriting:",
                    reply_markup=KeyboardFactory.get_back_keyboard()
                )
                context.user_data['test_creation_step'] = 'enter_title'
            else:
                await update.message.reply_text(
                    f"❌ Xatolik: {str(e)}\n\n"
                    f"Iltimos, ABCD formatini to'g'ri kiriting!",
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
                    
                    # To'g'ri javobni "Variant A" dan "A" ga o'zgartirish
                    correct_answer_letter = correct_answer.replace('Variant ', '').strip()
                    
                    if user_answer.upper() == correct_answer_letter.upper():
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
            
            # O'qituvchiga xabar yuborish
            await self._notify_teacher_about_result(update, context, test, db_user, correct_answers, questions_count, answers)
            
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
    
    async def _notify_teacher_about_result(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test, student, correct_answers, questions_count, answers):
        """O'qituvchiga o'quvchi natijasi haqida xabar yuborish"""
        try:
            # O'qituvchini topish
            teacher = await self.bot.user_service.get_user_by_id(test.teacher_id)
            if not teacher:
                return
            
            # O'quvchi ma'lumotlari
            student_name = f"{student.first_name} {student.last_name or ''}".strip()
            if not student_name:
                student_name = student.username or "Noma'lum o'quvchi"
            
            # Natija xabarini tayyorlash
            percentage = (correct_answers / questions_count) * 100 if questions_count > 0 else 0
            
            # Natija holatini alohida aniqlash
            result_status = '✅ O\'tdi' if percentage >= (test.passing_score or 0) else '❌ O\'tmadi'
            
            notification_message = f"""
📊 Yangi test natijasi!

👨‍🎓 O'quvchi: {student_name}
📝 Test: {test.title}
✅ To'g'ri javoblar: {correct_answers}/{questions_count}
📊 Foiz: {percentage:.1f}%
🎯 Natija: {result_status}

📈 Batafsil natijalarni ko'rish uchun "📊 Natijalar" tugmasini bosing!
            """
            
            # O'qituvchi uchun keyboard
            keyboard = [
                [InlineKeyboardButton("📊 Natijalar", callback_data=f"teacher_results_{test.id}")],
                [InlineKeyboardButton("📋 Barcha testlarim", callback_data="my_tests")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # O'qituvchiga xabar yuborish
            await context.bot.send_message(
                chat_id=teacher.telegram_id,
                text=notification_message,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            print(f"O'qituvchiga xabar yuborishda xatolik: {str(e)}")
    
    async def _handle_test_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Test qidirish logikasi"""
        user = update.effective_user
        
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
            # Avval test kodini tekshirish (shaxsiy testlar uchun)
            test = await self.bot.test_service.get_test_by_code(text)
            
            if test:
                # Shaxsiy test topildi
                if test.status == "active":
                    await self._show_single_test_result(update, context, test)
                    context.user_data['searching_test'] = False
                else:
                    user_role = await self.bot.user_service.get_user_role(user.id)
                    await update.message.reply_text(
                        "❌ Bu test hali faol emas!",
                        reply_markup=KeyboardFactory.get_back_keyboard(user_role)
                    )
            else:
                # Ommaviy testlarni nom bo'yicha qidirish
                await self._search_public_tests_by_title(update, context, text)
                
        except Exception as e:
            user_role = await self.bot.user_service.get_user_role(user.id)
            await update.message.reply_text(
                f"❌ Qidirishda xatolik yuz berdi: {str(e)}",
                reply_markup=KeyboardFactory.get_back_keyboard(user_role)
            )
    
    async def edit_profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Profil tahrirlash - foydalanuvchi roliga qarab"""
        user = update.effective_user
        user_settings = await self.bot.user_service.get_user_settings(user.id)
        
        if not user_settings:
            await update.message.reply_text("❌ Foydalanuvchi sozlamalari topilmadi!")
            return
        
        if user_settings.role == "teacher":
            # O'qituvchi uchun profil tahrirlash
            edit_text = """
✏️ O'qituvchi Profil Tahrirlash

Quyidagi ma'lumotlarni kiritish/yangilash mumkin:

📷 Profil rasmi
👨‍🏫 To'liq ism-familya
🎂 Yosh
📝 Haqida (qisqacha)
💼 Tajriba (yillar)
📚 Mutaxassislik fani

Qaysi ma'lumotni tahrirlashni xohlaysiz?
            """
            
            keyboard = [
                [KeyboardButton("📷 Profil rasmi"), KeyboardButton("👨‍🏫 Ism-familya")],
                [KeyboardButton("🎂 Yosh"), KeyboardButton("📝 Haqida")],
                [KeyboardButton("💼 Tajriba"), KeyboardButton("📚 Mutaxassislik fani")],
                [KeyboardButton("🔙 Orqaga")]
            ]
        else:
            # O'quvchi uchun profil tahrirlash
            edit_text = """
✏️ O'quvchi Profil Tahrirlash

Quyidagi ma'lumotlarni kiritish/yangilash mumkin:

👨‍🎓 To'liq ism-familya
🎂 Yosh

Qaysi ma'lumotni tahrirlashni xohlaysiz?
            """
            
            keyboard = [
                [KeyboardButton("👨‍🎓 Ism-familya")],
                [KeyboardButton("🎂 Yosh")],
                [KeyboardButton("🔙 Orqaga")]
            ]
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(edit_text, reply_markup=reply_markup)
    
    async def handle_profile_edit_field(self, update: Update, context: ContextTypes.DEFAULT_TYPE, field_type: str):
        """Profil maydonini tahrirlash"""
        user = update.effective_user
        
        # Profil tahrirlash holatini context ga saqlash
        context.user_data['editing_profile'] = True
        context.user_data['edit_field'] = field_type
        
        if field_type == "📷 Profil rasmi":
            text = "📷 Profil rasmini yuklash\n\nIltimos, yangi profil rasmingizni yuboring:"
        elif field_type in ["👨‍🏫 Ism-familya", "👨‍🎓 Ism-familya"]:
            text = "👤 To'liq ism-familya\n\nIltimos, to'liq ism-familyangizni kiriting:"
        elif field_type == "🎂 Yosh":
            text = "🎂 Yosh ma'lumoti\n\nIltimos, yoshingizni kiriting (raqamda):"
        elif field_type == "📝 Haqida":
            text = "📝 Haqida ma'lumot\n\nIltimos, o'zingiz haqida qisqacha ma'lumot kiriting:"
        elif field_type == "💼 Tajriba":
            text = "💼 Ish tajribasi\n\nIltimos, ish tajribangizni yillarda kiriting (masalan: 5):"
        elif field_type == "📚 Mutaxassislik fani":
            text = "📚 Mutaxassislik fani\n\nIltimos, mutaxassislik faningizni kiriting:"
        
        keyboard = [
            [KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def _handle_profile_edit_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Profil tahrirlash ma'lumotlarini saqlash"""
        if text == "🔙 Orqaga":
            # Profil tahrirlash holatini to'xtatish
            context.user_data['editing_profile'] = False
            context.user_data['edit_field'] = None
            
            # Asosiy menyuga qaytish
            user_role = await self.bot.user_service.get_user_role(user.id)
            await update.message.reply_text("🏠 Asosiy menyuga qaytdingiz.", reply_markup=KeyboardFactory.get_main_keyboard(user_role))
            return
        
        user = update.effective_user
        field_type = context.user_data.get('edit_field')
        
        try:
            # Ma'lumotlarni validatsiya qilish
            if field_type == "🎂 Yosh":
                try:
                    age = int(text)
                    if age < 5 or age > 100:
                        await update.message.reply_text(
                            "❌ Yosh 5 dan 100 gacha bo'lishi kerak!\n\nIltimos, to'g'ri yosh kiriting:",
                            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
                        )
                        return
                except ValueError:
                    await update.message.reply_text(
                        "❌ Yosh raqamda kiritilishi kerak!\n\nIltimos, to'g'ri yosh kiriting:",
                        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
                    )
                    return
            elif field_type == "💼 Tajriba":
                try:
                    experience = int(text)
                    if experience < 0 or experience > 50:
                        await update.message.reply_text(
                            "❌ Tajriba 0 dan 50 yilgacha bo'lishi kerak!\n\nIltimos, to'g'ri tajriba kiriting:",
                            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
                        )
                        return
                except ValueError:
                    await update.message.reply_text(
                        "❌ Tajriba raqamda kiritilishi kerak!\n\nIltimos, to'g'ri tajriba kiriting:",
                        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
                    )
                    return
            
            # Ma'lumotlarni saqlash
            field_mapping = {
                "📷 Profil rasmi": "profile_photo",
                "👨‍🏫 Ism-familya": "full_name",
                "👨‍🎓 Ism-familya": "full_name",
                "🎂 Yosh": "age",
                "📝 Haqida": "about",
                "💼 Tajriba": "experience",
                "📚 Mutaxassislik fani": "specialization"
            }
            
            db_field = field_mapping.get(field_type)
            if db_field:
                # Ma'lumotlarni bazaga saqlash
                success = await self.bot.user_service.update_profile_field(user.id, db_field, text)
                if success:
                    success_message = f"✅ {field_type} muvaffaqiyatli yangilandi!\n\n📝 Yangi qiymat: {text}\n\n💡 Endi profil ko'rishda bu ma'lumot ko'rsatiladi."
                else:
                    success_message = f"❌ {field_type} yangilashda xatolik yuz berdi!\n\nIltimos, qayta urinib ko'ring."
            else:
                success_message = f"✅ {field_type} muvaffaqiyatli yangilandi!\n\n📝 Yangi qiymat: {text}\n\n💡 Endi profil ko'rishda bu ma'lumot ko'rsatiladi."
            
            # Profil tahrirlash holatini to'xtatish
            context.user_data['editing_profile'] = False
            context.user_data['edit_field'] = None
            
            # Asosiy menyuga qaytish
            user_role = await self.bot.user_service.get_user_role(user.id)
            reply_markup = KeyboardFactory.get_main_keyboard(user_role)
            
            await update.message.reply_text(success_message, reply_markup=reply_markup)
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Ma'lumotlarni saqlashda xatolik: {str(e)}\n\nQayta urinib ko'ring:",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
            )
    
    async def rating_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reyting - faqat o'quvchilar uchun"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # O'quvchining ma'lumotlarini olish
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
            return
        
        # O'quvchining reytingdagi o'rnini olish
        ranking = await self.bot.test_service.get_student_ranking_position(db_user.id)
        
        # Reyting menyusini ko'rsatish
        rating_text = f"""
🏆 O'quvchilar Reytingi

👤 Sizning ma'lumotlaringiz:
📊 O'rtacha ball: {ranking['avg_score']:.1f}%
📝 Bajarilgan testlar: {ranking['tests_count']} ta

"""
        
        if ranking['position']:
            rating_text += f"🏅 Reytingdagi o'rin: {ranking['position']}/{ranking['total_students']}\n\n"
        else:
            rating_text += "📊 Reytingda qatnashish uchun test bajarishingiz kerak!\n\n"
        
        rating_text += "📋 Reyting turlarini tanlang:"
        
        keyboard = [
            [KeyboardButton("🥇 O'rtacha ball bo'yicha"), KeyboardButton("🏆 Eng yaxshi natija")],
            [KeyboardButton("📊 Eng faol o'quvchilar"), KeyboardButton("👤 Mening o'rnim")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(rating_text, reply_markup=reply_markup)
    
    async def show_rating_by_average_score(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """O'rtacha ball bo'yicha reyting"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Top 10 o'quvchilarni olish
        top_students = await self.bot.test_service.get_top_students_by_average_score(10)
        
        if not top_students:
            await update.message.reply_text("📊 Hozircha reyting ma'lumotlari yo'q.")
            return
        
        rating_text = "🥇 O'rtacha ball bo'yicha TOP 10:\n\n"
        
        for i, student_data in enumerate(top_students, 1):
            # O'quvchi ma'lumotlarini olish
            student = await self.bot.user_service.get_user_by_id(student_data.student_id)
            student_name = student.first_name if student else "Noma'lum"
            
            # Medal emojilari
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            rating_text += f"{medal} {student_name}\n"
            rating_text += f"   📊 O'rtacha: {student_data.avg_score:.1f}%\n"
            rating_text += f"   📝 Testlar: {student_data.tests_count} ta\n\n"
        
        keyboard = [
            [KeyboardButton("🏆 Eng yaxshi natija"), KeyboardButton("📊 Eng faol o'quvchilar")],
            [KeyboardButton("👤 Mening o'rnim"), KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(rating_text, reply_markup=reply_markup)
    
    async def show_rating_by_best_score(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Eng yaxshi natija bo'yicha reyting"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Top 10 o'quvchilarni olish
        top_students = await self.bot.test_service.get_top_students_by_best_score(10)
        
        if not top_students:
            await update.message.reply_text("📊 Hozircha reyting ma'lumotlari yo'q.")
            return
        
        rating_text = "🏆 Eng yaxshi natija bo'yicha TOP 10:\n\n"
        
        for i, student_data in enumerate(top_students, 1):
            # O'quvchi ma'lumotlarini olish
            student = await self.bot.user_service.get_user_by_id(student_data.student_id)
            student_name = student.first_name if student else "Noma'lum"
            
            # Medal emojilari
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            rating_text += f"{medal} {student_name}\n"
            rating_text += f"   🏆 Eng yaxshi: {student_data.best_score:.1f}%\n"
            rating_text += f"   📝 Testlar: {student_data.tests_count} ta\n\n"
        
        keyboard = [
            [KeyboardButton("🥇 O'rtacha ball bo'yicha"), KeyboardButton("📊 Eng faol o'quvchilar")],
            [KeyboardButton("👤 Mening o'rnim"), KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(rating_text, reply_markup=reply_markup)
    
    async def show_rating_by_tests_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Eng faol o'quvchilar reytingi"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Top 10 o'quvchilarni olish
        top_students = await self.bot.test_service.get_top_students_by_tests_count(10)
        
        if not top_students:
            await update.message.reply_text("📊 Hozircha reyting ma'lumotlari yo'q.")
            return
        
        rating_text = "📊 Eng faol o'quvchilar TOP 10:\n\n"
        
        for i, student_data in enumerate(top_students, 1):
            # O'quvchi ma'lumotlarini olish
            student = await self.bot.user_service.get_user_by_id(student_data.student_id)
            student_name = student.first_name if student else "Noma'lum"
            
            # Medal emojilari
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            rating_text += f"{medal} {student_name}\n"
            rating_text += f"   📝 Testlar: {student_data.tests_count} ta\n"
            rating_text += f"   📊 O'rtacha: {student_data.avg_score:.1f}%\n\n"
        
        keyboard = [
            [KeyboardButton("🥇 O'rtacha ball bo'yicha"), KeyboardButton("🏆 Eng yaxshi natija")],
            [KeyboardButton("👤 Mening o'rnim"), KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(rating_text, reply_markup=reply_markup)
    
    async def show_my_ranking_position(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """O'quvchining o'z o'rnini ko'rsatish"""
        user = update.effective_user
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if user_role != UserRole.STUDENT:
            await update.message.reply_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # O'quvchining ma'lumotlarini olish
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
            return
        
        # O'quvchining reytingdagi o'rnini olish
        ranking = await self.bot.test_service.get_student_ranking_position(db_user.id)
        
        if not ranking['position']:
            await update.message.reply_text(
                "📊 Reytingda qatnashish uchun kamida 1 ta test bajarishingiz kerak!\n\n"
                "📝 Test bajarib, natijalaringizni ko'ring!",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
            )
            return
        
        # O'quvchining statistikasini olish
        avg_score = await self.bot.test_service.get_student_average_score(db_user.id)
        best_score = await self.bot.test_service.get_student_best_score(db_user.id)
        
        position_text = f"""
👤 Sizning reyting ma'lumotlaringiz:

🏅 Reytingdagi o'rin: {ranking['position']}/{ranking['total_students']}
📊 O'rtacha ball: {ranking['avg_score']:.1f}%
🏆 Eng yaxshi natija: {best_score:.1f}%
📝 Bajarilgan testlar: {ranking['tests_count']} ta

"""
        
        # O'rin bo'yicha motivatsion xabar
        if ranking['position'] <= 3:
            position_text += "🎉 Ajoyib! Siz eng yaxshi o'quvchilar qatoridasiz!"
        elif ranking['position'] <= 10:
            position_text += "👍 Yaxshi natija! Davom eting!"
        elif ranking['position'] <= ranking['total_students'] // 2:
            position_text += "📈 O'rtacha natija. Yaxshilash uchun ko'proq test bajarib ko'ring!"
        else:
            position_text += "💪 Natijalaringizni yaxshilash uchun ko'proq mashq qiling!"
        
        keyboard = [
            [KeyboardButton("🥇 O'rtacha ball bo'yicha"), KeyboardButton("🏆 Eng yaxshi natija")],
            [KeyboardButton("📊 Eng faol o'quvchilar"), KeyboardButton("🔙 Orqaga")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(position_text, reply_markup=reply_markup)
    
    async def _show_single_test_result(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test):
        """Bitta test natijasini ko'rsatish"""
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
    
    async def _search_public_tests_by_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, page: int = 1):
        """Ommaviy testlarni nom bo'yicha qidirish (sahifalash bilan)"""
        try:
            # Testlarni olish
            limit = 10
            offset = (page - 1) * limit
            tests = await self.bot.test_service.search_public_tests_by_title(title, limit, offset)
            total_count = await self.bot.test_service.count_public_tests_by_title(title)
            
            if not tests:
                user_role = await self.bot.user_service.get_user_role(update.effective_user.id)
                await update.message.reply_text(
                    f"❌ \"{title}\" nomli ommaviy test topilmadi!\n\n"
                    f"🔍 Qayta urinib ko'ring yoki boshqa test qidiring.",
                    reply_markup=KeyboardFactory.get_back_keyboard(user_role)
                )
                return
            
            # Sahifa ma'lumotlari
            total_pages = (total_count + limit - 1) // limit
            start_idx = offset + 1
            end_idx = min(offset + len(tests), total_count)
            
            # Testlar ro'yxatini yaratish
            tests_text = f"""
🔍 Ommaviy testlar qidiruv natijasi: "{title}"

📊 Topilgan testlar: {total_count} ta
📄 Sahifa: {page}/{total_pages} ({start_idx}-{end_idx})

"""
            
            for i, test in enumerate(tests, start_idx):
                teacher = await self.bot.user_service.get_user_by_id(test.teacher_id)
                teacher_name = teacher.first_name if teacher else "Noma'lum"
                
                tests_text += f"""
{i}. 📝 {test.title}
👨‍🏫 O'qituvchi: {teacher_name}
⏱️ Vaqt: {test.time_limit or "Cheklanmagan"} daqiqa
🎯 O'tish balli: {test.passing_score or "Aniqlanmagan"}%
🆔 ID: {test.id}

"""
            
            # Navigatsiya tugmalari
            keyboard = []
            
            # Test boshlash tugmalari (faqat birinchi 5 ta test uchun)
            for i, test in enumerate(tests[:5]):
                keyboard.append([InlineKeyboardButton(f"📝 {test.title[:20]}...", callback_data=f"take_test_{test.id}")])
            
            # Navigatsiya tugmalari
            nav_buttons = []
            if page > 1:
                nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"search_page_{title}_{page-1}"))
            if page < total_pages:
                nav_buttons.append(InlineKeyboardButton("➡️ Keyingi", callback_data=f"search_page_{title}_{page+1}"))
            
            if nav_buttons:
                keyboard.append(nav_buttons)
            
            # Boshqaruv tugmalari
            keyboard.append([
                InlineKeyboardButton("🔍 Boshqa qidirish", callback_data="search_test"),
                InlineKeyboardButton("🔙 Orqaga", callback_data="available_tests")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(tests_text, reply_markup=reply_markup)
            
        except Exception as e:
            user_role = await self.bot.user_service.get_user_role(update.effective_user.id)
            await update.message.reply_text(
                f"❌ Qidirishda xatolik: {str(e)}",
                reply_markup=KeyboardFactory.get_back_keyboard(user_role)
            )
