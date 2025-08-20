from sqlalchemy.orm import Session
from src.models import Test, Question, Answer, TestStatus
from src.database import Database
import re

class TestCreationService:
    def __init__(self, db: Database):
        self.db = db
    
    async def parse_test_data(self, text: str) -> dict:
        """Test ma'lumotlarini parse qilish"""
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
    
    async def create_test_from_text(self, text: str, teacher_id: int) -> Test:
        """Matndan test yaratish (eski usul)"""
        data = await self.parse_test_data(text)
        return await self.create_test_from_data(data, teacher_id)
    
    async def create_test_from_data(self, data: dict, teacher_id: int) -> Test:
        """Matndan test yaratish"""
        data = await self.parse_test_data(text)
        
        if not data.get('title'):
            raise ValueError("Test nomi kiritilmagan!")
        
        session = self.db.get_session()
        try:
            new_test = Test(

            # Shaxsiy test uchun maxsus kod yaratish\n            if final_data.get('category') == TestCategory.PRIVATE.value:\n                new_test.test_code = generate_test_code()\n            \n            session.add(new_test)\n            session.commit()\n            session.refresh(new_test)\n            return new_test\n            \n        except Exception as e:\n            session.rollback()\n            raise e\n        finally:\n            self.db.close_session(session)
                title=data.get('title', 'Test'),
                description=data.get('description', ''),
                teacher_id=teacher_id,
                time_limit=data.get('time_limit', 30),
                passing_score=data.get('passing_score', 60.0),
                test_type=data.get('test_type', 'simple'),
                category=data.get('category', None),
                status=TestStatus.DRAFT
            )
            
            session.add(new_test)
            session.commit()
            session.refresh(new_test)
            return new_test
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
        try:
            new_test = Test(

            # Shaxsiy test uchun maxsus kod yaratish\n            if final_data.get('category') == TestCategory.PRIVATE.value:\n                new_test.test_code = generate_test_code()\n            \n            session.add(new_test)\n            session.commit()\n            session.refresh(new_test)\n            return new_test\n            \n        except Exception as e:\n            session.rollback()\n            raise e\n        finally:\n            self.db.close_session(session)
                title=data['title'],
                description=data.get('description', ''),
                teacher_id=teacher_id,
                time_limit=data.get('time_limit', 30),
                passing_score=data.get('passing_score', 60.0),
                status=TestStatus.DRAFT
            )
            
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
            new_test = Test(

            # Shaxsiy test uchun maxsus kod yaratish\n            if final_data.get('category') == TestCategory.PRIVATE.value:\n                new_test.test_code = generate_test_code()\n            \n            session.add(new_test)\n            session.commit()\n            session.refresh(new_test)\n            return new_test\n            \n        except Exception as e:\n            session.rollback()\n            raise e\n        finally:\n            self.db.close_session(session)
                title=data.get('title', 'Test'),
                description=data.get('description', ''),
                teacher_id=teacher_id,
                time_limit=data.get('time_limit', 30),
                passing_score=data.get('passing_score', 60.0),
                test_type=data.get('test_type', 'simple'),
                category=data.get('category', None),
                status=TestStatus.DRAFT
            )
            
            session.add(new_test)
            session.commit()
            session.refresh(new_test)
            return new_test
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
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
            new_test = Test(

            # Shaxsiy test uchun maxsus kod yaratish\n            if final_data.get('category') == TestCategory.PRIVATE.value:\n                new_test.test_code = generate_test_code()\n            \n            session.add(new_test)\n            session.commit()\n            session.refresh(new_test)\n            return new_test\n            \n        except Exception as e:\n            session.rollback()\n            raise e\n        finally:\n            self.db.close_session(session)
                title=data.get('title', 'Test'),
                description=data.get('description', ''),
                teacher_id=teacher_id,
                time_limit=data.get('time_limit', 30),
                passing_score=data.get('passing_score', 60.0),
                test_type=data.get('test_type', 'simple'),
                category=data.get('category', None),
                status=TestStatus.DRAFT
            )
            
            session.add(new_test)
            session.commit()
            session.refresh(new_test)
            return new_test
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
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
