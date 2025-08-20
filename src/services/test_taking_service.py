from sqlalchemy.orm import Session
from src.models import Test, Question, Answer, TestResult, TestStatus
from src.database import Database
from datetime import datetime
import json

class TestTakingService:
    def __init__(self, db: Database):
        self.db = db
    
    async def get_test_for_student(self, test_id: int) -> dict:
        """O'quvchi uchun testni olish"""
        session = self.db.get_session()
        try:
            test = session.query(Test).filter(
                Test.id == test_id,
                Test.status == TestStatus.ACTIVE
            ).first()
            
            if not test:
                return None
            
            questions = session.query(Question).filter(
                Question.test_id == test_id
            ).order_by(Question.order_number).all()
            
            test_data = {
                'id': test.id,
                'title': test.title,
                'description': test.description,
                'time_limit': test.time_limit,
                'passing_score': test.passing_score,
                'questions': []
            }
            
            for question in questions:
                answers = session.query(Answer).filter(
                    Answer.question_id == question.id
                ).order_by(Answer.order_number).all()
                
                question_data = {
                    'id': question.id,
                    'text': question.question_text,
                    'points': question.points,
                    'answers': [
                        {
                            'id': answer.id,
                            'text': answer.answer_text
                        } for answer in answers
                    ]
                }
                test_data['questions'].append(question_data)
            
            return test_data
            
        finally:
            self.db.close_session(session)
    
    async def start_test_session(self, test_id: int, student_id: int) -> dict:
        """Test sessiyasini boshlash"""
        session = self.db.get_session()
        try:
            # Test mavjudligini tekshirish
            test = session.query(Test).filter(
                Test.id == test_id,
                Test.status == TestStatus.ACTIVE
            ).first()
            
            if not test:
                return None
            
            # Avvalgi natija mavjudligini tekshirish
            existing_result = session.query(TestResult).filter(
                TestResult.test_id == test_id,
                TestResult.student_id == student_id
            ).first()
            
            if existing_result:
                return {'error': 'Bu testni avval ishlagansiz!'}
            
            # Test ma'lumotlarini olish
            test_data = await self.get_test_for_student(test_id)
            
            return {
                'test': test_data,
                'started_at': datetime.now(),
                'session_id': f"{test_id}_{student_id}_{datetime.now().timestamp()}"
            }
            
        finally:
            self.db.close_session(session)
    
    async def submit_test_answers(self, test_id: int, student_id: int, 
                                 answers: dict) -> TestResult:
        """Test javoblarini topshirish"""
        session = self.db.get_session()
        try:
            # Test ma'lumotlarini olish
            test = session.query(Test).filter(Test.id == test_id).first()
            if not test:
                raise ValueError("Test topilmadi!")
            
            # Javoblarni tekshirish va ball hisoblash
            total_score = 0
            max_score = 0
            answers_data = {}
            
            questions = session.query(Question).filter(Question.test_id == test_id).all()
            
            for question in questions:
                max_score += question.points
                
                if str(question.id) in answers:
                    student_answer_id = answers[str(question.id)]
                    
                    # To'g'ri javobni tekshirish
                    correct_answer = session.query(Answer).filter(
                        Answer.question_id == question.id,
                        Answer.is_correct == True
                    ).first()
                    
                    if correct_answer and str(correct_answer.id) == str(student_answer_id):
                        total_score += question.points
                    
                    answers_data[str(question.id)] = {
                        'question_id': question.id,
                        'student_answer_id': student_answer_id,
                        'correct_answer_id': correct_answer.id if correct_answer else None,
                        'is_correct': correct_answer and str(correct_answer.id) == str(student_answer_id)
                    }
            
            # Natijani saqlash
            percentage = (total_score / max_score) * 100 if max_score > 0 else 0
            
            result = TestResult(
                test_id=test_id,
                student_id=student_id,
                score=total_score,
                max_score=max_score,
                percentage=percentage,
                answers_data=answers_data,
                completed_at=datetime.now()
            )
            
            session.add(result)
            session.commit()
            session.refresh(result)
            
            return result
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def get_test_result(self, result_id: int) -> dict:
        """Test natijasini olish"""
        session = self.db.get_session()
        try:
            result = session.query(TestResult).filter(TestResult.id == result_id).first()
            if not result:
                return None
            
            return {
                'id': result.id,
                'test_title': result.test.title,
                'score': result.score,
                'max_score': result.max_score,
                'percentage': result.percentage,
                'completed_at': result.completed_at,
                'passed': result.percentage >= result.test.passing_score
            }
            
        finally:
            self.db.close_session(session)
