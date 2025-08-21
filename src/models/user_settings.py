from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.database import Base

class UserSettings(Base):
    """Foydalanuvchi sozlamalari"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Telegram ID - har bir foydalanuvchi uchun alohida
    telegram_id = Column(Integer, nullable=False, unique=True)
    
    # Foydalanuvchi roli - har bir akkaunt uchun alohida
    role = Column(String(20), nullable=False, default="student")  # student, teacher, admin
    
    # Qo'shimcha sozlamalar
    language = Column(String(10), default="uz")  # til
    theme = Column(String(20), default="light")  # tema
    notifications = Column(Boolean, default=True)  # bildirishnomalar
    
    # Test yaratish sozlamalari (o'qituvchilar uchun)
    default_test_type = Column(String(20), default="simple")
    default_test_category = Column(String(20), default="public")
    default_subject = Column(String(50), nullable=True)
    
    # Test ishlash sozlamalari (o'quvchilar uchun)
    auto_submit = Column(Boolean, default=False)  # avtomatik topshirish
    show_results_immediately = Column(Boolean, default=True)  # natijani darhol ko'rsatish
    
    # Profil ma'lumotlari
    profile_photo = Column(String(500), nullable=True)  # profil rasmi URL
    full_name = Column(String(100), nullable=True)  # to'liq ism-familya
    age = Column(Integer, nullable=True)  # yosh
    about = Column(Text, nullable=True)  # haqida (o'qituvchilar uchun)
    experience = Column(Integer, nullable=True)  # tajriba yillari (o'qituvchilar uchun)
    specialization = Column(String(100), nullable=True)  # mutaxassislik fani (o'qituvchilar uchun)
    
    # Vaqt sozlamalari
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="settings")
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, telegram_id={self.telegram_id}, role={self.role})>"
