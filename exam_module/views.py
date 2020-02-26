import decimal

from django import forms
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib import messages

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    HTML,
    Field,
    Submit,
)

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
            # read the cleaned values
            student_reg_no = exam_form.cleaned_data.get('student_reg_no')
            subject_name = exam_form.cleaned_data.get('subject_name')
            exam_type_name = exam_form.cleaned_data.get('exam_type_name')
            term_name = exam_form.cleaned_data.get('term_name')
            date_done = exam_form.cleaned_data.get('date_done')
            marks = exam_form.cleaned_data.get('marks')

            # create instances
            student_profile = StudentProfile.objects.get(reg_no=student_reg_no)
            subject = Subject.objects.get(name=subject_name)
            exam_type = ExamType.objects.get(name=exam_type_name)
            term = Term.objects.get(name=term_name)
            
            # create the exam object and redirect
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

            # get students in the given form and stream.
            # form is determined using date_done.year 
            year_since_registration = date_done.year
            query_set = StudentProfile.objects.filter(stream=stream)
            student_list = [s for s in query_set if s.get_form(year_since_registration) == form]

            subject_name = create_many_exams_filter_form.cleaned_data.get('subject_name')
            exam_type_name = create_many_exams_filter_form.cleaned_data.get('exam_type_name')
            term_name = create_many_exams_filter_form.cleaned_data.get('term_name')

            # Create a runtime students-exams-entry-form.
            # Embed the subject_name, exam_type_name, term_name and date_done
            # from filter view as hidden inputs. This will be needed to create
            # the exam object later
            
            # students_exams_entry_form as f
            f = forms.Form()
            f.fields['form'] = forms.CharField(widget=forms.HiddenInput(attrs={'value': form}))
            f.fields['stream'] = forms.CharField(widget=forms.HiddenInput(attrs={'value': stream}))
            f.fields['subject_name'] = forms.CharField(widget=forms.HiddenInput(attrs={'value': subject_name}))
            f.fields['exam_type_name'] = forms.CharField(widget=forms.HiddenInput(attrs={'value': exam_type_name}))
            f.fields['term_name'] = forms.CharField(widget=forms.HiddenInput(attrs={'value': term_name}))
            f.fields['date_done'] = forms.CharField(widget=forms.HiddenInput(attrs={'value': str(date_done)[:-6]}))

            # instantiate crispy_forms helper
            f.helper = FormHelper()
            f.helper.form_method = 'post'
            f.helper.form_action = 'exam_module:create_many_exams'
            f.helper.form_id = 'students-exams-entry-form'
            layout_components = [] #  Pack all layouts items here

            for student in student_list:
                # read the corresponding exam object if it exists.
                exam_object = get_object_or_none(
                    Exam,
                    student__reg_no=student.reg_no,
                    subject__name=subject_name,
                    exam_type__name=exam_type_name,
                    term__name=term_name,
                )
                # Add a number field, 'reg_no'_marks for each student. Populated with existing
                # value or 0 otherwise
                f.fields['%s_marks' %(student.reg_no)] = forms.CharField(widget=forms.NumberInput(attrs={
                    'id': 'id_%s_marks' %(student.reg_no),
                    'value': exam_object.marks if exam_object else 0,
                    'min': 0,
                    'max': 99.99,
                    'step': 0.01,
                    'class': 'marks'
                }), label='')

                # create a layout component
                layout_components.extend([
                    HTML(
                        '''
                        <tr>
                            <td>%s</td>
                            <td>%s %s %s</td>
                            <td>
                        '''%(student.reg_no,student.user.first_name,student.user.middle_name,student.user.last_name),
                    ),
                    Field(
                        '%s_marks'%(student.reg_no),
                    ),
                    HTML(
                        '''
                            </td>
                        </tr>
                        '''
                    )
                ])
            
            # create the final layout
            f.helper.layout = Layout(
                # include the hidden fields
                'form', 'stream', 'subject_name', 'exam_type_name', 'term_name', 'date_done',
                # unpack the above components
                *layout_components,
                # submit button inside a <tr>
                HTML(
                    '''
                    <tr>
                        <td colspan="3">
                    '''
                ),
                Submit('submit', 'Save Changes', css_class='btn btn-primary'),
                HTML(
                    '''
                        </td>
                    </tr>
                    '''
                )
            )
                

            return render(request, self.template_name, {
                'create_many_exams_filter_form': create_many_exams_filter_form,
                'students_exams_entry_form': f,
            })
        return render(request, self.template_name, {
            'create_many_exams_filter_form': create_many_exams_filter_form,
            'students_exams_entry_form': None
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
            'students_exams_entry_form': None,
        })

    def post(self, request, *args, **kwargs):
        create_many_exams_filter_form = CreateManyExamsFilterForm(request.POST)
        student_reg_nos = [s[:-6] for s in request.POST.keys() if s.endswith('_marks')] # 'reg_no_marks'

        errors = [] # list of all students whose marks have issues
        if create_many_exams_filter_form.is_valid():
            subject_name = request.POST['subject_name']
            exam_type_name = request.POST['exam_type_name']
            term_name = request.POST['term_name']
            date_done = request.POST['date_done']

            # form is valid, we can read them
            subject = Subject.objects.get(name=subject_name)
            exam_type = ExamType.objects.get(name=exam_type_name)
            term = Term.objects.get(name=term_name)
            
            # save marks to corresponding student
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

            # show messages              
            if errors:
                messages.error(
                    request,
                    'Marks for registration numbers (%s) have errors.' %(', '.join(errors)) # reg_nos with errors
                )
            else:
                messages.success(request, 'Data has been saved successfully.')
                r = CreateManyExamsFilterView() # workaround a redirect
                return r.post(request)
        
        return render(request, self.template_name, {
            'create_many_exams_filter_form': create_many_exams_filter_form,
            'students_list_with_marks': None,
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
    except Exam.DoesNotExist: # then
        exam_object = Exam.objects.create( # create new
            student = student_profile,
            subject = subject,
            exam_type = exam_type,
            term = term,
            date_done = date_done,
            marks = marks
        )
    else: # update the existing
        exam_object.date_done = date_done
        exam_object.marks = marks
        exam_object.save()
    
    return exam_object

def get_object_or_none(model, **kwargs):
    '''
    Return the object from models that matches the given
    kwargs, None if none is found.
    '''
    try:
        obj = model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None
    return obj