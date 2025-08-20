import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from src.database import Database
from src.models import User, UserRole
from src.services.user_service import UserService
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
        
        # Bot yaratish
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Bot handerlarni sozlash"""
        # Asosiy komandalar
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("register", self.register_command))
        
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
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komandasi"""
        user = update.effective_user
        welcome_text = f"""
🎓 Test Bot ga xush kelibsiz, {user.first_name}!

Bu bot orqali:
📝 O'qituvchilar testlar tuzishi
📊 O'quvchilar testlarni ishlashi
�� Natijalarni ko'rish mumkin

Boshlash uchun /register komandasini yuboring.
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Ro'yxatdan o'tish", callback_data="register")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yordam komandasi"""
        help_text = """
🤖 Test Bot - Yordam

📋 Mavjud komandalar:

�� Umumiy:
/start - Botni ishga tushirish
/help - Yordam
/register - Ro'yxatdan o'tish

👨‍🏫 O'qituvchilar uchun:
/create_test - Yangi test yaratish
/my_tests - Mening testlarim
/results - Test natijalari

👨‍🎓 O'quvchilar uchun:
/available_tests - Mavjud testlar
/my_results - Mening natijalarim
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
                [InlineKeyboardButton("👨‍🎓 O'quvchi", callback_data="role_student")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ Ro'yxatdan o'tdingiz! Iltimos, rolingizni tanlang:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("❌ Ro'yxatdan o'tishda xatolik yuz berdi!")
    
    async def create_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test yaratish komandasi"""
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.TEACHER:
            await update.message.reply_text("❌ Bu komanda faqat o'qituvchilar uchun!")
            return
        
        await update.message.reply_text(
            "📝 Yangi test yaratish uchun quyidagi formatda xabar yuboring:\n\n"
            "Test nomi: [Test nomi]\n"
            "Tavsif: [Test tavsifi]\n"
            "Vaqt chegarasi: [daqiqalarda]\n"
            "O'tish balli: [foizda]"
        )
        context.user_data['creating_test'] = True
    
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
        
        keyboard = [[InlineKeyboardButton(f"📝 {test.title}", callback_data=f"take_test_{test.id}")] for test in tests]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
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
    
    async def _set_user_role(self, query, role):
        """Foydalanuvchi roli o'rnatish"""
        user = query.from_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if db_user:
            user_role = UserRole.TEACHER if role == "teacher" else UserRole.STUDENT
            await self.user_service.update_user_role(db_user.id, user_role)
            
            role_text = "👨‍🏫 O'qituvchi" if role == "teacher" else "👨‍🎓 O'quvchi"
            await query.edit_message_text(f"✅ Rolingiz o'rnatildi: {role_text}")
    
    async def _start_test(self, query, test_id):
        """Testni boshlash"""
        user = query.from_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.STUDENT:
            await query.edit_message_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Testni boshlash logikasi
        await query.edit_message_text(f"📝 Test boshlanmoqda... Test ID: {test_id}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xabar handerlari"""
        user = update.effective_user
        text = update.message.text
        
        if context.user_data.get('creating_test'):
            # Test yaratish logikasi
            await update.message.reply_text("📝 Test yaratish logikasi ishlab chiqilmoqda...")
            context.user_data['creating_test'] = False
        else:
            await update.message.reply_text("❓ Tushunarsiz xabar. /help komandasi bilan yordam oling.")
    
    async def my_tests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening testlarim"""
        await update.message.reply_text("📝 Mening testlarim funksiyasi ishlab chiqilmoqda...")
    
    async def results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test natijalari"""
        await update.message.reply_text("📊 Test natijalari funksiyasi ishlab chiqilmoqda...")
    
    async def my_results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mening natijalarim"""
        await update.message.reply_text("📈 Mening natijalarim funksiyasi ishlab chiqilmoqda...")
    
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
