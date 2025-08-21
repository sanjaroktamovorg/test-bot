from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.models import UserRole
from src.bot.keyboards import KeyboardFactory
import time
from datetime import datetime

class CallbackHandlers:
    """Callback handerlari"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback handerlari"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "role_teacher":
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
        elif data == "main_menu":
            await self.main_menu_callback(update, context)
        
        # Inline test answer callbacks
        elif data.startswith("answer_"):
            # Format: answer_{question_id}_{option}
            parts = data.split("_")
            question_id = int(parts[1])
            option = parts[2]
            await self.handle_inline_answer(update, context, question_id, option)
        elif data.startswith("test_page_"):
            # Format: test_page_{test_id}_{page}
            parts = data.split("_")
            test_id = int(parts[2])
            page = int(parts[3])
            await self.show_test_page(update, context, test_id, page)
        elif data.startswith("finish_inline_test_"):
            test_id = int(data.split("_")[3])
            await self.finish_inline_test(update, context, test_id)
        elif data.startswith("use_text_mode_"):
            test_id = int(data.split("_")[3])
            await self.switch_to_text_mode(update, context, test_id)
        
        # Test yaratish callbacks
        elif data.startswith("create_test_type_"):
            test_type = data.split("_")[3]
            await self.handle_test_type_selection(update, context, test_type)
        elif data.startswith("create_test_category_"):
            category = data.split("_")[3]
            await self.handle_test_category_selection(update, context, category)
        elif data.startswith("create_test_subject_"):
            subject = data.split("_")[3]
            await self.handle_test_subject_selection(update, context, subject)
        elif data.startswith("create_test_time_"):
            time_limit = int(data.split("_")[3])
            await self.handle_test_time_selection(update, context, time_limit)
        elif data.startswith("create_test_score_"):
            passing_score = int(data.split("_")[3])
            await self.handle_test_score_selection(update, context, passing_score)
        elif data == "create_test_finish":
            await self.handle_test_finish(update, context)
        elif data == "create_test_cancel":
            await self.handle_test_cancel(update, context)
        
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
        
        # Rol nomini alohida aniqlash
        role_name = '👨‍🏫 O\'qituvchi' if user_role == UserRole.TEACHER else '👨‍🎓 O\'quvchi'
        
        menu_text = f"""
🏠 Asosiy menyu

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: {role_name}

