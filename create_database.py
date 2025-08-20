#!/usr/bin/env python3
"""
Database yaratish scripti
"""

import os
import sys
from dotenv import load_dotenv
from src.database import Database
from src.models.user import User, UserRole
from src.models.test import Test, Question, Answer
from src.models.result import TestResult

def create_database():
    """Database va jadvallarni yaratish"""
    load_dotenv()
    
    try:
        db = Database()
        db.create_tables()
        print("✅ Database jadvallari muvaffaqiyatli yaratildi!")
        
        # Test ma'lumotlari qo'shish
        session = db.get_session()
        
        # Admin foydalanuvchi yaratish
        admin_user = User(
            telegram_id=123456789,
            username="admin",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN
        )
        
        session.add(admin_user)
        session.commit()
        print("✅ Test foydalanuvchi yaratildi!")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
