from sqlalchemy.orm import Session
from src.models import User, UserRole
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
    
    async def update_user_role(self, user_id: int, role: UserRole) -> bool:
        """Foydalanuvchi roli o'zgartirish"""
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.role = role
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
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
