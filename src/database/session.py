from .database import SessionLocal

def get_db():
    """Database sessiyasini olish uchun dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
