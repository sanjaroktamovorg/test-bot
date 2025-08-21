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
                test_type=TestType.SIMPLE.value,  # .value qo'shildi
                category=data.get('category', TestCategory.PUBLIC.value),  # .value qo'shildi
                subject=data.get('subject', ''),
                time_limit=data.get('time_limit', 30),
                passing_score=data.get('passing_score', 60.0),
                status=TestStatus.DRAFT.value  # .value qo'shildi
            )
            
            # Shaxsiy test uchun maxsus kod yaratish
            if data.get('category') == TestCategory.PRIVATE.value:  # .value qo'shildi
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
    
    async def parse_abcd_format(self, text: str) -> list:
        """ABCD formatini parse qilish - abcd, ABCD, 1a2b3c4d formatlarini qo'llab-quvvatlash"""
        text = text.strip().replace(' ', '').replace('\n', '')
        questions = []
        
        # Format 1: abcdabcd... yoki ABCDABCD...
        if all(char.lower() in 'abcd' for char in text):
            for i, answer in enumerate(text):
                questions.append({
                    'question_number': i + 1,
                    'correct_answer': answer.upper()
                })
        
        # Format 2: 1a2b3c4d5a... (raqam + harf)
        elif any(char.isdigit() for char in text):
            current_number = ""
            for char in text:
                if char.isdigit():
                    current_number = char
                elif char.lower() in 'abcd' and current_number:
                    questions.append({
                        'question_number': int(current_number),
                        'correct_answer': char.upper()
                    })
                    current_number = ""
        
        # Format 3: Har qatordan alohida (har qatorda bitta javob)
        else:
            lines = text.split('\n') if '\n' in text else [text]
            for i, line in enumerate(lines):
                line = line.strip().replace(' ', '')
                if line and line[0].lower() in 'abcd':
                    questions.append({
                        'question_number': i + 1,
                        'correct_answer': line[0].upper()
                    })
        
        return questions
    
    async def create_test_with_abcd_answers(self, test_id: int, abcd_text: str) -> bool:
        """ABCD formatida test yaratish"""
        session = self.db.get_session()
        try:
            # ABCD formatini parse qilish
            questions_data = await self.parse_abcd_format(abcd_text)
            
            if not questions_data:
                raise ValueError("ABCD formatida savollar topilmadi!")
            
            # Har bir savol uchun standart savol matni yaratish
            for i, q_data in enumerate(questions_data):
                question_number = q_data['question_number']
                correct_answer = q_data['correct_answer']
                
                # Savol yaratish
                question = Question(
                    test_id=test_id,
                    question_text=f"Savol {question_number}",
                    question_type="multiple_choice",
                    points=1,
                    order_number=question_number
                )
                
                session.add(question)
                session.commit()
                session.refresh(question)
                
                # Javoblar qo'shish (A, B, C, D)
                answers = ['A', 'B', 'C', 'D']
                for j, answer_text in enumerate(answers):
                    answer = Answer(
                        question_id=question.id,
                        answer_text=f"Variant {answer_text}",
                        is_correct=(answer_text == correct_answer),
                        order_number=j + 1
                    )
                    session.add(answer)
                
                session.commit()
            
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def add_question_to_test(self, test_id: int, question_text: str, 
                                  answers: list, correct_answer: int) -> Question:
        """Testga savol qo'shish (eski usul)"""
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
                test.status = TestStatus.ACTIVE.value  # .value qo'shildi
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
