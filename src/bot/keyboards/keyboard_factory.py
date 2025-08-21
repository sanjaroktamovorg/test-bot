from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from src.models import UserRole

class KeyboardFactory:
    """Keyboard yaratish uchun factory class"""
    
    @staticmethod
    def get_main_keyboard(user_role: UserRole):
        """Asosiy reply keyboard"""
        if user_role == UserRole.TEACHER:
            keyboard = [
                [KeyboardButton("📝 Test yaratish"), KeyboardButton("📋 Mening testlarim")],
                [KeyboardButton("📊 Natijalar"), KeyboardButton("⚙️ Sozlamalar")]
            ]
        else:  # STUDENT
            keyboard = [
                [KeyboardButton("📝 Mavjud testlar"), KeyboardButton("📊 Mening natijalarim")],
                [KeyboardButton("🏆 Reyting"), KeyboardButton("⚙️ Sozlamalar")]
            ]
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_test_type_keyboard():
        """Test turi tanlash uchun reply keyboard"""
        keyboard = [
            [KeyboardButton("📝 Oddiy test")],
            [KeyboardButton("🏛️ DTM test")],
            [KeyboardButton("🏆 Milliy sertifikat test")],
            [KeyboardButton("📖 Ochiq (variantsiz) test")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_test_category_keyboard():
        """Test toifasi tanlash uchun reply keyboard"""
        keyboard = [
            [KeyboardButton("🌍 Ommaviy test")],
            [KeyboardButton("🔒 Shaxsiy test")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_test_subject_keyboard():
        """Test fani tanlash uchun reply keyboard"""
        keyboard = [
            [KeyboardButton("📐 Matematika"), KeyboardButton("⚡ Fizika")],
            [KeyboardButton("🧪 Kimyo"), KeyboardButton("🌿 Biologiya")],
            [KeyboardButton("📚 Tarix"), KeyboardButton("🌍 Geografiya")],
            [KeyboardButton("📖 Adabiyot"), KeyboardButton("🗣️ Til")],
            [KeyboardButton("💻 Informatika"), KeyboardButton("📋 Boshqa")],
            [KeyboardButton("🔙 Orqaga")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_test_keyboard(tests):
        """Testlar uchun inline keyboard"""
        keyboard = []
        for test in tests:
            keyboard.append([InlineKeyboardButton(
                f"📝 {test.title}", 
                callback_data=f"take_test_{test.id}"
            )])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_teacher_tests_keyboard(tests):
        """O'qituvchi testlari uchun inline keyboard"""
        keyboard = []
        for test in tests:
            keyboard.append([InlineKeyboardButton(
                f"📝 {test.title}", 
                callback_data=f"view_teacher_test_{test.id}"
            )])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_results_keyboard(results):
        """Natijalar uchun inline keyboard"""
        keyboard = []
        for result in results:
            # Test ma'lumotlarini alohida olish kerak
            keyboard.append([InlineKeyboardButton(
                f"📊 Natija #{result.id} - {result.percentage:.1f}%", 
                callback_data=f"view_result_{result.id}"
            )])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_keyboard():
        """Orqaga qaytish uchun keyboard"""
        return ReplyKeyboardMarkup([[KeyboardButton("🔙 Orqaga")]], resize_keyboard=True)
