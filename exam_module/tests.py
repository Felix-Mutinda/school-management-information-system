import datetime
import decimal

from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from django.shortcuts import reverse

from django_webtest import WebTest

from accounts.tests import create_profile, create_user
from accounts.models import Stream

from .models import (
    Subject,
    ExamType,
    Term,
    Exam
)
from .forms import (
    CreateExamForm,
    CreateManyExamsFilterForm,
    ExamReportsFilterForm,
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
            stream=Stream.objects.create(name='south'),
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
            stream=Stream.objects.create(name='south'),
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
    fixtures = ['users','student_profiles', 'subjects', 'terms', 'exam_types', 'streams']

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
            'student_reg_no': '3',
            'subject_name': 'Mathematics',
            'exam_type_name': 'Mid Term',
            'term_name': '3',
            'date_done': timezone.now(),
            'marks': 50.0,
        })
        self.assertTrue(exam_form.is_valid())

class CreateOneExamViewTests(WebTest):
    fixtures = ['users','student_profiles', 'subjects', 'terms', 'exam_types', 'streams']

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
    
    def test_no_duplicate_exam_objects(self):
        '''
        Adding an exam object twice should ovewrite the existing one.
        '''
        date_done = datetime.datetime.now()
        # first instance
        page = self.app.get(self.create_one_exam_url, user='staff')
        page.form['student_reg_no'] = '2'
        page.form['subject_name'] = 'Biology'
        page.form['exam_type_name'] = 'CAT 2'
        page.form['term_name'] = '3'
        page.form['date_done'] =  date_done
        page.form['marks'] = 50.0
        page = page.form.submit().follow()

        # second instance
        page.form['student_reg_no'] = '2'
        page.form['subject_name'] = 'Biology'
        page.form['exam_type_name'] = 'CAT 2'
        page.form['term_name'] = '3'
        page.form['date_done'] =  date_done
        page.form['marks'] = 55.5
        page = page.form.submit().follow()

        # check only the second one is in db
        query_set = Exam.objects.filter(
            student__reg_no='2',
            subject__name='Biology',
            exam_type__name='CAT 2',
            term__name='3',
            date_done=date_done
        )
        self.assertEqual(len(query_set), 1)
        self.assertEqual(query_set[0].marks, 55.5)

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
        self.assertContains(page, 'Exams')

