from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models import Test, Question, Answer, TestResult, TestStatus
from src.database import Database

class TestService:
    def __init__(self, db: Database):
        self.db = db
    
    async def create_test(self, title: str, description: str, teacher_id: int, 
                         time_limit: int = None, passing_score: float = None) -> Test:
        """Yangi test yaratish"""
        session = self.db.get_session()
        try:
            new_test = Test(
                title=title,
                description=description,
                teacher_id=teacher_id,
                time_limit=time_limit,
                passing_score=passing_score,
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
    
    async def get_available_tests(self) -> list[Test]:
        """Mavjud testlarni olish (faqat ommaviy testlar)"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(
                Test.status == TestStatus.ACTIVE,
                Test.category == TestCategory.PUBLIC.value
            ).all()
        finally:
            self.db.close_session(session)
    
    async def get_test_by_code(self, test_code: str) -> Test:
        """Maxsus kod bo'yicha testni olish"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(
                Test.test_code == test_code,
                Test.status == TestStatus.ACTIVE
            ).first()
        finally:
            self.db.close_session(session)
        finally:
            self.db.close_session(session)
    
    async def get_test_by_id(self, test_id: int) -> Test:
        """ID bo'yicha testni olish"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(Test.id == test_id).first()
        finally:
            self.db.close_session(session)
    
    async def get_teacher_tests(self, teacher_id: int) -> list[Test]:
        """O'qituvchining testlarini olish"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(Test.teacher_id == teacher_id).all()
        finally:
            self.db.close_session(session)
    
    async def add_question(self, test_id: int, question_text: str, 
                          question_type: str = "multiple_choice", points: int = 1, 
                          order_number: int = None) -> Question:
        """Testga savol qo'shish"""
        session = self.db.get_session()
        try:
            if order_number is None:
                # Avtomatik tartib raqami
                max_order = session.query(Question).filter(Question.test_id == test_id).count()
                order_number = max_order + 1
            
            new_question = Question(
                test_id=test_id,
                question_text=question_text,
                question_type=question_type,
                points=points,
                order_number=order_number
            )
            
            session.add(new_question)
            session.commit()
            session.refresh(new_question)
            return new_question
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def add_answer(self, question_id: int, answer_text: str, 
                        is_correct: bool = False, order_number: int = None) -> Answer:
        """Savolga javob qo'shish"""
        session = self.db.get_session()
        try:
            if order_number is None:
                # Avtomatik tartib raqami
                max_order = session.query(Answer).filter(Answer.question_id == question_id).count()
                order_number = max_order + 1
            
            new_answer = Answer(
                question_id=question_id,
                answer_text=answer_text,
                is_correct=is_correct,
                order_number=order_number
            )
            
            session.add(new_answer)
            session.commit()
            session.refresh(new_answer)
            return new_answer
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def get_test_questions(self, test_id: int) -> list[Question]:
        """Testning savollarini olish"""
        session = self.db.get_session()
        try:
            return session.query(Question).filter(Question.test_id == test_id).order_by(Question.order_number).all()
        finally:
            self.db.close_session(session)
    
    async def get_question_answers(self, question_id: int) -> list[Answer]:
        """Savolning javoblarini olish"""
        session = self.db.get_session()
        try:
            return session.query(Answer).filter(Answer.question_id == question_id).order_by(Answer.order_number).all()
        finally:
            self.db.close_session(session)
    
    async def submit_test_result(self, test_id: int, student_id: int, 
                                score: float, max_score: float, answers_data: dict) -> TestResult:
        """Test natijasini saqlash"""
        session = self.db.get_session()
        try:
            percentage = (score / max_score) * 100 if max_score > 0 else 0
            
            new_result = TestResult(
                test_id=test_id,
                student_id=student_id,
                score=score,
                max_score=max_score,
                percentage=percentage,
                answers_data=answers_data
            )
            
            session.add(new_result)
            session.commit()
            session.refresh(new_result)
            return new_result
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def get_student_results(self, student_id: int) -> list[TestResult]:
        """O'quvchining natijalarini olish"""
        session = self.db.get_session()
        try:
            return session.query(TestResult).filter(TestResult.student_id == student_id).all()
        finally:
            self.db.close_session(session)
    
    async def get_test_results(self, test_id: int) -> list[TestResult]:
        """Testning barcha natijalarini olish"""
        session = self.db.get_session()
        try:
            return session.query(TestResult).filter(TestResult.test_id == test_id).all()
        finally:
            self.db.close_session(session)
