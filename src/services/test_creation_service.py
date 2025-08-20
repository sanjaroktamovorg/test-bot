from sqlalchemy.orm import Session
from src.models import Test, Question, Answer, TestStatus, TestType, TestCategory
from src.database import Database
import random
import string

class TestCreationService:
    def __init__(self, db: Database):
        self.db = db
    
    def generate_test_code(self) -> str:
        """Shaxsiy test uchun maxsus kod yaratish"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    async def create_simple_test(self, data: dict, teacher_id: int) -> Test:
        """Oddiy test yaratish - soddalashtirilgan"""
        session = self.db.get_session()
        try:
            new_test = Test(
                title=data['title'],
                description=data.get('description', ''),
                teacher_id=teacher_id,
                test_type=TestType.SIMPLE,
                category=data.get('category', TestCategory.PUBLIC),
                subject=data.get('subject', ''),
                time_limit=data.get('time_limit', 30),
                passing_score=data.get('passing_score', 60.0),
                status=TestStatus.DRAFT
            )
            
            # Shaxsiy test uchun maxsus kod yaratish
            if data.get('category') == TestCategory.PRIVATE:
                new_test.test_code = self.generate_test_code()
            
            session.add(new_test)
            session.commit()
            session.refresh(new_test)
            return new_test
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def add_question_to_test(self, test_id: int, question_text: str, 
                                  answers: list, correct_answer: int) -> Question:
        """Testga savol qo'shish"""
        session = self.db.get_session()
        try:
            # Savol yaratish
            question = Question(
                test_id=test_id,
                question_text=question_text,
                question_type="multiple_choice",
                points=1,
                order_number=1  # Avtomatik tartib
            )
            
            session.add(question)
            session.commit()
            session.refresh(question)
            
            # Javoblar qo'shish
            for i, answer_text in enumerate(answers):
                answer = Answer(
                    question_id=question.id,
                    answer_text=answer_text,
                    is_correct=(i == correct_answer),
                    order_number=i + 1
                )
                session.add(answer)
            
            session.commit()
            return question
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def activate_test(self, test_id: int) -> bool:
        """Testni faollashtirish"""
        session = self.db.get_session()
        try:
            test = session.query(Test).filter(Test.id == test_id).first()
            if test:
                test.status = TestStatus.ACTIVE
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def parse_test_data(self, text: str) -> dict:
        """Test ma'lumotlarini parse qilish (eski usul uchun)"""
        import re
        data = {}
        
        # Test nomi
        name_match = re.search(r'Test nomi:\s*(.+)', text, re.IGNORECASE)
        if name_match:
            data['title'] = name_match.group(1).strip()
        
        # Tavsif
        desc_match = re.search(r'Tavsif:\s*(.+)', text, re.IGNORECASE)
        if desc_match:
            data['description'] = desc_match.group(1).strip()
        
        # Vaqt chegarasi
        time_match = re.search(r'Vaqt chegarasi:\s*(\d+)', text, re.IGNORECASE)
        if time_match:
            data['time_limit'] = int(time_match.group(1))
        
        # O'tish balli
        score_match = re.search(r'O\'tish balli:\s*(\d+)', text, re.IGNORECASE)
        if score_match:
            data['passing_score'] = float(score_match.group(1))
        
        return data
    
    async def create_test_from_data(self, data: dict, teacher_id: int) -> Test:
        """Ma'lumotlardan test yaratish (eski usul uchun)"""
        return await self.create_simple_test(data, teacher_id)