class CreateManyExamsFilterFormTests(TestCase):

    fixtures = ['users','student_profiles', 'subjects', 'terms', 'exam_types', 'streams', 'subjects_done_by_student']

    def test_form_with_no_data(self):
        '''
        Several fields are required to determine the
        class, stream, subject, exam_type ...
        needed to create exam objects for several students.
        '''
        form = CreateManyExamsFilterForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['form'], ['This field is required.'])
        self.assertEqual(form.errors['stream'], ['This field is required.'])
        self.assertEqual(form.errors['subject_name'], ['This field is required.'])
        self.assertEqual(form.errors['exam_type_name'], ['This field is required.'])
        self.assertEqual(form.errors['term_name'], ['This field is required.'])
        self.assertEqual(form.errors['date_done'], ['This field is required.'])
    
    def test_form_with_invalid_data(self):
        '''
        If a combination of the filters does not return a list
        of students, raise a validation error.
        '''
        form = CreateManyExamsFilterForm({
            'form': 6,
            'stream': 'east',
            'subject_name': 'Python',
            'exam_type_name': 'End Term',
            'term_name': '1',
            'date_done': datetime.datetime.now(),
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
                form.non_field_errors(),
                ['There are no students found in form %s %s in the year %s.' %(
                    form.cleaned_data.get('form'),
                    form.cleaned_data.get('stream'),
                    form.cleaned_data.get('date_done').year,
                )],
            )

    def test_form_with_valid_data(self):
        '''
        A valid combination of the filters should return a 
        list of students to fill their exam details.
        '''
        form = CreateManyExamsFilterForm({
            'form': 2,
            'stream': 'west',
            'subject_name': 'Kiswahili',
            'exam_type_name': 'End Term',
            'term_name': '3',
            'date_done': timezone.now(),
        })
        self.assertTrue(form.is_valid())

class CreateManyExamsFilterViewTests(WebTest):

    fixtures = ['users','student_profiles', 'subjects', 'terms', 'exam_types', 'streams', 'subjects_done_by_student']

    def setUp(self):
        self.create_many_exams_filter_url = reverse('exam_module:create_many_exams_filter')
        self.create_many_exams_url = reverse('exam_module:create_many_exams')
        self.login_url = reverse('accounts:login')

    def test_requires_login(self):
        '''
        Only authenticated users an access this view
        '''
        page = self.app.get(self.create_many_exams_filter_url)
        self.assertRedirects(
            page,
            self.login_url+'?next='+self.create_many_exams_filter_url
        )
    
    def test_redirects_to_create_many_exams_url(self):
        '''
        The filter form is embed in create_many_exams.html template.
        A get request to create_many_exams_filter redirects there.
        '''
        page = self.app.get(self.create_many_exams_filter_url, user='staff')
        self.assertRedirects(
            page,
            self.create_many_exams_url,
        )

    
    def test_filter_view_with_no_data(self):
        '''
        All filter form values are required to generate students.
        '''
        page = self.app.get(self.create_many_exams_url, user='staff')
        filter_form = page.forms['filter-exams-form']
        page = filter_form.submit()
        self.assertContains(page, 'This field is required.')

    def test_filter_view_with_invalid_data(self):
        '''
        If data generates no student list, get an error response,
        also unknown subjects, exam_types, terms also result in error.
        '''
        page = self.app.get(self.create_many_exams_url, user='staff')
        filter_form = page.forms['filter-exams-form']
        filter_form['form'] = 6
        filter_form['stream'] = 'north'
        filter_form['subject_name'] = 'Mathematics'
        filter_form['exam_type_name'] = 'Mid Term'
        filter_form['term_name'] = '3'
        filter_form['date_done'] = datetime.datetime.now()
        page = filter_form.submit()
        self.assertContains(
            page,
            'There are no students found in form %s %s in the year %s.' %(
                6,
                'north',
                datetime.datetime.now().year,
            )
        )
    
    def test_filter_view_with_valid_data(self):
        '''
        Correct filters should return the student list, no errors.
        '''
        page = self.app.get(self.create_many_exams_url, user='staff')
        filter_form = page.forms['filter-exams-form']
        filter_form['form'] = 4
        filter_form['stream'] = 'north'
        filter_form['subject_name'] = 'Kiswahili'
        filter_form['exam_type_name'] = 'CAT 2'
        filter_form['term_name'] = '2'
        filter_form['date_done'] = datetime.datetime.now()
        page = filter_form.submit()
        self.assertNotContains(
            page,
            'There are no students found in form %s %s in the year %s.' %(
                4,
                'north',
                datetime.datetime.now().year,
            )
        )
        self.assertNotContains(page, 'This subject is not found.')
        self.assertNotContains(page, 'This exam type is not found.')
        self.assertNotContains(page, 'This term is not found.')
        self.assertTrue(page.context['students_exams_entry_form'] != None)

class CreateManyExamsViewTests(WebTest):

    fixtures = ['users','student_profiles', 'subjects', 'terms', 'exam_types', 'streams', 'subjects_done_by_student']

    def setUp(self):
        self.create_many_exams_filter_url = reverse('exam_module:create_many_exams_filter')
        self.create_many_exams_url = reverse('exam_module:create_many_exams')
        self.login_url = reverse('accounts:login')

    def test_requires_login(self):
        '''
        Only authenticated users an access this view
        '''
        page = self.app.get(self.create_many_exams_url)
        self.assertRedirects(
            page,
            self.login_url+'?next='+self.create_many_exams_url
        )

    def test_filter_form_is_rendered(self):
        '''
        Show form to authenticated users to fill.
        '''
        page = self.app.get(self.create_many_exams_url, user='staff')
        self.assertTrue(len(page.forms) >= 1)
        self.assertEqual(page.forms[0].id, 'filter-exams-form')
    
    def test_filter_with_invalid_data(self):
        '''
        Incorrect combination of filter tags should return an empty
        students_list.
        '''
        page = self.app.get(self.create_many_exams_url, user='staff')
        filter_form = page.forms['filter-exams-form']
        filter_form['form'] = 8
        filter_form['stream'] = 'north'
        filter_form['subject_name'] = 'Kiswahili'
        filter_form['exam_type_name'] = 'Opener'
        filter_form['term_name'] = '2'
        filter_form['date_done'] = datetime.datetime.now()
        page = filter_form.submit()
        self.assertEqual(page.context['students_exams_entry_form'], None)
    
    def test_filter_with_valid_data(self):
        '''
        Correct combination of filter tags should return a non-empty
        students_list.
        '''
        page = self.app.get(self.create_many_exams_url, user='staff')
        filter_form = page.forms['filter-exams-form']
        filter_form['form'] = 4
        filter_form['stream'] = 'north'
        filter_form['subject_name'] = 'Kiswahili'
        filter_form['exam_type_name'] = 'CAT 2'
        filter_form['term_name'] = '2'
        filter_form['date_done'] = datetime.datetime.now()
        page = filter_form.submit()
        # 2 students returned
        self.assertTrue ('4_marks', page.forms[1].fields)
        self.assertTrue ('5_marks', page.forms[1].fields)
        self.assertContains( # their full name displayed
            page,
            'User 5 Mid name Last name',
        )
    
    def test_marks_entry_form_rendered(self):
        '''
        A form to fill in student marks based on applied filters.
        '''
        page = self.app.get(self.create_many_exams_url, user='staff')
        filter_form = page.forms['filter-exams-form']
        filter_form['form'] = 4
        filter_form['stream'] = 'north'
        filter_form['subject_name'] = 'Kiswahili'
        filter_form['exam_type_name'] = 'CAT 2'
        filter_form['term_name'] = '2'
        filter_form['date_done'] = datetime.datetime.now()
        page = filter_form.submit()
        self.assertEqual(page.forms[1].id, 'students-exams-entry-form') # second form

    def test_batch_marks_with_valid_data(self):
        '''
        Filling and submitting the students-exams-entry-form should 
        save the data to database.
        '''
        # apply filters to get the form
        page = self.app.get(self.create_many_exams_url, user='staff')
        filter_form = page.forms['filter-exams-form']
        filter_form['form'] = 4
        filter_form['stream'] = 'north'
        filter_form['subject_name'] = 'Kiswahili'
        filter_form['exam_type_name'] = 'CAT 2'
        filter_form['term_name'] = '2'
        filter_form['date_done'] = datetime.datetime.now()
        page = filter_form.submit()

        # input marks for reg_no 4 and 5 in fixtures
        entry_form = page.forms['students-exams-entry-form']
        entry_form['4_marks'] = 99.99
        entry_form['5_marks'] = 00.00
        page = entry_form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Data has been saved successfully.')
        returned_entry_form = page.forms['students-exams-entry-form']
        self.assertEqual(
            decimal.Decimal(returned_entry_form['4_marks'].value),
            decimal.Decimal('99.99')
        )
        self.assertEqual(
            decimal.Decimal(returned_entry_form['5_marks'].value),
            decimal.Decimal('00.00')
        )


    def test_batch_marks_with_invalid_data(self):
        '''
        Out of bound[0.00, 99.99] values or non decimal should raise
        validation error.
        '''
        # apply filters to get the form
        page = self.app.get(self.create_many_exams_url, user='staff')
        filter_form = page.forms['filter-exams-form']
        filter_form['form'] = 4
        filter_form['stream'] = 'north'
        filter_form['subject_name'] = 'Kiswahili'
        filter_form['exam_type_name'] = 'CAT 2'
        filter_form['term_name'] = '2'
        filter_form['date_done'] = datetime.datetime.now()
        page = filter_form.submit()

        # input incorrect marks for reg_no 4 and 5 in fixtures
        entry_form = page.forms['students-exams-entry-form']
        entry_form['4_marks'] = 100.00
        entry_form['5_marks'] = 'nan'
        page = entry_form.submit()
        self.assertContains(page, 'Marks for registration numbers (%s, %s) have errors.' % ('4', '5'))


class ExamReportsView(WebTest):
    '''
    Exam reports home. Renderes quick links to generate
    various exam reports and student result slips.
    '''

    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.exam_reports_home_view_url = reverse('exam_module:exam_reports_home')

    def test_requires_login(self):
        page = self.app.get(self.exam_reports_home_view_url)
        self.assertRedirects(
            page,
            self.login_url+'?next='+self.exam_reports_home_view_url
        )
    
    def test_the_required_links_displayed(self):
        page = self.app.get(self.exam_reports_home_view_url, user='staff')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, reverse('exam_module:generate_exam_reports'))


