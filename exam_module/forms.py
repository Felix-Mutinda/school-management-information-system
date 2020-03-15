import datetime

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Div,
    Field,
    Submit,
    Fieldset,
    HTML,
)

from accounts.models import (
    StudentProfile,
    Stream,
)

from .models import (
    Subject,
    ExamType,
    Term,
    SubjectsDoneByStudent,
)

from .utils import get_objects_as_choices

# use html5 type="date"
class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        kwargs['format'] = '%Y-%m-%d'
        super().__init__(**kwargs)

class CreateExamForm(forms.Form):
    '''
    Handle higher level validity i.e. required fields
    and Correct data type.
    '''
    student_reg_no = forms.CharField(label="Student Registration Number", max_length=20)
    subject_name = forms.ModelChoiceField(label="Subject", widget=forms.Select, queryset=Subject.objects, empty_label=None, to_field_name='name')
    exam_type_name = forms.ModelChoiceField(label="Exam Type", widget=forms.Select, queryset=ExamType.objects,  empty_label=None, to_field_name='name')
    term_name = forms.ModelChoiceField(label="Term", widget=forms.Select, queryset=Term.objects, empty_label=None, to_field_name='name')
    date_done = forms.DateField(widget=DateInput, initial=datetime.date.today())
    marks = forms.DecimalField(max_digits=4, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(CreateExamForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'exam_module:create_one_exam'
        self.helper.layout = Layout(
            Fieldset(
                'Student Exam Entry',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Field('student_reg_no', autofocus='autofocues'),
                Div(
                    Field('subject_name', wrapper_class='col'),
                    Field('exam_type_name', wrapper_class='col'),
                    css_class='form-row',
                ),
                Div(
                    Field('term_name', wrapper_class='col'),
                    Field('date_done', wrapper_class='col'),
                    css_class='form-row',
                ),
                Field('marks'),
                Submit('submit', 'Save', css_class='btn btn-primary'),
                css_class='p-3 border rounded',
            )
        )
    
    # validations, all passed in values should exist in db

    def clean_student_reg_no(self):
        student_reg_no = self.cleaned_data.get('student_reg_no')
        try:
            student_profile = StudentProfile.objects.get(reg_no=student_reg_no)
        except StudentProfile.DoesNotExist:
            raise forms.ValidationError('A student with this registration number is not found.')
        return student_reg_no

    def clean_subject_name(self):
        subject_name = self.cleaned_data.get('subject_name')
        if subject_name.name == 'All':
            raise forms.ValidationError('Select a single subject.')
            
        try:
            subject = Subject.objects.get(name=subject_name)
        except Subject.DoesNotExist:
            raise forms.ValidationError('This subject is not found.')
        return subject_name
    
    def clean_exam_type_name(self):
        exam_type_name = self.cleaned_data.get('exam_type_name')
        try:
            exam_type = ExamType.objects.get(name=exam_type_name)
        except ExamType.DoesNotExist:
            raise forms.ValidationError('This exam type is not found.')
        return exam_type_name
    
    def clean_term_name(self):
        term_name = self.cleaned_data.get('term_name')
        try:
            term = Term.objects.get(name=term_name)
        except Term.DoesNotExist:
            raise forms.ValidationError('This term is not found.')
        return term_name
        
    

class CreateManyExamsFilterForm(forms.Form):
    '''
    Fields used to retrieve a group of students for 
    batch exam entry.
    '''
    form = forms.IntegerField()
    stream = forms.ModelChoiceField(widget=forms.Select, queryset=Stream.objects, empty_label=None, to_field_name='name')
    subject_name = forms.ModelChoiceField(label='Subject', widget=forms.Select, queryset=Subject.objects, empty_label=None, to_field_name='name')
    exam_type_name = forms.ModelChoiceField(label='Exam Type', widget=forms.Select, queryset=ExamType.objects, empty_label=None, to_field_name='name')
    term_name = forms.ModelChoiceField(label='Term', widget=forms.Select, queryset=Term.objects, empty_label=None, to_field_name='name')
    date_done = forms.DateField(label='Date Done', widget=DateInput, initial=datetime.date.today())

    def __init__(self, *args, **kwargs):
        '''
        Initialize crispy form helper
        '''
        super(CreateManyExamsFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'exam_module:create_many_exams_filter'
        self.helper.form_id = 'filter-exams-form'
        self.helper.layout = Layout(
            Fieldset(
                'Filter Tags',
                Div(
                    Field('form', wrapper_class='col'),
                    Field('stream', wrapper_class='col'),
                    Field('subject_name', wrapper_class='col'),
                    css_class='form-row',
                ),
                Div(
                    Field('exam_type_name', wrapper_class='col'),
                    Field('term_name', wrapper_class='col'),
                    Field('date_done', wrapper_class='col'),
                    css_class='form-row',
                ),
                Submit(
                    'submit',
                    'Filter',
                    css_class='btn btn-primary',
                ),
                css_class='p-3 border',
            ),
        )

    def clean_subject_name(self):
        '''
        The given subject name should exist in db.
        '''
        subject_name = self.cleaned_data.get('subject_name')
        try:
            subject = Subject.objects.get(name=subject_name)
        except Subject.DoesNotExist:
            raise forms.ValidationError('This subject is not found.')
    
        return subject_name

    def clean_exam_type_name(self):
        '''
        The given exam type name should exist in db.
        '''
        exam_type_name = self.cleaned_data.get('exam_type_name')
        try:
            exam_type = ExamType.objects.get(name=exam_type_name)
        except ExamType.DoesNotExist:
            raise forms.ValidationError('This exam type is not found.')
    
        return exam_type_name

    def clean_term_name(self):
        '''
        The given term name should exist in db.
        '''
        term_name = self.cleaned_data.get('term_name')
        try:
            term = Term.objects.get(name=term_name)
        except Term.DoesNotExist:
            raise forms.ValidationError('This term is not found.')
    
        return term_name

    def clean(self, *args, **kwargs):
        '''
        There should be students in the given form, stream on that
        particular date_done year.
        '''

        super(CreateManyExamsFilterForm, self).clean(*args, **kwargs)
        if 'date_done' in self.cleaned_data:
            date_done = self.cleaned_data.get('date_done')
            year_offset = date_done.year
            if 'form' in self.cleaned_data and 'stream' in self.cleaned_data:
                form = self.cleaned_data.get('form')
                stream = self.cleaned_data.get('stream')
                query_set = StudentProfile.objects.filter(stream__name=stream)
                students_list = [s for s in query_set if s.get_form(year_offset) == form]
                if not students_list:
                    raise forms.ValidationError(
                        'There are no students found in form %s %s in the year %s.' %(
                            form,
                            stream,
                            year_offset,
                    ))
                    
                # if no students taking that subject also raise a validation error
                subject_name = self.cleaned_data.get('subject_name', '')
                if subject_name:
                    students_list = [s for s in students_list if subject_name in [sd.subject for sd in SubjectsDoneByStudent.objects.filter(student=s)]]
                    if not students_list:
                        raise forms.ValidationError(
                            'No students in form %d %s taking %s.' % (form, stream, subject_name)
                        )

class ExamReportsFilterForm(forms.Form):
    '''
    Used to apply filters to get students, and specify exam types
    used to compute the student final grade.
    '''
    form = forms.IntegerField()
    stream = forms.ModelChoiceField(widget=forms.Select, queryset=Stream.objects, empty_label=None, to_field_name='name')
    subject = forms.ModelChoiceField(widget=forms.Select, queryset=Subject.objects, empty_label=None, to_field_name='name')
    exam_types = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=ExamType.objects, to_field_name='name')
    term = forms.ModelChoiceField(widget=forms.Select, queryset=Term.objects, empty_label=None, to_field_name='name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'exam-reports-filter-form'
        self.helper.form_method  = 'post'
        self.helper.form_action = 'exam_module:generate_exam_reports'
        self.helper.layout = Layout(
            Fieldset(
                'Filter Tags',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Div(
                    Field('form', wrapper_class='col'),
                    Field('stream', wrapper_class='col'),
                    css_class='form-row',
                ),
                Div(
                    Field('subject', wrapper_class='col'),
                    Field('term', wrapper_class='col'),
                    css_class='form-row',
                ),
                Field('exam_types'),
                Submit('submit', 'Generate', css_class='btn btn-primary'),
                css_class='p-3 border rounded',
            )
        )
    
    def clean(self, *args, **kwargs):
        '''
        There should be students in the given form, stream on that
        particular date_done year.
        '''

        super().clean(*args, **kwargs)
        year_offset = datetime.datetime.now().year
        if 'form' in self.cleaned_data and 'stream' in self.cleaned_data:
            form = self.cleaned_data.get('form')
            stream = self.cleaned_data.get('stream')
            if stream.name == 'All':
                query_set = StudentProfile.objects.all()
            else:
                query_set = StudentProfile.objects.filter(stream__name=stream)
            students_list = [s for s in query_set if s.get_form(year_offset) == form]
            if not students_list:
                raise forms.ValidationError(
                    'No students found in form %s %s.' %(
                        form,
                        stream,
                    )
                )
            
            # if no students taking that subject also raise a validation error
            subject = self.cleaned_data.get('subject', '')
            if subject and subject.name != 'All':
                students_list = [s for s in students_list if subject in [sd.subject for sd in SubjectsDoneByStudent.objects.filter(student=s)]]
                if not students_list:
                    raise forms.ValidationError(
                        'No students in form %d %s taking %s.' % (form, stream, subject.name)
                    )

class GenerateResultsSlipPerStudentFilterForm(forms.Form):
    '''
    Specify the reg_no of the student.
    '''
    reg_no = forms.CharField(label='Registration Number')
    exam_types_names = forms.ModelMultipleChoiceField(label='Exam Types', widget=forms.CheckboxSelectMultiple, queryset=ExamType.objects, to_field_name='name')
    term_name = forms.ModelChoiceField(label='Term', widget=forms.Select, queryset=Term.objects, empty_label=None, to_field_name='name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'exam_module:generate_results_slip_per_student'
        self.helper.form_method = 'get'
        self.helper.form_id = 'generate-results-slip-per-student-filter-form'
        self.helper.layout = Layout(
            Fieldset(
                'Filter Tags',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Field('reg_no'),
                Div(
                    Field('term_name', wrapper_class='col'),
                    Field('exam_types_names', wrapper_class='col'),
                    css_class='form-row',
                ),
                Submit('submit', 'Generate', css_class='btn btn-primary'),
                css_class='p-3 border rounded',
            )
        )

    def clean_reg_no(self):
        reg_no = self.cleaned_data.get('reg_no')
        try:
            StudentProfile.objects.get(reg_no=reg_no)
        except StudentProfile.DoesNotExist:
            raise forms.ValidationError('No student with this registration number is found.')
        return reg_no

class GenerateResultsSlipPerClassFilterForm(forms.Form):
    '''
    A form to specify filter tags to print results slip 
    for several student.
    '''
    form = forms.IntegerField()
    stream = forms.ModelChoiceField(widget=forms.Select, queryset=Stream.objects, empty_label=None, to_field_name='name')
    exam_types_names = forms.ModelMultipleChoiceField(label='Exam Types', widget=forms.CheckboxSelectMultiple, queryset=ExamType.objects, to_field_name='name')
    term_name = forms.ModelChoiceField(label='Term', widget=forms.Select, queryset=Term.objects, empty_label=None, to_field_name='name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'exam_module:generate_results_slip_per_class'
        self.helper.form_method = 'get'
        self.helper.form_id = 'generate-results-slip-per-class-filter-form'
        self.helper.layout = Layout(
            Fieldset(
                'Filter Tags',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Div(
                    Field('form', wrapper_class='col'),
                    Field('stream', wrapper_class='col'),
                    css_class='form-row',
                ),
                Div(
                    Field('term_name', wrapper_class='col'),
                    Field('exam_types_names', wrapper_class='col'),
                    css_class='form-row',
                ),
                Submit('submit', 'Generate', css_class='btn btn-primary'),
                css_class='p-3 border rounded',
            )
        )
    
    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        form = self.cleaned_data.get('form', '')
        stream_name = self.cleaned_data.get('stream', '')
        if form and stream_name:
            if stream_name.name == 'All':
                query_set = StudentProfile.objects.all()
            else:
                query_set = StudentProfile.objects.filter(stream__name=stream_name)
            students_list = [s for s in query_set if s.get_form() == form]
            if not students_list:
                raise forms.ValidationError(
                    'No students found in form %s %s.' % (form, stream_name)
                )