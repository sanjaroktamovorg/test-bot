import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv
from src.database import Database
from src.services.user_service import UserService
from src.services.test_service import TestService
from src.services.test_creation_service import TestCreationService
from src.services.test_taking_service import TestTakingService
from src.bot.handlers import CommandHandlers, MessageHandlers, CallbackHandlers

load_dotenv()

class TestBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN topilmadi!")
        
        # Database va servislar
        self.db = Database()
        self.user_service = UserService(self.db)
        self.test_service = TestService(self.db)
        self.test_creation_service = TestCreationService(self.db)
        self.test_taking_service = TestTakingService(self.db)
        
        # Handlerlar
        self.command_handlers = CommandHandlers(self)
        self.message_handlers = MessageHandlers(self)
        self.callback_handlers = CallbackHandlers(self)
        
        # Bot yaratish
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Bot handerlarni sozlash"""
        # Asosiy komandalar
        self.application.add_handler(CommandHandler("start", self.command_handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.command_handlers.help_command))
        self.application.add_handler(CommandHandler("register", self.command_handlers.register_command))
        self.application.add_handler(CommandHandler("menu", self.command_handlers.menu_command))
        
        # O'qituvchi komandalari
        self.application.add_handler(CommandHandler("create_test", self.message_handlers.create_test_command))
        self.application.add_handler(CommandHandler("my_tests", self.message_handlers.my_tests_command))
        self.application.add_handler(CommandHandler("results", self.message_handlers.results_command))
        
        # O'quvchi komandalari
        self.application.add_handler(CommandHandler("available_tests", self.message_handlers.available_tests_command))
        self.application.add_handler(CommandHandler("my_results", self.message_handlers.my_results_command))
        
        # Callback handerlari
        self.application.add_handler(CallbackQueryHandler(self.callback_handlers.handle_callback))
        
        # Xabar handerlari
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handlers.handle_message))
    
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
