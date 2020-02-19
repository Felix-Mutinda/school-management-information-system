from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib import messages

from accounts.models import StudentProfile

from .forms import (
    CreateExamForm
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
                Exam.objects.create(
                    student = student_profile,
                    subject = subject,
                    exam_type = exam_type,
                    term = term,
                    date_done = date_done,
                    marks = marks
                )
                messages.success(request, 'Data has been saved successfully.')
                return redirect(reverse('exam_module:create_one_exam'))

        return render(request, self.template_name, {'exam_form': exam_form})