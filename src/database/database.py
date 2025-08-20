from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_bot.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Database:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_tables(self):
        """Barcha jadvallarni yaratish"""
        # Barcha modellarni import qilish
        from src.models.user import User
        from src.models.test import Test, Question, Answer
        from src.models.result import TestResult
        from src.models.test_types import TestTemplate
        
        # Barcha jadvallarni yaratish
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Database sessiyasini olish"""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Database sessiyasini yopish"""
        session.close()