Asosiy menyuga qaytdingiz.
        """
        
        # Inline keyboard yaratish
        keyboard = [
            [InlineKeyboardButton("🏠 Asosiy menyu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(menu_text, reply_markup=reply_markup)
    
    async def change_role_confirm_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Rol o'zgartirishni tasdiqlash"""
        query = update.callback_query
        user = query.from_user
        
        try:
            # Foydalanuvchi ma'lumotlarini olish
            db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
            if not db_user:
                await query.edit_message_text("❌ Foydalanuvchi topilmadi!")
                return
            
            # Barcha ma'lumotlarni o'chirish
            await self.bot.user_service.delete_user_data(db_user.id)
            
            # Foydalanuvchini qayta yaratish
            await self.bot.user_service.register_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            # Rol tanlash menyusini ko'rsatish
            keyboard = [
                [InlineKeyboardButton("👨‍🏫 O'qituvchi", callback_data="role_teacher")],
                [InlineKeyboardButton("👨‍🎓 O'quvchi", callback_data="role_student")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "✅ Barcha ma'lumotlar o'chirildi!\n\nIltimos, yangi rolingizni tanlang:",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await query.edit_message_text(f"❌ Xatolik yuz berdi: {str(e)}")
    
    async def change_role_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Rol o'zgartirishni bekor qilish"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli tekshirish
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        # Rol nomini alohida aniqlash
        role_name = '👨‍🏫 O\'qituvchi' if user_role == UserRole.TEACHER else '👨‍🎓 O\'quvchi'
        
        menu_text = f"""
🏠 Asosiy menyu

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: {role_name}

Rol o'zgartirish bekor qilindi.
        """
        
        # Inline keyboard yaratish
        keyboard = [
            [InlineKeyboardButton("🏠 Asosiy menyu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(menu_text, reply_markup=reply_markup)
    

    
    async def role_teacher_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """O'qituvchi roli tanlash"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli o'zgartirish
        success = await self.bot.user_service.update_user_role(user.id, UserRole.TEACHER)
        
        if success:
            # Rol tanlash tasdiqlash xabari
            confirmation_text = f"""
✅ **Rol muvaffaqiyatli tanlandi!**

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: 👨‍🏫 O'qituvchi
📅 Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}

🎉 Tabriklaymiz! Endi siz o'qituvchi sifatida:
• 📝 Testlar yaratishingiz mumkin
• 📊 Natijalarni ko'rishingiz mumkin
• 👥 O'quvchilarni boshqarishingiz mumkin

Asosiy menyuga o'tish uchun /menu buyrug'ini yuboring.
            """
            
            await query.edit_message_text(confirmation_text, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Rol o'zgartirishda xatolik yuz berdi!")
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Asosiy menyu callback"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli tekshirish
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        # Rol nomini alohida aniqlash
        role_name = '👨‍🏫 O\'qituvchi' if user_role == UserRole.TEACHER else '👨‍🎓 O\'quvchi'
        
        menu_text = f"""
🏠 Asosiy menyu

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: {role_name}

Quyidagi tugmalardan birini tanlang:
        """
        
        # ReplyKeyboardMarkup yaratish va yangi xabar yuborish
        reply_markup = KeyboardFactory.get_main_keyboard(user_role)
        await query.message.reply_text(menu_text, reply_markup=reply_markup)
        await query.delete_message()
    
    async def role_student_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """O'quvchi roli tanlash"""
        query = update.callback_query
        user = query.from_user
        
        # Foydalanuvchi roli o'zgartirish
        success = await self.bot.user_service.update_user_role(user.id, UserRole.STUDENT)
        
        if success:
            # Rol tanlash tasdiqlash xabari
            confirmation_text = f"""
✅ **Rol muvaffaqiyatli tanlandi!**

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: 👨‍🎓 O'quvchi
📅 Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}

🎉 Tabriklaymiz! Endi siz o'quvchi sifatida:
• 📝 Mavjud testlarni ishlashingiz mumkin
• 📊 Natijalaringizni ko'rishingiz mumkin
• 🏆 Reytingda qatnashishingiz mumkin

Asosiy menyuga o'tish uchun /menu buyrug'ini yuboring.
            """
            
            await query.edit_message_text(confirmation_text, parse_mode='Markdown')
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
        
        # Inline button yoki matn tanlash
        start_message = f"""
🚀 Test boshlanmoqda!

📋 Test: {test.title}
📊 Savollar soni: {questions_count}
⏱️ Vaqt chegarasi: {test.time_limit or "Cheklanmagan"} daqiqa

📱 Qaysi usulda test ishlashni xohlaysiz?
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Inline tugmalar (Tavsiya etiladi)", callback_data=f"test_page_{test_id}_1")],
            [InlineKeyboardButton("✏️ Matn orqali (Eski usul)", callback_data=f"use_text_mode_{test_id}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="available_tests")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(start_message, reply_markup=reply_markup)
    
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
    
    async def search_page_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, page: int):
        """Test qidirish sahifasi navigatsiyasi"""
        query = update.callback_query
        
        try:
            # Testlarni olish
            limit = 10
            offset = (page - 1) * limit
            tests = await self.bot.test_service.search_public_tests_by_title(title, limit, offset)
            total_count = await self.bot.test_service.count_public_tests_by_title(title)
            
            if not tests:
                await query.edit_message_text("❌ Testlar topilmadi!")
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
            await query.edit_message_text(tests_text, reply_markup=reply_markup)
            
        except Exception as e:
            await query.edit_message_text(f"❌ Xatolik: {str(e)}")
    
    # ====== INLINE TEST ANSWER HANDLERS ======
    
    async def show_test_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_id: int, page: int):
        """Test sahifasini ko'rsatish (10 talik guruhlar)"""
        query = update.callback_query
        
        # Test ma'lumotlarini olish
        test = await self.bot.test_service.get_test_by_id(test_id)
        if not test:
            await query.edit_message_text("❌ Test topilmadi!")
            return
        
        # Test savollarini olish
        test_questions = await self.bot.test_service.get_test_questions(test_id)
        questions_count = len(test_questions)
        
        # Sahifa parametrlarini hisoblash
        questions_per_page = 10
        total_pages = (questions_count + questions_per_page - 1) // questions_per_page
        
        if page < 1 or page > total_pages:
            page = 1
        
        start_idx = (page - 1) * questions_per_page
        end_idx = min(start_idx + questions_per_page, questions_count)
        
        # Context dan javoblarni olish
        current_test = context.user_data.get('current_test', {})
        inline_answers = current_test.get('inline_answers', {})
        
        # Sahifa matnini yaratish
        message_text = f"""
📋 Test: {test.title}
📄 Sahifa: {page}/{total_pages} ({start_idx + 1}-{end_idx} savollar)

"""
        
        # Savollarni ko'rsatish
        keyboard = []
        for i in range(start_idx, end_idx):
            question_num = i + 1
            message_text += f"❓ SAVOL {question_num}\n"
            
            # Javob tugmalarini yaratish
            row = []
            for option in ['A', 'B', 'C', 'D']:
                selected = inline_answers.get(str(i), '') == option
                button_text = f"✅{option}" if selected else option
                callback_data = f"answer_{i}_{option}"
                row.append(InlineKeyboardButton(button_text, callback_data=callback_data))
            keyboard.append(row)
            
            message_text += "\n"
        
        # Navigatsiya tugmalarini qo'shish
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi 10 ta", callback_data=f"test_page_{test_id}_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️ Keyingi 10 ta", callback_data=f"test_page_{test_id}_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Boshqaruv tugmalari
        control_buttons = []
        answered_count = len(inline_answers)
        if answered_count == questions_count:
            control_buttons.append(InlineKeyboardButton("✅ Testni tugatish", callback_data=f"finish_inline_test_{test_id}"))
        
        control_buttons.append(InlineKeyboardButton("✏️ Matn usuli", callback_data=f"use_text_mode_{test_id}"))
        control_buttons.append(InlineKeyboardButton("🔙 Orqaga", callback_data="available_tests"))
        keyboard.append(control_buttons)
        
        # Progress barni qo'shish
        progress_text = f"\n📊 Javob berilgan: {answered_count}/{questions_count}"
        if answered_count > 0:
            progress_percent = (answered_count / questions_count) * 100
            progress_text += f" ({progress_percent:.1f}%)"
        
        message_text += progress_text
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message_text, reply_markup=reply_markup)
    
    async def handle_inline_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, question_id: int, option: str):
        """Inline javobni qayta ishlash"""
        query = update.callback_query
        
        # Context dan test ma'lumotlarini olish
        current_test = context.user_data.get('current_test', {})
        if not current_test:
            await query.answer("❌ Test sessiyasi topilmadi!")
            return
        
        test_id = current_test.get('test_id')
        if not test_id:
            await query.answer("❌ Test ma'lumotlari topilmadi!")
            return
        
        # Javobni saqlash
        if 'inline_answers' not in current_test:
            current_test['inline_answers'] = {}
        
        current_test['inline_answers'][str(question_id)] = option
        context.user_data['current_test'] = current_test
        
        # Joriy sahifani aniqlash
        questions_per_page = 10
        current_page = (question_id // questions_per_page) + 1
        
        # Sahifani qayta ko'rsatish
        await self.show_test_page(update, context, test_id, current_page)
        
        # Foydalanuvchiga javob berish
        await query.answer(f"✅ {question_id + 1}-savol uchun {option} tanlandi")
    
    async def finish_inline_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_id: int):
        """Inline testni tugatish"""
        query = update.callback_query
        user = query.from_user
        
        # Context dan test ma'lumotlarini olish
        current_test = context.user_data.get('current_test', {})
        inline_answers = current_test.get('inline_answers', {})
        
        if not inline_answers:
            await query.answer("❌ Hech qanday javob berilmagan!")
            return
        
        # Test ma'lumotlarini olish
        test = await self.bot.test_service.get_test_by_id(test_id)
        test_questions = await self.bot.test_service.get_test_questions(test_id)
        questions_count = len(test_questions)
        
        # Barcha savollarga javob berilganligini tekshirish
        if len(inline_answers) != questions_count:
            missing_count = questions_count - len(inline_answers)
            await query.answer(f"❌ {missing_count} ta savolga javob berilmagan!")
            return
        
        try:
            # Foydalanuvchi ma'lumotlarini olish
            db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
            
            # Javoblarni test_taking_service formatiga o'tkazish
            answers_dict = {}
            for i in range(questions_count):
                question = test_questions[i]
                user_answer = inline_answers.get(str(i), '')
                
                # Javob variantlarini olish
                question_answers = await self.bot.test_service.get_question_answers(question.id)
                
                # User answer (A, B, C, D) ni answer_id ga o'tkazish
                for answer in question_answers:
                    answer_letter = answer.answer_text.replace('Variant ', '').strip()
                    if answer_letter.upper() == user_answer.upper():
                        answers_dict[str(question.id)] = str(answer.id)
                        break
            
            # Testni tugatish
            result = await self.bot.test_taking_service.submit_test_answers(
                test_id, db_user.id, answers_dict
            )
            
            # Test ishlash holatini to'xtatish
            context.user_data['taking_test'] = False
            context.user_data['current_test'] = {}
            
            # Natijani ko'rsatish
            passed = result.percentage >= (test.passing_score or 0)
            result_emoji = "🎉" if passed else "😔"
            result_text = "Tabriklaymiz! Testni o'tdingiz!" if passed else "Afsus! Testni o'ta olmadingiz."
            
            final_message = f"""
{result_emoji} Test tugatildi!

📋 Test: {test.title}
📊 Savollar soni: {questions_count}
✅ To'g'ri javoblar: {int(result.score)}/{int(result.max_score)}
📈 Ball: {result.score}/{result.max_score}
📊 Foiz: {result.percentage:.1f}%

🎯 O'tish balli: {test.passing_score or 'Aniqlanmagan'}%
{result_text}
            """
            
            keyboard = [
                [InlineKeyboardButton("📊 Batafsil natija", callback_data=f"view_result_{result.id}")],
                [InlineKeyboardButton("📝 Boshqa test", callback_data="available_tests")],
                [InlineKeyboardButton("🏠 Asosiy menyu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(final_message, reply_markup=reply_markup)
            
        except Exception as e:
            await query.edit_message_text(f"❌ Test tugatishda xatolik: {str(e)}")
    
    async def switch_to_text_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_id: int):
        """Matn usulga o'tish"""
        query = update.callback_query
        
        # Test ma'lumotlarini olish
        test = await self.bot.test_service.get_test_by_id(test_id)
        test_questions = await self.bot.test_service.get_test_questions(test_id)
        questions_count = len(test_questions)
        
        text_message = f"""
✏️ Matn usuli tanlandi!

📋 Test: {test.title}
📊 Savollar soni: {questions_count}

💡 Javoblarni quyidagi formatda kiriting:
• ABCDABCD... (katta harflar)
• abcdabcd... (kichik harflar)
• 1A2B3C4D... (raqam + katta harf)
• 1a2b3c4d... (raqam + kichik harf)

📝 Misol: abcdabcdabcd

🔽 Quyida javoblaringizni kiriting:
        """
        
        await query.edit_message_text(text_message)
    
    # Test yaratish callback funksiyalari
    async def handle_test_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_type: str):
        """Test turi tanlash - inline button"""
        query = update.callback_query
        from src.models.test_types import TestType
        
        test_type_map = {
            'simple': TestType.SIMPLE,
            'dtm': TestType.DTM,
            'national_cert': TestType.NATIONAL_CERT,
            'open': TestType.OPEN
        }
        
        if test_type in test_type_map:
            context.user_data['test_data']['test_type'] = test_type_map[test_type].value
            
            if test_type == 'simple':
                # Oddiy test uchun toifa tanlash
                text = "📝 Oddiy test yaratish uchun toifani tanlang:"
                keyboard = [
                    [InlineKeyboardButton("🌍 Ommaviy test", callback_data="create_test_category_public")],
                    [InlineKeyboardButton("🔒 Shaxsiy test", callback_data="create_test_category_private")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(text, reply_markup=reply_markup)
            else:
                # Boshqa test turlari uchun xabar
                text = f"🚧 {test_type} yaratish funksiyasi ishlab chiqilmoqda!\n\nIltimos, oddiy test yaratishni sinab ko'ring."
                keyboard = [
                    [InlineKeyboardButton("🔙 Orqaga", callback_data="create_test_cancel")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def handle_test_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
        """Test toifasi tanlash - inline button"""
        query = update.callback_query
        from src.models.test_types import TestCategory
        
        category_map = {
            'public': TestCategory.PUBLIC,
            'private': TestCategory.PRIVATE
        }
        
        if category in category_map:
            context.user_data['test_data']['category'] = category_map[category].value
            
            # Fan tanlash
            text = "📚 Test fani uchun mutaxassislikni tanlang:"
            keyboard = [
                [InlineKeyboardButton("📐 Matematika", callback_data="create_test_subject_math")],
                [InlineKeyboardButton("🔬 Fizika", callback_data="create_test_subject_physics")],
                [InlineKeyboardButton("🧪 Kimyo", callback_data="create_test_subject_chemistry")],
                [InlineKeyboardButton("🌍 Tarix", callback_data="create_test_subject_history")],
                [InlineKeyboardButton("🌱 Biologiya", callback_data="create_test_subject_biology")],
                [InlineKeyboardButton("🌐 Ingliz tili", callback_data="create_test_subject_english")],
                [InlineKeyboardButton("📖 O'zbek tili", callback_data="create_test_subject_uzbek")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="create_test_type_simple")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def handle_test_subject_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, subject: str):
        """Test fani tanlash - inline button"""
        query = update.callback_query
        
        subject_map = {
            'math': 'Matematika',
            'physics': 'Fizika',
            'chemistry': 'Kimyo',
            'history': 'Tarix',
            'biology': 'Biologiya',
            'english': 'Ingliz tili',
            'uzbek': 'O\'zbek tili'
        }
        
        if subject in subject_map:
            context.user_data['test_data']['subject'] = subject_map[subject]
            
            # Vaqt chegarasi tanlash
            text = "⏱️ Test uchun vaqt chegarasini tanlang:"
            keyboard = [
                [InlineKeyboardButton("15 daqiqa", callback_data="create_test_time_15")],
                [InlineKeyboardButton("30 daqiqa", callback_data="create_test_time_30")],
                [InlineKeyboardButton("45 daqiqa", callback_data="create_test_time_45")],
                [InlineKeyboardButton("60 daqiqa", callback_data="create_test_time_60")],
                [InlineKeyboardButton("90 daqiqa", callback_data="create_test_time_90")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="create_test_category_public")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def handle_test_time_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, time_limit: int):
        """Test vaqti tanlash - inline button"""
        query = update.callback_query
        
        context.user_data['test_data']['time_limit'] = time_limit
        
        # O'tish balli tanlash
        text = "🎯 Test uchun o'tish ballini tanlang:"
        keyboard = [
            [InlineKeyboardButton("50%", callback_data="create_test_score_50")],
            [InlineKeyboardButton("60%", callback_data="create_test_score_60")],
            [InlineKeyboardButton("70%", callback_data="create_test_score_70")],
            [InlineKeyboardButton("80%", callback_data="create_test_score_80")],
            [InlineKeyboardButton("90%", callback_data="create_test_score_90")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="create_test_subject_math")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def handle_test_score_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, passing_score: int):
        """O'tish balli tanlash - inline button"""
        query = update.callback_query
        
        context.user_data['test_data']['passing_score'] = passing_score
        
        # Test nomini kiritish so'raladi
        text = "📝 Endi test nomini kiriting:\n\nMisol: Algebra testi, Fizika testi, Tarix testi..."
        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="create_test_time_30")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
        
        # Test nomini kiritish holatini o'rnatish
        context.user_data['creating_test'] = True
        context.user_data['test_creation_step'] = 'enter_title'
    
    async def handle_test_finish(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test yaratishni tugatish"""
        query = update.callback_query
        
        # Test ma'lumotlarini ko'rsatish
        test_data = context.user_data.get('test_data', {})
        
        text = f"""
✅ Test ma'lumotlari tayyor!

📝 Nomi: {test_data.get('title', 'Noma\'lum')}
📚 Fan: {test_data.get('subject', 'Aniqlanmagan')}
⏱️ Vaqt: {test_data.get('time_limit', 30)} daqiqa
🎯 O'tish balli: {test_data.get('passing_score', 60)}%
📂 Toifa: {'Ommaviy' if test_data.get('category') == 'public' else 'Shaxsiy'}

Testni yaratishni xohlaysizmi?
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Testni yaratish", callback_data="create_test_confirm")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data="create_test_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    async def handle_test_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test yaratishni bekor qilish"""
        query = update.callback_query
        
        # Barcha test yaratish holatlarini tozalash
        context.user_data['creating_test'] = False
        context.user_data['test_creation_step'] = None
        context.user_data['test_data'] = {}
        
        text = "❌ Test yaratish bekor qilindi."
        keyboard = [
            [InlineKeyboardButton("🏠 Asosiy menyu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
