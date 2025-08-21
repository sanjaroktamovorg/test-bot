from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.models import UserRole
from src.bot.keyboards import KeyboardFactory

class CommandHandlers:
    """Asosiy komanda handerlari"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komandasi"""
        user = update.effective_user
        
        # Foydalanuvchini tekshirish
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            # Ro'yxatdan o'tmagan foydalanuvchi - avtomatik ro'yxatdan o'tkazish
            db_user = await self.bot.user_service.register_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            if db_user:
                welcome_text = f"""
🎓 Test Bot ga xush kelibsiz, {user.first_name}!

Bu bot orqali:
📝 O'qituvchilar testlar tuzishi
📊 O'quvchilar testlarni ishlashi
📈 Natijalarni ko'rish mumkin

⚠️ **Muhim:** Rolingizni tanlaganingizdan so'ng uni o'zgartirib bo'lmaydi!

Iltimos, rolingizni tanlang:
                """
                
                keyboard = [
                    [InlineKeyboardButton("👨‍🏫 O'qituvchi", callback_data="role_teacher")],
                    [InlineKeyboardButton("👨‍🎓 O'quvchi", callback_data="role_student")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Ro'yxatdan o'tishda xatolik yuz berdi!")
        else:
            # Ro'yxatdan o'tgan foydalanuvchi - to'g'ridan-to'g'ri dashboard
            await self.menu_command(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yordam komandasi"""
        help_text = """
🤖 Test Bot - Yordam

📋 Mavjud komandalar:

👤 Umumiy:
/start - Botni ishga tushirish
/help - Yordam
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
    

    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Asosiy menyu - har bir foydalanuvchi uchun alohida"""
        user = update.effective_user
        
        # Foydalanuvchi sozlamalarini olish
        user_role = await self.bot.user_service.get_user_role(user.id)
        
        if not user_role:
            await update.message.reply_text("❌ Avval ro'yxatdan o'ting! /register")
            return
        
        role_text = "👨‍🏫 O'qituvchi" if user_role == UserRole.TEACHER else "👨‍🎓 O'quvchi"
        dashboard_title = "O'qituvchi Dashboard" if user_role == UserRole.TEACHER else "O'quvchi Dashboard"
        
        menu_text = f"""
🏠 {dashboard_title}

👤 Foydalanuvchi: {user.first_name}
🎭 Rol: {role_text}
🆔 Telegram ID: {user.id}

Quyidagi tugmalardan birini tanlang:
        """
        
        reply_markup = KeyboardFactory.get_main_keyboard(user_role)
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    
    async def version_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Versiya komandasi"""
        version_text = """
🤖 Test Bot - Versiya ma'lumotlari

            📋 Versiya: v0.9.31
📅 Yangilangan: 2025-01-27
👨‍💻 Developer: Test Bot Team

            🆕 So'nggi o'zgarishlar:
            • Asosiy menular soddalashtirildi
            • O'quvchilar va o'qituvchilar uchun minimal menu
            • Ortiqcha tugmalar olib tashlandi
            • Foydalanuvchi tajribasi yaxshilandi
            • Bot interfeysi optimallashtirildi

🔧 Texnik ma'lumotlar:
• Python 3.10+
• python-telegram-bot 20.7
• SQLAlchemy 2.0.23
• SQLite Database

📞 Yordam uchun: /help
        """
        await update.message.reply_text(version_text)