class GenerateExamReportsFilterFormTests(TestCase):
    '''
    A form to filter students to show report for, and
    the exam types used to compute the final grade.
    '''
    fixtures = ['student_profiles', 'streams', 'users']

    def test_form_with_no_data(self):
        form = ExamReportsFilterForm({})
        self.assertFalse(form.is_valid())
    
    def test_form_with_invalid_data(self):
        form = ExamReportsFilterForm({
            'form': 8,
            'stream': 'west',
            'subject': 'all',
            'exam_types': ['Opener']
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ['No students found in form %s %s.' %(8, 'west')])

    def test_form_with_valid_data(self):
        form = ExamReportsFilterForm({
            'form': 1,
            'stream': 'east',
            'subject': 'all',
            'exam_types': ['Opener', 'Mid Term', 'End Term'],
            'term': '1',
        })
        self.assertTrue(form.is_valid())

class GenerateExamReportsViewTests(WebTest):

    fixtures = ['student_profiles', 'streams', 'users', 'subjects', 'subjects_done_by_student']

    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.exam_reports_view_url = reverse('exam_module:generate_exam_reports')
    
    def test_requires_login(self):
        page = self.app.get(self.exam_reports_view_url)
        self.assertRedirects(
            page,
            self.login_url+'?next='+self.exam_reports_view_url
        )
    
    def test_filter_form_is_rendered(self):
        '''
        The form to apply filters should be rendered.
        '''
        page = self.app.get(self.exam_reports_view_url, user='staff')
        self.assertEqual(page.status_code, 200)
        self.assertTrue(len(page.forms) >= 1)
        self.assertEqual(page.form.action, self.exam_reports_view_url)
    
    def test_filter_view_with_no_data(self):
        '''
        All the fields are required.
        '''
        page = self.app.get(self.exam_reports_view_url, user='staff')
        page = page.form.submit()
        self.assertContains(page, 'This field is required')
    
    def test_filter_view_form_with_invalid_data(self):
        page = self.app.get(self.exam_reports_view_url, user='staff')
        page.form['form'] = 8
        page.form['stream'] = 'east'
        page.form['subject'] =  'all'
        page.form['exam_types'] = ['Opener', 'Mid Term']
        page = page.form.submit()
        self.assertContains(page, 'No students found in form %s %s.' % (8, 'east'))

    def test_filter_view_form_with_valid_data(self):
        page = self.app.get(self.exam_reports_view_url, user='staff')
        page.form['form'] = 2
        page.form['stream']  = 'west'
        page.form['subject']  = 'all'
        page.form['exam_types'] = ['Opener', 'Mid Term', 'End Term']
        page.form['term'] = 1
        page = page.form.submit()
        self.assertEqual(page.content_type, 'application/pdf')