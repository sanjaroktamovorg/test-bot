from telegram import Update
from telegram.ext import ContextTypes
from src.models import UserRole
from src.bot.keyboards import KeyboardFactory

class CallbackHandlers:
    """Callback handerlari"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tugma bosish handerlari"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "register":
            await self.bot.command_handlers.register_command(update, context)
        elif query.data.startswith("role_"):
            role = query.data.split("_")[1]
            await self._set_user_role(query, role)
        elif query.data.startswith("take_test_"):
            test_id = int(query.data.split("_")[2])
            await self._start_test(query, test_id)
        elif query.data == "back_to_menu":
            await self._back_to_menu(query, context)
        elif query.data.startswith("view_result_"):
            result_id = int(query.data.split("_")[2])
            await self._view_result(query, result_id)
    
    async def _set_user_role(self, query, role):
        """Foydalanuvchi roli o'rnatish"""
        user = query.from_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if db_user:
            user_role = UserRole.TEACHER if role == "teacher" else UserRole.STUDENT
            await self.bot.user_service.update_user_role(db_user.id, user_role)
            
            role_text = "👨‍🏫 O'qituvchi" if role == "teacher" else "👨‍🎓 O'quvchi"
            await query.edit_message_text(f"✅ Rolingiz o'rnatildi: {role_text}")
            
            # Asosiy menyuni ko'rsatish
            keyboard = KeyboardFactory.get_main_keyboard(user_role)
            await query.message.reply_text("🏠 Asosiy menyu:", reply_markup=keyboard)
    
    async def _start_test(self, query, test_id):
        """Testni boshlash"""
        user = query.from_user
        db_user = await self.bot.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.STUDENT:
            await query.edit_message_text("❌ Bu funksiya faqat o'quvchilar uchun!")
            return
        
        # Testni boshlash logikasi
        await query.edit_message_text(f"📝 Test boshlanmoqda... Test ID: {test_id}")
    
    async def _back_to_menu(self, query, context):
        """Menyuga qaytish"""
        await self.bot.command_handlers.menu_command(context, context)
    
    async def _view_result(self, query, result_id):
        """Natijani ko'rish"""
        await query.edit_message_text(f"📊 Natija ko'rish... Result ID: {result_id}")
