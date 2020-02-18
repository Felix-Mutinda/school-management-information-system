from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError

from accounts.tests import create_profile, create_user

from .models import (
    Subject,
    ExamType,
    Term,
    Exam
)

class ExamModelTests(TestCase):

    def test_is_exam_object_created_with_no_data(self):
        '''
        All the fields are required to create an exam object.
        '''
        exam = Exam()
        self.assertRaises(IntegrityError, exam.save)
    
    def test_is_exam_object_created_with_all_data(self):
        '''
        If all fields are given the exam creation should 
        succeed.
        '''
        student_user = create_user(is_student=True, username='student', password='pass')
        student_profile = create_profile(
            is_student=True,
            user=student_user,
            reg_no='reg_no',
            form='2',
            stream='south',
            house='house'
        )
        subject = Subject.objects.create(name='Mathematics')
        exam_type = ExamType.objects.create(name='Mid-term')
        term = Term.objects.create(name='1')
        date_done = timezone.now()
        marks = 50.0
        exam = Exam.objects.create(
            student=student_profile,
            subject=subject,
            exam_type=exam_type,
            term=term,
            date_done=date_done,
            marks=marks
        )
        self.assertEqual(Exam.objects.count(), 1)
        exam = Exam.objects.first()
        self.assertEqual(exam.student, student_profile)
        self.assertEqual(exam.subject, subject)
        self.assertEqual(exam.exam_type, exam_type)
        self.assertEqual(exam.term, term)
        self.assertEqual(exam.date_done, date_done)
        self.assertEqual(exam.marks, marks)
        
    def test_student_can_do_multiple_exams(self):
        '''
        A student  should be able to sit for several exams.
        '''
        student_user = create_user(is_student=True, username='student', password='pass')
        student_profile = create_profile(
            is_student=True,
            user=student_user,
            reg_no='reg_no',
            form='2',
            stream='south',
            house='house'
        )
        subject = Subject.objects.create(name='Mathematics')
        exam_type = ExamType.objects.create(name='Mid-term')
        term = Term.objects.create(name='1')
        date_done = timezone.now()
        marks = 50.0
        exam = Exam.objects.create(
            student=student_profile,
            subject=subject,
            exam_type=exam_type,
            term=term,
            date_done=date_done,
            marks=marks
        )

        subject2 = Subject.objects.create(name='English')
        exam_type2 = ExamType.objects.create(name='End-term')
        term2 = Term.objects.create(name='2')
        exam = Exam.objects.create(
            student=student_profile,
            subject=subject2,
            exam_type=exam_type2,
            term=term2,
            date_done=date_done,
            marks=marks
        )
        self.assertEqual(Exam.objects.count(), 2)
        exam = Exam.objects.first()
        self.assertEqual(exam.student, student_profile)
        self.assertEqual(exam.subject, subject)
        self.assertEqual(exam.exam_type, exam_type)
        self.assertEqual(exam.term, term)
        self.assertEqual(exam.date_done, date_done)
        self.assertEqual(exam.marks, marks)

        exam = Exam.objects.last()
        self.assertEqual(exam.student, student_profile)
        self.assertEqual(exam.subject, subject2)
        self.assertEqual(exam.exam_type, exam_type2)
        self.assertEqual(exam.term, term2)
        self.assertEqual(exam.date_done, date_done)
        self.assertEqual(exam.marks, marks)