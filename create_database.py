#!/usr/bin/env python3
"""
Database yaratish scripti
"""

import os
import sys
from dotenv import load_dotenv
from src.database import Database

def create_database():
    """Database va jadvallarni yaratish"""
    load_dotenv()
    
    try:
        db = Database()
        db.create_tables()
        print("✅ Database jadvallari muvaffaqiyatli yaratildi!")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
