#!/usr/bin/env python3
"""
Test Bot sinov scripti
"""

import os
import sys
from dotenv import load_dotenv
from src.bot import TestBot

def test_bot():
    """Bot sinovini o'tkazish"""
    load_dotenv()
    
    try:
        # Bot yaratish
        bot = TestBot()
        print("✅ Bot muvaffaqiyatli yaratildi!")
        
        # Bot handerlari mavjudligini tekshirish
        handlers = bot.application.handlers
        print(f"✅ Bot handerlari: {len(handlers)} ta")
        
        # Database ulanishni tekshirish
        db = bot.db
        session = db.get_session()
        print("✅ Database ulanish muvaffaqiyatli!")
        session.close()
        
        print("\n🎉 Test Bot to'liq ishlaydi!")
        return True
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

if __name__ == "__main__":
    success = test_bot()
    sys.exit(0 if success else 1)
