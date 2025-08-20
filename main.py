#!/usr/bin/env python3
"""
Test Bot - Asosiy dastur
"""

import os
import sys
import logging
from dotenv import load_dotenv
from src.bot import TestBot
from src.database import Database

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_database():
    """Database ni sozlash"""
    try:
        db = Database()
        db.create_tables()
        logger.info("Database jadvallari yaratildi")
        return db
    except Exception as e:
        logger.error(f"Database sozlashda xatolik: {e}")
        raise

def main():
    """Asosiy dastur"""
    # Environment faylini yuklash
    load_dotenv()
    
    # Logs papkasini yaratish
    os.makedirs('logs', exist_ok=True)
    
    try:
        # Database ni sozlash
        db = setup_database()
        
        # Bot yaratish
        bot = TestBot()
        
        # Botni ishga tushirish
        logger.info("Test Bot ishga tushirilmoqda...")
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
