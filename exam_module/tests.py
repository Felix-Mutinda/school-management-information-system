import datetime

from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from django.shortcuts import reverse

from django_webtest import WebTest

from accounts.tests import create_profile, create_user

from .models import (
    Subject,
    ExamType,
    Term,
    Exam
)
from .forms import (
    CreateExamForm,
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
            house='house',
            date_registered=timezone.now()
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
            house='house',
            date_registered=timezone.now(),
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

class SubjectModelTests(TestCase):

    def test_create_null_subject_name(self):
        '''
        No null subject names are allowed.
        '''
        subject = Subject()
        subject.name = None
        self.assertRaises(IntegrityError, subject.save)

class ExamTypeModelTests(TestCase):

    def test_create_null_exam_type_name(self):
        '''
        No null subject names are allowed.
        '''
        exam_type = ExamType()
        exam_type.name = None
        self.assertRaises(IntegrityError, exam_type.save)

class TermModelTests(TestCase):

    def test_create_null_term_name(self):
        '''
        No null subject names are allowed.
        '''
        term = Term()
        term.name = None
        self.assertRaises(IntegrityError, term.save)

class CreateExamFormTests(TestCase):

    def test_form_with_no_data(self):
        '''
        All fields of an exam object are required.
        '''
        exam_form = CreateExamForm({})
        self.assertFalse(exam_form.is_valid())
        self.assertEqual(exam_form.errors['exam_type_name'], ['This field is required.'])
        self.assertEqual(exam_form.errors['date_done'], ['This field is required.'])
        self.assertEqual(exam_form.errors['student_reg_no'], ['This field is required.'])
        self.assertEqual(exam_form.errors['exam_type_name'], ['This field is required.'])
        self.assertEqual(exam_form.errors['subject_name'], ['This field is required.'])
        self.assertEqual(exam_form.errors['term_name'], ['This field is required.'])
    
    def test_form_with_partial_data(self):
        '''
        All fields required.
        '''
        exam_form = CreateExamForm({
            'student_reg_no': '4576',
            'marks': 50.0,
            'term_name': 3
        })
        self.assertFalse(exam_form.is_valid())
        self.assertEqual(exam_form.errors['subject_name'], ['This field is required.'])
        self.assertEqual(exam_form.errors['exam_type_name'], ['This field is required.'])
        self.assertEqual(exam_form.errors['date_done'], ['This field is required.'])

    def test_form_with_all_fields_filled(self):
        '''
        Correctly filled form should not raise any 
        validation errors.
        '''
        exam_form = CreateExamForm({
            'student_reg_no': '3345',
            'subject_name': 'Mathematics',
            'exam_type_name': 'Mid-term',
            'term_name': '3',
            'date_done': timezone.now(),
            'marks': 50.0,
        })
        self.assertTrue(exam_form.is_valid())

class CreateOneExamViewTests(WebTest):
    fixtures = ['users','student_profiles', 'subjects', 'terms', 'exam_types']

    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.create_one_exam_url = reverse('exam_module:create_one_exam')
        # self.create_batch_exam_url = reverse('exam_module:create_batch_exam')

    def test_requires_login(self):
        '''
        Should redirect to a login page is no logged in.
        '''
        page = self.app.get(self.create_one_exam_url)
        self.assertRedirects(
            page,
            '%s?next=%s' %(self.login_url, self.create_one_exam_url)
        )
    
    def test_form_is_rendered(self):
        '''
        Should be able to display the exam input form.
        '''
        page = self.app.get(self.create_one_exam_url, user='staff')
        self.assertEqual(len(page.forms), 1)
    
    def test_submit_form_with_no_data(self):
        '''
        Required fields should raise validation error.
        '''
        page = self.app.get(self.create_one_exam_url, user='staff')
        page = page.form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'This field is required.')

    def test_submit_form_with_data(self):
        '''
        Required fields should raise validation error.
        '''
        page = self.app.get(self.create_one_exam_url, user='staff')
        page.form['student_reg_no'] = '2'
        page.form['subject_name'] = 'Biology'
        page.form['exam_type_name'] = 'CAT 2'
        page.form['term_name'] = '3'
        page.form['date_done'] =  datetime.datetime.now()
        page.form['marks'] = 50.0
        page = page.form.submit().follow()
        self.assertContains(page, 'Data has been saved successfully.')

class HomeViewTests(WebTest):  

    def test_requires_login(self):
        page = self.app.get(reverse('exam_module:home'))
        self.assertRedirects(
            page,
            '%s?next=%s' %(reverse('accounts:login'), reverse('exam_module:home'))
        )
    
    def test_home_displays_message(self):
        '''
        Should have a title Exam Module.
        '''
        page = self.app.get(reverse('exam_module:home'), user='staff')
        self.assertTrue(page.status_code, 200)
        self.assertContains(page, 'Exam Module.')