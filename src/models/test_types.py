from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import secrets
import string
from src.database.database import Base

class TestType(enum.Enum):
    SIMPLE = "simple"           # Oddiy test
    DTM = "dtm"                 # DTM test
    NATIONAL_CERT = "national_cert"  # Milliy sertifikat test
    OPEN = "open"               # Ochiq (variantsiz) test

class TestCategory(enum.Enum):
    PUBLIC = "public"           # Ommaviy test
    PRIVATE = "private"         # Shaxsiy test

class TestSubject(enum.Enum):
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    LITERATURE = "literature"
    LANGUAGE = "language"
    COMPUTER_SCIENCE = "computer_science"
    OTHER = "other"

class TestTemplate(Base):
    __tablename__ = "test_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    test_type = Column(String(50), nullable=False)  # TestType enum
    category = Column(String(50), nullable=True)    # TestCategory enum
    subject = Column(String(50), nullable=True)     # TestSubject enum
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TestTemplate(id={self.id}, name='{self.name}', type={self.test_type})>"

def generate_test_code():
    """Test uchun maxsus kod yaratish"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
