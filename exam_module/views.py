import decimal

from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib import messages

from accounts.models import StudentProfile

from .forms import (
    CreateExamForm,
    CreateManyExamsFilterForm,
)
from .models import (
    Subject,
    ExamType,
    Term,
    Exam,
)

class HomeView(LoginRequiredMixin, View):

    template_name = 'exam_module/home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class CreateOneExamView(LoginRequiredMixin, View):
    '''
    Handles creation of a single exam instance.
    '''
    form_class = CreateExamForm
    template_name = 'exam_module/create_one_exam.html'

    def get(self, request, *args, **kwargs):
        exam_form = self.form_class()
        return render(request, self.template_name, {'exam_form': exam_form})

    def post(self, request, *args, **kwargs):
        exam_form = self.form_class(request.POST)
        if exam_form.is_valid():
            student_reg_no = exam_form.cleaned_data.get('student_reg_no')
            subject_name = exam_form.cleaned_data.get('subject_name')
            exam_type_name = exam_form.cleaned_data.get('exam_type_name')
            term_name = exam_form.cleaned_data.get('term_name')
            date_done = exam_form.cleaned_data.get('date_done')
            marks = exam_form.cleaned_data.get('marks')
            try:
                student_profile = StudentProfile.objects.get(reg_no=student_reg_no)
                subject = Subject.objects.get(name=subject_name)
                exam_type = ExamType.objects.get(name=exam_type_name)
                term = Term.objects.get(name=term_name)
            except StudentProfile.DoesNotExist:
                exam_form.add_error('student_reg_no', 'A student with this registration number is not found.')
            except Subject.DoesNotExist:
                exam_form.add_error('subject_name', 'This subject is not found.')
            except ExamType.DoesNotExist:
                exam_form.add_error('exam_type_name', 'This exam type is not found.')
            except Term.DoesNotExist:
                exam_form.add_error('term_name', 'This term is not found.')
                
            else:
                create_exam_object(student_profile.reg_no, subject, exam_type, term, date_done, marks)
                messages.success(request, 'Data has been saved successfully.')
                return redirect(reverse('exam_module:create_one_exam'))

        return render(request, self.template_name, {'exam_form': exam_form})

class CreateManyExamsFilterView(LoginRequiredMixin, View):
    '''
    Apply filters to generate a list of students for a batch exam
    entry.
    '''
    form_class = CreateManyExamsFilterForm
    template_name = 'exam_module/create_many_exams.html'

    def get(self, request, *args, **kwargs):
        return redirect(reverse('exam_module:create_many_exams'))


    def post(self, request, *args, **kwargs):
        create_many_exams_filter_form = self.form_class(request.POST)
        if create_many_exams_filter_form.is_valid():
            form = create_many_exams_filter_form.cleaned_data.get('form')
            stream = create_many_exams_filter_form.cleaned_data.get('stream')
            date_done = create_many_exams_filter_form.cleaned_data.get('date_done')
            year_since_registration = date_done.year
            query_set = StudentProfile.objects.filter(stream=stream)
            student_list = [s for s in query_set if s.get_form(year_since_registration) == form]
            # if a student has marks already filled, read them. this will
            # be used to populate the students-exams-entry-form
            subject_name = create_many_exams_filter_form.cleaned_data.get('subject_name')
            exam_type_name = create_many_exams_filter_form.cleaned_data.get('exam_type_name')
            term_name = create_many_exams_filter_form.cleaned_data.get('term_name')
            student_list_with_marks = []
            for student in student_list:
                query_set = Exam.objects.filter(
                    student__reg_no=student.reg_no,
                    subject__name=subject_name,
                    exam_type__name=exam_type_name,
                    term__name=term_name,
                )
                student_list_with_marks.append((student, query_set[0].marks if query_set else 0))

            return render(request, self.template_name, {
                'create_many_exams_filter_form': create_many_exams_filter_form,
                'students_list_with_marks': student_list_with_marks,
            })
        return render(request, self.template_name, {
            'create_many_exams_filter_form': create_many_exams_filter_form,
            'students_list_with_marks': []
        })

class CreateManyExamsView(LoginRequiredMixin, View):
    '''
    Renders a filter form to get the students. To each student
    there corresponds a form to input an exam object.
    If valid this exam objects are populated in db.
    '''

    template_name = 'exam_module/create_many_exams.html'
    
    def get(self, request, *args, **kwargs):
        create_many_exams_filter_form = CreateManyExamsFilterForm()
        return render(request, self.template_name, {
            'create_many_exams_filter_form': create_many_exams_filter_form,
            'students_list_with_marks': [],
        })

    def post(self, request, *args, **kwargs):
        create_many_exams_filter_form = CreateManyExamsFilterForm(request.POST)
        student_reg_nos = [s[:-6] for s in request.POST.keys() if s.endswith('_marks')] # 'reg_no_marks'

        errors = []
        students_list_with_marks = []
        if create_many_exams_filter_form.is_valid():
            subject_name = request.POST['subject_name']
            exam_type_name = request.POST['exam_type_name']
            term_name = request.POST['term_name']
            date_done = request.POST['date_done']

            try:
                subject = Subject.objects.get(name=subject_name)
                exam_type = ExamType.objects.get(name=exam_type_name)
                term = Term.objects.get(name=term_name)
            except Exception: # catch all
                messages.error(request, 'A weird error has occured. Make sure you are sober while using this program.')
            else:
                for reg_no in student_reg_nos:
                    try:
                        student = StudentProfile.objects.get(reg_no=reg_no)
                        exam_object = create_exam_object(
                            student.reg_no,
                            subject,
                            exam_type,
                            term,
                            date_done,
                            marks=decimal.Decimal(request.POST['%s_marks' % reg_no])
                        )
                    except Exception: # catch all
                        errors.append(reg_no)
                    else:
                        # if all goes well get (student, marks)
                        students_list_with_marks.append((student, exam_object.marks))
                        
        if errors:
            messages.error(
                request,
                'Marks for registration numbers (%s) have errors.' %(', '.join(errors)) # reg_nos with errors
            )
        else:
            messages.success(request, 'Data has been saved successfully.')
                         
        return render(request, self.template_name, {
            'create_many_exams_filter_form': create_many_exams_filter_form,
            'students_list_with_marks': students_list_with_marks,
        })

# helper functions

# create and exam object
def create_exam_object(reg_no, subject, exam_type, term, date_done, marks):
    student_profile = StudentProfile.objects.get(reg_no=reg_no)
    # don't duplicate the exam object.
    try:
        exam_object = Exam.objects.get( # get to update
            student=student_profile,
            subject=subject,
            exam_type=exam_type,
            term=term,
        )
    except Exam.DoesNotExist:
        exam_object = Exam.objects.create( # create new
            student = student_profile,
            subject = subject,
            exam_type = exam_type,
            term = term,
            date_done = date_done,
            marks = marks
        )
    else:
        exam_object.date_done = date_done
        exam_object.marks = marks
        exam_object.save()
    
    return exam_object