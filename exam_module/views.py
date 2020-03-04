import decimal, datetime

from django import forms
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    HTML,
    Field,
    Submit,
)

from fpdf import FPDF

from accounts.models import StudentProfile

from .forms import (
    CreateExamForm,
    CreateManyExamsFilterForm,
    ExamReportsFilterForm
)
from .models import (
    Subject,
    ExamType,
    Term,
    Exam,
    SubjectsDoneByStudent,
)
from .utils import get_grade


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
            query_set = StudentProfile.objects.filter(stream__name=stream)
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

class ExamReportsView(LoginRequiredMixin, View):
    '''
    exam reports home
    '''
    template_name = 'exam_module/exam_reports_home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class GenerateExamReportsView(LoginRequiredMixin, View):
    '''
    Generate exam reports based on filters passed by the user.
    '''
    form_class = ExamReportsFilterForm
    template_name = 'exam_module/generate_exam_reports.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            'exam_reports_filter_form': form
        })
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            f = form.cleaned_data.get('form')
            stream_name = form.cleaned_data.get('stream')
            subject_name = form.cleaned_data.get('subject')
            exam_types_names = form.cleaned_data.get('exam_types')
            term_name = form.cleaned_data.get('term')

            # get students
            year_offset = datetime.datetime.now().year
            if stream_name == 'all':
                query_set = StudentProfile.objects.all()
            else:
                query_set = StudentProfile.objects.filter(stream__name=stream_name)
            students_list = [s for s in query_set if s.get_form(year_offset) == f]

            # pdf
            pdf = FPDF()
            pdf.add_page()

            # Effective page width, or just epw
            epw = pdf.w - 2*pdf.l_margin

            # table title
            title = 'Form %d %s Exam Report' % (f, stream_name.capitalize() if stream_name != 'all' else '')
            subtitle1 = 'Term %s: (%s)' % (term_name, ', '.join(exam_types_names))
            subtitle2 = 'Subjects: %s' % (subject_name.capitalize())
            pdf.set_font('Times', 'B', 16)
            th = pdf.font_size # text height
            pdf.cell(epw, th+1, title, align='C', ln=1)
            pdf.set_font('Times', 'B', 12)
            th = pdf.font_size
            pdf.cell(epw, th+0.5, subtitle1, align='C', ln=1)
            pdf.cell(epw, th+0.5, subtitle2, align='C', ln=1)
            pdf.ln(4)

            # table body
            tmp = []
            if subject_name == 'all': # report for all subjects
                pass
            else: # report for a particular subject
                # get students who do that subject
                students_list = [s for s in students_list if subject_name in [sd.subject.name for sd in SubjectsDoneByStudent.objects.filter(student=s)]]
                for student in students_list:
                    exam_objects = Exam.objects.filter(
                        student=student,
                        subject__name=subject_name,
                        term__name=term_name,
                    )
                    tmp_entry = { 
                        'student': student,
                        'exam_objects': [],
                        'total': 0.0,
                    }
                    for exam_object in exam_objects:
                        if exam_object.exam_type.name in exam_types_names:
                            tmp_entry['exam_objects'].append(exam_object)
                            tmp_entry['total'] += float(exam_object.marks)
                    tmp.append(tmp_entry)
                # sort tmp
                tmp.sort(key=lambda t: t['total'], reverse=True)
                
                # output tmp
                # thead
                tet = len(exam_types_names) # total exam types names
                pdf.set_font('Times', 'B', 13); th = pdf.font_size # text height
                pdf.cell(epw*0.05, th, 'No.', border=1, align='C') # 0.5% of epw
                pdf.cell(epw*0.10, th, 'Reg No.', border=1, align='C')
                pdf.cell(epw*0.30, th, 'Name', border=1, align='C')
                for exam_type_name in exam_types_names:
                    pdf.cell(epw*(0.40/tet), th, exam_type_name, border=1, align='C')
                pdf.cell(epw*(0.15/2), th, 'Avg.', border=1, align='C')
                pdf.cell(epw*(0.15/2), th, 'Grade', border=1, align='C')
                pdf.ln(th)

                # tbody
                for i,v in enumerate(tmp):
                    pdf.set_font('Times', '', 12); th = pdf.font_size
                    pdf.cell(epw*0.05, th, str(i+1), border=1) # 0.5% of epw
                    pdf.cell(epw*0.10, th, v['student'].reg_no, border=1)
                    u = v['student'].user
                    pdf.cell(epw*0.30, th, '%s %s %s' %(u.first_name, u.middle_name, u.last_name), border=1)
                    for exam_type_name in exam_types_names:
                        marks = 0.0 # get marks
                        for exam_object in v['exam_objects']:
                            if exam_object.exam_type.name == exam_type_name:
                                marks = exam_object.marks
                                break
                        pdf.cell(epw*(0.40/tet), th, str(marks), border=1, align='C')
                    avg = round(v['total'] / tet, 2) # compute avegare
                    pdf.cell(epw*(0.15/2), th, str(avg), border=1, align='C')
                    pdf.cell(epw*(0.15/2), th, get_grade(avg), border=1, align='C') # use get_grade utility
                    pdf.ln(th)


            response = HttpResponse(pdf.output(dest='S').encode('latin-1'))
            response['Content-Type'] = 'application/pdf'

            
            response['Content-Disposition'] = 'inline; filename="%s.pdf"' %(title)

            messages.success(request, 'Exam report has been generated.')
            return response

        return render(request, self.template_name, {
            'exam_reports_filter_form': form
        })