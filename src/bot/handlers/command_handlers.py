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
            
            await update.message.reply_text(
                "✅ Ro'yxatdan o'tdingiz! Iltimos, rolingizni tanlang:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("❌ Ro'yxatdan o'tishda xatolik yuz berdi!")
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Asosiy menyu"""
        user = update.effective_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
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
        
        reply_markup = KeyboardFactory.get_main_keyboard(db_user.role)
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
