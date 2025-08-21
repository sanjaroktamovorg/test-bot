from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models import Test, Question, Answer, TestResult, TestStatus
from src.models.test_types import TestCategory
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
                Test.status == TestStatus.ACTIVE.value,
                Test.category == TestCategory.PUBLIC.value
            ).all()
        finally:
            self.db.close_session(session)
    
    async def get_public_tests(self) -> list[Test]:
        """Faqat ommaviy testlarni olish"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(
                Test.status == TestStatus.ACTIVE.value,
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
                Test.status == TestStatus.ACTIVE.value
            ).first()
        finally:
            self.db.close_session(session)
    
    async def search_test_by_title(self, title: str) -> Test:
        """Test nomi bo'yicha qidirish"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(
                Test.title.ilike(f"%{title}%"),
                Test.status == TestStatus.ACTIVE.value
            ).first()
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
    
    async def get_test_results(self, test_id: int) -> list[TestResult]:
        """Test natijalarini olish"""
        session = self.db.get_session()
        try:
            return session.query(TestResult).filter(TestResult.test_id == test_id).all()
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
    
    # Statistika metodlari
    async def get_teacher_tests_count(self, teacher_id: int) -> int:
        """O'qituvchining testlar sonini olish"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(Test.teacher_id == teacher_id).count()
        finally:
            self.db.close_session(session)
    
    async def get_teacher_active_tests_count(self, teacher_id: int) -> int:
        """O'qituvchining faol testlar sonini olish"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(
                Test.teacher_id == teacher_id,
                Test.status == TestStatus.ACTIVE.value
            ).count()
        finally:
            self.db.close_session(session)
    
    async def get_teacher_total_results(self, teacher_id: int) -> int:
        """O'qituvchining barcha test natijalari sonini olish"""
        session = self.db.get_session()
        try:
            # O'qituvchining testlari ID larini olish
            teacher_test_ids = session.query(Test.id).filter(Test.teacher_id == teacher_id).subquery()
            # Bu testlardagi barcha natijalar sonini hisoblash
            return session.query(TestResult).filter(TestResult.test_id.in_(teacher_test_ids)).count()
        finally:
            self.db.close_session(session)
    
    async def get_student_completed_tests_count(self, student_id: int) -> int:
        """O'quvchining bajargan testlar sonini olish"""
        session = self.db.get_session()
        try:
            return session.query(TestResult).filter(TestResult.student_id == student_id).count()
        finally:
            self.db.close_session(session)
    
    async def get_student_average_score(self, student_id: int) -> float:
        """O'quvchining o'rtacha ballini olish"""
        session = self.db.get_session()
        try:
            results = session.query(TestResult).filter(TestResult.student_id == student_id).all()
            if not results:
                return 0.0
            total_percentage = sum(result.percentage for result in results)
            return total_percentage / len(results)
        finally:
            self.db.close_session(session)
    
    async def get_student_best_score(self, student_id: int) -> float:
        """O'quvchining eng yaxshi natijasini olish"""
        session = self.db.get_session()
        try:
            result = session.query(TestResult).filter(TestResult.student_id == student_id).order_by(TestResult.percentage.desc()).first()
            return result.percentage if result else 0.0
        finally:
            self.db.close_session(session)
    
    # Reyting metodlari
    async def get_top_students_by_average_score(self, limit: int = 10) -> list:
        """O'rtacha ball bo'yicha eng yaxshi o'quvchilar"""
        session = self.db.get_session()
        try:
            # Har bir o'quvchining o'rtacha ballini hisoblash
            from sqlalchemy import func
            
            subquery = session.query(
                TestResult.student_id,
                func.avg(TestResult.percentage).label('avg_score'),
                func.count(TestResult.id).label('tests_count')
            ).group_by(TestResult.student_id).having(
                func.count(TestResult.id) >= 1  # Kamida 1 ta test bajargan
            ).subquery()
            
            # O'rtacha ball bo'yicha saralash
            results = session.query(
                subquery.c.student_id,
                subquery.c.avg_score,
                subquery.c.tests_count
            ).order_by(subquery.c.avg_score.desc()).limit(limit).all()
            
            return results
        finally:
            self.db.close_session(session)
    
    async def get_top_students_by_best_score(self, limit: int = 10) -> list:
        """Eng yaxshi natija bo'yicha top o'quvchilar"""
        session = self.db.get_session()
        try:
            # Har bir o'quvchining eng yaxshi natijasini olish
            from sqlalchemy import func
            
            subquery = session.query(
                TestResult.student_id,
                func.max(TestResult.percentage).label('best_score'),
                func.count(TestResult.id).label('tests_count')
            ).group_by(TestResult.student_id).having(
                func.count(TestResult.id) >= 1  # Kamida 1 ta test bajargan
            ).subquery()
            
            # Eng yaxshi natija bo'yicha saralash
            results = session.query(
                subquery.c.student_id,
                subquery.c.best_score,
                subquery.c.tests_count
            ).order_by(subquery.c.best_score.desc()).limit(limit).all()
            
            return results
        finally:
            self.db.close_session(session)
    
    async def get_top_students_by_tests_count(self, limit: int = 10) -> list:
        """Testlar soni bo'yicha eng faol o'quvchilar"""
        session = self.db.get_session()
        try:
            # Har bir o'quvchining testlar sonini hisoblash
            from sqlalchemy import func
            
            results = session.query(
                TestResult.student_id,
                func.count(TestResult.id).label('tests_count'),
                func.avg(TestResult.percentage).label('avg_score')
            ).group_by(TestResult.student_id).order_by(
                func.count(TestResult.id).desc()
            ).limit(limit).all()
            
            return results
        finally:
            self.db.close_session(session)
    
    async def get_student_ranking_position(self, student_id: int) -> dict:
        """O'quvchining reytingdagi o'rnini olish"""
        session = self.db.get_session()
        try:
            # O'quvchining o'rtacha ballini hisoblash
            from sqlalchemy import func
            
            student_avg = session.query(
                func.avg(TestResult.percentage).label('avg_score')
            ).filter(TestResult.student_id == student_id).scalar()
            
            if not student_avg:
                return {
                    'position': None,
                    'total_students': 0,
                    'avg_score': 0.0,
                    'tests_count': 0
                }
            
            # Barcha o'quvchilar o'rtacha ballini hisoblash
            all_students_avg = session.query(
                TestResult.student_id,
                func.avg(TestResult.percentage).label('avg_score')
            ).group_by(TestResult.student_id).subquery()
            
            # O'quvchining o'rnini hisoblash
            position = session.query(all_students_avg).filter(
                all_students_avg.c.avg_score > student_avg
            ).count() + 1
            
            # Jami o'quvchilar soni
            total_students = session.query(all_students_avg).count()
            
            # O'quvchining testlar soni
            tests_count = session.query(TestResult).filter(
                TestResult.student_id == student_id
            ).count()
            
            return {
                'position': position,
                'total_students': total_students,
                'avg_score': float(student_avg),
                'tests_count': tests_count
            }
        finally:
            self.db.close_session(session)
    
    async def check_test_title_unique(self, title: str, teacher_id: int) -> bool:
        """Test nomi unique ekanligini tekshirish (bir o'qituvchi uchun)"""
        session = self.db.get_session()
        try:
            existing_test = session.query(Test).filter(
                Test.title == title,
                Test.teacher_id == teacher_id
            ).first()
            return existing_test is None
        finally:
            self.db.close_session(session)
    
    async def generate_test_code(self) -> str:
        """Maxsus test kodi yaratish"""
        import random
        import string
        
        # 6 xonali raqam + 2 ta harf
        numbers = ''.join(random.choices(string.digits, k=6))
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        test_code = f"{numbers}{letters}"
        
        # Kod unique ekanligini tekshirish
        session = self.db.get_session()
        try:
            existing_code = session.query(Test).filter(Test.test_code == test_code).first()
            if existing_code:
                # Agar kod mavjud bo'lsa, yangi kod yaratish
                return await self.generate_test_code()
            return test_code
        finally:
            self.db.close_session(session)
    
    async def search_public_tests_by_title(self, title: str, limit: int = 10, offset: int = 0) -> list[Test]:
        """Ommaviy testlarni nom bo'yicha qidirish (sahifalash bilan)"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(
                Test.title.ilike(f"%{title}%"),
                Test.status == TestStatus.ACTIVE.value,
                Test.category == TestCategory.PUBLIC.value
            ).offset(offset).limit(limit).all()
        finally:
            self.db.close_session(session)
    
    async def count_public_tests_by_title(self, title: str) -> int:
        """Ommaviy testlar sonini hisoblash (nom bo'yicha)"""
        session = self.db.get_session()
        try:
            return session.query(Test).filter(
                Test.title.ilike(f"%{title}%"),
                Test.status == TestStatus.ACTIVE.value,
                Test.category == TestCategory.PUBLIC.value
            ).count()
        finally:
            self.db.close_session(session)
    
    # Test tahrirlash metodlari
    async def update_test_basic_info(self, test_id: int, teacher_id: int, **kwargs) -> bool:
        """Testning asosiy ma'lumotlarini yangilash"""
        session = self.db.get_session()
        try:
            test = session.query(Test).filter(
                Test.id == test_id,
                Test.teacher_id == teacher_id
            ).first()
            
            if not test:
                return False
            
            # Yangilanish mumkin bo'lgan maydonlar
            allowed_fields = ['title', 'description', 'subject', 'time_limit', 'passing_score', 'category']
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(test, field, value)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def update_question(self, question_id: int, teacher_id: int, **kwargs) -> bool:
        """Savolni yangilash"""
        session = self.db.get_session()
        try:
            # Savol o'qituvchiga tegishli ekanligini tekshirish
            question = session.query(Question).join(Test).filter(
                Question.id == question_id,
                Test.teacher_id == teacher_id
            ).first()
            
            if not question:
                return False
            
            # Yangilanish mumkin bo'lgan maydonlar
            allowed_fields = ['question_text', 'points', 'order_number']
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(question, field, value)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def update_answer(self, answer_id: int, teacher_id: int, **kwargs) -> bool:
        """Javobni yangilash"""
        session = self.db.get_session()
        try:
            # Javob o'qituvchiga tegishli ekanligini tekshirish
            answer = session.query(Answer).join(Question).join(Test).filter(
                Answer.id == answer_id,
                Test.teacher_id == teacher_id
            ).first()
            
            if not answer:
                return False
            
            # Yangilanish mumkin bo'lgan maydonlar
            allowed_fields = ['answer_text', 'is_correct', 'order_number']
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(answer, field, value)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def delete_question(self, question_id: int, teacher_id: int) -> bool:
        """Savolni o'chirish"""
        session = self.db.get_session()
        try:
            # Savol o'qituvchiga tegishli ekanligini tekshirish
            question = session.query(Question).join(Test).filter(
                Question.id == question_id,
                Test.teacher_id == teacher_id
            ).first()
            
            if not question:
                return False
            
            # Avval javoblarni o'chirish
            session.query(Answer).filter(Answer.question_id == question_id).delete()
            
            # Keyin savolni o'chirish
            session.delete(question)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def delete_answer(self, answer_id: int, teacher_id: int) -> bool:
        """Javobni o'chirish"""
        session = self.db.get_session()
        try:
            # Javob o'qituvchiga tegishli ekanligini tekshirish
            answer = session.query(Answer).join(Question).join(Test).filter(
                Answer.id == answer_id,
                Test.teacher_id == teacher_id
            ).first()
            
            if not answer:
                return False
            
            session.delete(answer)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)
    
    async def get_test_for_editing(self, test_id: int, teacher_id: int) -> dict:
        """Testni tahrirlash uchun ma'lumotlarni olish"""
        session = self.db.get_session()
        try:
            test = session.query(Test).filter(
                Test.id == test_id,
                Test.teacher_id == teacher_id
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
                'subject': test.subject,
                'time_limit': test.time_limit,
                'passing_score': test.passing_score,
                'category': test.category,
                'status': test.status,
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
                    'order_number': question.order_number,
                    'answers': [
                        {
                            'id': answer.id,
                            'text': answer.answer_text,
                            'is_correct': answer.is_correct,
                            'order_number': answer.order_number
                        } for answer in answers
                    ]
                }
                test_data['questions'].append(question_data)
            
            return test_data
            
        finally:
            self.db.close_session(session)
    
    async def get_question_by_id(self, question_id: int) -> Question:
        """ID bo'yicha savolni olish"""
        session = self.db.get_session()
        try:
            return session.query(Question).filter(Question.id == question_id).first()
        finally:
            self.db.close_session(session)
    
    async def get_answer_by_id(self, answer_id: int) -> Answer:
        """ID bo'yicha javobni olish"""
        session = self.db.get_session()
        try:
            return session.query(Answer).filter(Answer.id == answer_id).first()
        finally:
            self.db.close_session(session)