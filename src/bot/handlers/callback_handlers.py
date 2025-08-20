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
        elif data.startswith("view_result_"):
            result_id = int(data.split("_")[2])
            await self.view_result_callback(update, context, result_id)
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
        
        reply_markup = KeyboardFactory.get_main_keyboard(user_role)
        await query.edit_message_text(menu_text, reply_markup=reply_markup)
    
    async def take_test_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, test_id: int):
        """Test ishlash callback"""
        query = update.callback_query
        await query.edit_message_text("📝 Test ishlash funksiyasi ishlab chiqilmoqda...")
    
    async def view_result_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, result_id: int):
        """Natija ko'rish callback"""
        query = update.callback_query
        await query.edit_message_text("📊 Natija ko'rish funksiyasi ishlab chiqilmoqda...")
