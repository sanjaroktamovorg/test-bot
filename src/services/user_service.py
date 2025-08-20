from sqlalchemy.orm import Session
from src.models import User, UserRole, UserSettings
from src.database import Database

class UserService:
    def __init__(self, db: Database):
        self.db = db
    
    async def register_user(self, telegram_id: int, username: str = None, 
                          first_name: str = None, last_name: str = None) -> User:
        """Foydalanuvchini ro'yxatdan o'tkazish"""
        session = self.db.get_session()
        try:
            # Foydalanuvchi mavjudligini tekshirish
            existing_user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if existing_user:
                return existing_user
            
            # Yangi foydalanuvchi yaratish
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.STUDENT  # Default rol
            )
            
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            # Foydalanuvchi sozlamalarini yaratish
            user_settings = UserSettings(
                user_id=new_user.id,
                telegram_id=telegram_id,
                role=UserRole.STUDENT.value
            )
            
            session.add(user_settings)
            session.commit()
            
            return new_user
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """Telegram ID bo'yicha foydalanuvchini olish"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.telegram_id == telegram_id).first()
        finally:
            self.db.close_session(session)
    
    async def get_user_settings(self, telegram_id: int) -> UserSettings:
        """Foydalanuvchi sozlamalarini olish"""
        session = self.db.get_session()
        try:
            return session.query(UserSettings).filter(UserSettings.telegram_id == telegram_id).first()
        finally:
            self.db.close_session(session)
    
    async def update_user_role(self, telegram_id: int, role: UserRole) -> bool:
        """Foydalanuvchi roli o'zgartirish - har bir akkaunt uchun alohida"""
        session = self.db.get_session()
        try:
            # UserSettings ni yangilash
            user_settings = session.query(UserSettings).filter(UserSettings.telegram_id == telegram_id).first()
            if user_settings:
                user_settings.role = role.value
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def get_user_role(self, telegram_id: int) -> UserRole:
        """Foydalanuvchi roli olish - har bir akkaunt uchun alohida"""
        session = self.db.get_session()
        try:
            user_settings = session.query(UserSettings).filter(UserSettings.telegram_id == telegram_id).first()
            if user_settings:
                return UserRole(user_settings.role)
            return UserRole.STUDENT  # Default
        finally:
            self.db.close_session(session)
    
    async def get_all_teachers(self) -> list[User]:
        """Barcha o'qituvchilarni olish"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.role == UserRole.TEACHER).all()
        finally:
            self.db.close_session(session)
    
    async def get_all_students(self) -> list[User]:
        """Barcha o'quvchilarni olish"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.role == UserRole.STUDENT).all()
        finally:
            self.db.close_session(session)
    
    async def update_user_settings(self, telegram_id: int, **kwargs) -> bool:
        """Foydalanuvchi sozlamalarini yangilash"""
        session = self.db.get_session()
        try:
            user_settings = session.query(UserSettings).filter(UserSettings.telegram_id == telegram_id).first()
            if user_settings:
                for key, value in kwargs.items():
                    if hasattr(user_settings, key):
                        setattr(user_settings, key, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
