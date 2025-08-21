from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.models import UserRole
from src.bot.keyboards import KeyboardFactory
import time

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
        elif data.startswith("start_test_"):
            test_id = int(data.split("_")[2])
            await self.start_test_callback(update, context, test_id)
        elif data.startswith("teacher_results_"):
            test_id = int(data.split("_")[2])
            await self.teacher_results_callback(update, context, test_id)
        elif data.startswith("view_test_results_"):
            test_id = int(data.split("_")[3])
            await self.teacher_results_callback(update, context, test_id)
        elif data == "back_to_menu":
            await self.back_to_menu_callback(update, context)
        else:
            await query.edit_message_text("❌ Noma'lum callback!")
    
    async def teacher_results_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_id: int):
        """O'qituvchi uchun test natijalarini ko'rish"""
        query = update.callback_query
        
        try:
            # Testni topish
            test = await self.bot.test_service.get_test_by_id(test_id)
            if not test:
                await query.edit_message_text("❌ Test topilmadi!")
                return
            
            # Test natijalarini olish
            results = await self.bot.test_service.get_test_results(test_id)
            if not results:
                await query.edit_message_text("📊 Bu test uchun hali natijalar yo'q!")
                return
            
            # Natijalar jadvalini yaratish
            table_text = await self._create_results_table(test, results)
            
            # PDF yaratish
            pdf_path = await self._create_results_pdf(test, results)
            
            # Natijalarni yuborish
            await query.edit_message_text(
                f"📊 {test.title} testi natijalari:\n\n{table_text}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📄 PDF yuklab olish", callback_data=f"download_pdf_{test_id}")],
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="my_tests")]
                ])
            )
            
            # PDF faylni yuborish
            if pdf_path:
                with open(pdf_path, 'rb') as pdf_file:
                    await context.bot.send_document(
                        chat_id=query.from_user.id,
                        document=pdf_file,
                        filename=f"{test.title}_natijalari.pdf"
                    )
            
        except Exception as e:
            await query.edit_message_text(f"❌ Natijalarni ko'rishda xatolik: {str(e)}")
    
    async def _create_results_table(self, test, results):
        """Natijalar jadvalini yaratish"""
        try:
            # Jadval sarlavhasi
            table = f"📊 {test.title} testi natijalari\n\n"
            table += "🏆 Reyting | 👤 Ism Familiya | "
            
            # Savollar sonini aniqlash
            questions = await self.bot.test_service.get_test_questions(test.id)
            for i in range(len(questions)):
                table += f"{i+1} | "
            table += "T.J.S\n"
            table += "─" * 50 + "\n"
            
            # Natijalarni saralash (reyting bo'yicha)
            sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
            
            for rank, result in enumerate(sorted_results, 1):
                # O'quvchi ma'lumotlari
                student = await self.bot.user_service.get_user_by_id(result.student_id)
                student_name = f"{student.first_name} {student.last_name or ''}".strip()
                if not student_name:
                    student_name = student.username or "Noma'lum"
                
                # Natija qatorini yaratish
                row = f"{rank:2d} | {student_name:15s} | "
                
                # Har bir savol uchun natija
                answers_data = result.answers_data.get('answers', [])
                correct_count = 0
                
                for i, question in enumerate(questions):
                    if i < len(answers_data):
                        user_answer = answers_data[i]['correct_answer']
                        # To'g'ri javobni aniqlash
                        question_answers = await self.bot.test_service.get_question_answers(question.id)
                        correct_answer = None
                        for answer in question_answers:
                            if answer.is_correct:
                                correct_answer = answer.answer_text.replace('Variant ', '').strip()
                                break
                        
                        # Natijani belgilash
                        if user_answer.upper() == correct_answer.upper():
                            row += "1 | "
                            correct_count += 1
                        else:
                            row += "0 | "
                    else:
                        row += "- | "
                
                # To'g'ri javoblar soni
                row += f"{correct_count}\n"
                table += row
            
            return table
            
        except Exception as e:
            return f"❌ Jadval yaratishda xatolik: {str(e)}"
    
    async def _create_results_pdf(self, test, results):
        """Natijalar PDF faylini yaratish"""
        try:
            # PDF yaratish uchun reportlab ishlatamiz
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            import os
            
            # PDF fayl nomi
            pdf_filename = f"test_results_{test.id}_{int(time.time())}.pdf"
            pdf_path = f"/tmp/{pdf_filename}"
            
            # PDF hujjatini yaratish
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            
            # Sarlavha
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Markazga tekislash
            )
            
            title = Paragraph(f"{test.title} testi natijalari", title_style)
            elements.append(title)
            
            # Jadval ma'lumotlari
            questions = await self.bot.test_service.get_test_questions(test.id)
            
            # Jadval sarlavhasi
            headers = ['Reyting', 'Ism Familiya']
            for i in range(len(questions)):
                headers.append(str(i+1))
            headers.append('T.J.S')
            
            table_data = [headers]
            
            # Natijalarni saralash
            sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
            
            for rank, result in enumerate(sorted_results, 1):
                # O'quvchi ma'lumotlari
                student = await self.bot.user_service.get_user_by_id(result.student_id)
                student_name = f"{student.first_name} {student.last_name or ''}".strip()
                if not student_name:
                    student_name = student.username or "Noma'lum"
                
                # Natija qatori
                row = [str(rank), student_name]
                
                # Har bir savol uchun natija
                answers_data = result.answers_data.get('answers', [])
                correct_count = 0
                
                for i, question in enumerate(questions):
                    if i < len(answers_data):
                        user_answer = answers_data[i]['correct_answer']
                        # To'g'ri javobni aniqlash
                        question_answers = await self.bot.test_service.get_question_answers(question.id)
                        correct_answer = None
                        for answer in question_answers:
                            if answer.is_correct:
                                correct_answer = answer.answer_text.replace('Variant ', '').strip()
                                break
                        
                        # Natijani belgilash
                        if user_answer.upper() == correct_answer.upper():
                            row.append('1')
                            correct_count += 1
                        else:
                            row.append('0')
                    else:
                        row.append('-')
                
                # To'g'ri javoblar soni
                row.append(str(correct_count))
                table_data.append(row)
            
            # Jadvalni yaratish
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            elements.append(table)
            
            # PDF yaratish
            doc.build(elements)
            
            return pdf_path
            
        except Exception as e:
            print(f"PDF yaratishda xatolik: {str(e)}")
            return None
    
    async def back_to_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Asosiy menyuga qaytish"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli tekshirish
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        menu_text = f"""
🏠 Asosiy menyu

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: {'👨‍🏫 O\'qituvchi' if user_role == UserRole.TEACHER else '👨‍🎓 O\'quvchi'}

Quyidagi tugmalardan birini tanlang:
        """
        
        reply_markup = KeyboardFactory.get_main_keyboard(user_role)
        await query.edit_message_text(menu_text, reply_markup=reply_markup)
    
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
        
        if 'error' in test_session:
            await query.edit_message_text(f"❌ {test_session['error']}")
            return
        
        # Test ma'lumotlarini context ga saqlash
        context.user_data['current_test'] = {
            'test_id': test_id,
            'session_id': test_session['session_id'],
            'current_question': 0,
            'answers': {},
            'start_time': test_session['started_at']
        }
        
        # Test avtomatik boshlanadi - start_test_callback ni chaqirish
        await self.start_test_callback(update, context, test_id)
    
    async def view_result_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, result_id: int):
        """Natija ko'rish callback"""
        query = update.callback_query
        
        # Test natijasini olish
        try:
            # Test natijasini database dan olish
            from src.models import TestResult
            session = self.bot.test_service.db.get_session()
            
            try:
                result = session.query(TestResult).filter(TestResult.id == result_id).first()
                
                if not result:
                    await query.edit_message_text("❌ Natija topilmadi!")
                    return
                
                # Test ma'lumotlarini olish
                test = await self.bot.test_service.get_test_by_id(result.test_id)
                if not test:
                    await query.edit_message_text("❌ Test ma'lumotlari topilmadi!")
                    return
                
                # Batafsil natija xabarini yaratish
                date_str = result.completed_at.strftime('%d.%m.%Y %H:%M') if result.completed_at else 'Noma\'lum'
                status_text = '✅ O\'tdi' if result.percentage >= (test.passing_score or 0) else '❌ O\'tmadi'
                questions_count = len(result.answers_data.get('answers', [])) if result.answers_data else 'Noma\'lum'
                
                result_details = f"""
📊 Batafsil test natijasi

📋 Test: {test.title}
📅 Sana: {date_str}

📈 Natijalar:
• Ball: {result.score}/{result.max_score}
• Foiz: {result.percentage:.1f}%
• Holat: {status_text}

🎯 Test ma'lumotlari:
• O'tish balli: {test.passing_score or 'Aniqlanmagan'}%
• Savollar soni: {questions_count}
                """
                
                keyboard = [
                    [InlineKeyboardButton("📝 Boshqa test", callback_data="available_tests")],
                    [InlineKeyboardButton("📊 Barcha natijalar", callback_data="my_results")],
    
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(result_details, reply_markup=reply_markup)
                
            finally:
                self.bot.test_service.db.close_session(session)
                
        except Exception as e:
            await query.edit_message_text(f"❌ Natijani olishda xatolik: {str(e)}")
    
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
    
    async def start_test_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_id: int):
        """Testni boshlash callback"""
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
        
        if 'error' in test_session:
            await query.edit_message_text(f"❌ {test_session['error']}")
            return
        
        # Test ma'lumotlarini context ga saqlash
        context.user_data['current_test'] = {
            'test_id': test_id,
            'session_id': test_session['session_id'],
            'current_question': 0,
            'answers': {},
            'start_time': test_session['started_at'],
            'test_title': test.title
        }
        
        # Test ishlash holatini context ga saqlash
        context.user_data['taking_test'] = True
        
        # Test boshlash xabarini yuborish
        test_questions = await self.bot.test_service.get_test_questions(test_id)
        questions_count = len(test_questions)
        
        start_message = f"""
🚀 Test boshlanmoqda!

📋 Test: {test.title}
📊 Savollar soni: {questions_count}
⏱️ Vaqt chegarasi: {test.time_limit or "Cheklanmagan"} daqiqa

💡 Javoblarni quyidagi formatda kiriting:
• ABCDABCD... (katta harflar)
• abcdabcd... (kichik harflar)
• 1A2B3C4D... (raqam + katta harf)
• 1a2b3c4d... (raqam + kichik harf)

📝 Misol: abcdabcdabcd

🔽 Quyida javoblaringizni kiriting:
        """
        
        await query.edit_message_text(start_message)
    
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
