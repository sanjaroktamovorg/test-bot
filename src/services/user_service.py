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
            
            # Foydalanuvchi sozlamalarini yaratish - User jadvalidagi rol bilan sinxronlash
            user_settings = UserSettings(
                user_id=new_user.id,
                telegram_id=telegram_id,
                role=new_user.role.value  # User jadvalidagi rol bilan bir xil
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
    
    async def get_user_by_id(self, user_id: int) -> User:
        """ID bo'yicha foydalanuvchini olish"""
        session = self.db.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
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
        """Foydalanuvchi roli o'zgartirish - har ikki jadvalda ham yangilash"""
        session = self.db.get_session()
        try:
            # User jadvalini yangilash
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                return False
            
            user.role = role
            
            # UserSettings ni yangilash
            user_settings = session.query(UserSettings).filter(UserSettings.telegram_id == telegram_id).first()
            if user_settings:
                user_settings.role = role.value
            else:
                # Agar UserSettings mavjud bo'lmasa, yaratish
                user_settings = UserSettings(
                    user_id=user.id,
                    telegram_id=telegram_id,
                    role=role.value
                )
                session.add(user_settings)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def get_user_role(self, telegram_id: int) -> UserRole:
        """Foydalanuvchi roli olish - User jadvalidan asosiy manba sifatida"""
        session = self.db.get_session()
        try:
            # Avval User jadvalidan tekshirish (asosiy manba)
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user and user.role:
                return user.role
            
            # Agar User jadvalida topilmasa, UserSettings dan tekshirish
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
    
    async def update_profile_field(self, telegram_id: int, field: str, value) -> bool:
        """Profil maydonini yangilash"""
        session = self.db.get_session()
        try:
            user_settings = session.query(UserSettings).filter(UserSettings.telegram_id == telegram_id).first()
            if user_settings and hasattr(user_settings, field):
                setattr(user_settings, field, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def get_profile_data(self, telegram_id: int) -> dict:
        """Profil ma'lumotlarini olish"""
        session = self.db.get_session()
        try:
            user_settings = session.query(UserSettings).filter(UserSettings.telegram_id == telegram_id).first()
            if user_settings:
                return {
                    'profile_photo': user_settings.profile_photo,
                    'full_name': user_settings.full_name,
                    'age': user_settings.age,
                    'about': user_settings.about,
                    'experience': user_settings.experience,
                    'specialization': user_settings.specialization
                }
            return {}
        finally:
            self.db.close_session(session)
    
    async def get_full_name(self, telegram_id: int) -> str:
        """Foydalanuvchining to'liq ismini olish"""
        session = self.db.get_session()
        try:
            # Avval UserSettings dan full_name ni tekshirish
            user_settings = session.query(UserSettings).filter(UserSettings.telegram_id == telegram_id).first()
            if user_settings and user_settings.full_name:
                return user_settings.full_name
            
            # Agar full_name yo'q bo'lsa, User jadvalidan first_name va last_name ni olish
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                if user.first_name and user.last_name:
                    return f"{user.first_name} {user.last_name}"
                elif user.first_name:
                    return user.first_name
                elif user.last_name:
                    return user.last_name
            
            return "Foydalanuvchi"
        finally:
            self.db.close_session(session)
    
    async def sync_user_roles(self) -> dict:
        """User va UserSettings jadvallaridagi rollarni sinxronlashtirish"""
        session = self.db.get_session()
        try:
            # Barcha foydalanuvchilarni olish
            users = session.query(User).all()
            synced_count = 0
            errors = []
            
            for user in users:
                try:
                    # UserSettings ni topish yoki yaratish
                    user_settings = session.query(UserSettings).filter(
                        UserSettings.telegram_id == user.telegram_id
                    ).first()
                    
                    if user_settings:
                        # Agar UserSettings mavjud bo'lsa, User jadvalidagi rol bilan yangilash
                        if user_settings.role != user.role.value:
                            user_settings.role = user.role.value
                            synced_count += 1
                    else:
                        # Agar UserSettings mavjud bo'lmasa, yaratish
                        user_settings = UserSettings(
                            user_id=user.id,
                            telegram_id=user.telegram_id,
                            role=user.role.value
                        )
                        session.add(user_settings)
                        synced_count += 1
                        
                except Exception as e:
                    errors.append(f"User ID {user.id}: {str(e)}")
            
            session.commit()
            return {
                "success": True,
                "synced_count": synced_count,
                "total_users": len(users),
                "errors": errors
            }
            
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "error": str(e),
                "synced_count": 0,
                "total_users": 0,
                "errors": []
            }
        finally:
            self.db.close_session(session)
