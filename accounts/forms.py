import datetime
from django import forms
from django.contrib.auth import (
    get_user_model,
    authenticate,
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field, Fieldset, Div

from .models import (
    StaffProfile,
    StudentProfile,
    Stream,
)

User = get_user_model()

class StaffLoginForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(StaffLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-signin'
        self.helper.form_method = 'post'
        self.helper.form_action = 'accounts:login'
        self.helper.layout = Layout(
            HTML(
                '''
                <img src="/static/img/logo2.jpg" alt="logo" width="120px" height="100px">
                <h1 class="h3 mb-3 font-weight-normal">Please sign in</h1>
                '''
            ),
            Field('username', placeholder='Username', autofocus='autofocus', autocomplete='off'),
            Field('password', placeholder='Password'),
            Submit('submit', 'Login', css_class='btn-lg btn-block'),
            HTML(
                '''
                <p class="mt-5 mb-3 text-muted">&copy; 2020</p>
                '''
            ),
        )
    
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user or not user.is_staff:
                raise forms.ValidationError('Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')
        
class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('username', wrapper_class='col'),
                Field('password', wrapper_class='col'),
                css_class='form-row',
            ),
            Div(
                Field('first_name', wrapper_class='col'),
                Field('middle_name', wrapper_class='col'),
                Field('last_name', wrapper_class='col'),
                css_class='form-row',
            ),
            Div(
                Field('phone_number', wrapper_class='col'),
                Field('email', wrapper_class='col'),
                css_class='form-row',
            ),
        )

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'phone_number'
        ]

class StaffProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('staff_id', wrapper_class='col'),
                Field('position', wrapper_class='col'),
                css_class='form-row',
            )
        )

    class Meta:
        model = StaffProfile
        fields = [
            'staff_id',
            'position'
        ]

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'reg_no',
            'form',
            'stream',
            'kcpe_marks',
            'house',
            'date_registered'
        ]
        error_messages = {
            'reg_no': {
                'unique': 'This registration number is already taken.'
            }
        }

class RegisterStudentForm(forms.Form):
    '''
    A student registration form. Accepts fields for student_user,
    student_profile, guardian_user
    '''
    def __init__(self, *args, **kwargs):
        super(RegisterStudentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'accounts:register_student'
        self.helper.form_class = 'form-register-student'
        self.helper.layout = Layout(
            Fieldset(
                'Register Student',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Fieldset(
                    'Student Details',
                    Field('student_reg_no', autofocus='autofocus'),
                    Div(
                        Field('student_first_name', wrapper_class='col'),
                        Field('student_middle_name', wrapper_class='col'),
                        Field('student_last_name', wrapper_class='col'),
                        css_class='form-row',
                    ),
                    Div(
                        Field('student_form', wrapper_class='col'),
                        Field('student_stream_name', wrapper_class='col'),
                        Field('student_house', wrapper_class='col'),
                        css_class='form-row',
                    ),
                    Div(
                        Field('student_kcpe_marks', wrapper_class='col'),
                        Field('student_date_registered', wrapper_class='col'),
                        css_class='form-row',
                    ),
                    css_class='p-2 mb-2 border rounded',
                ),
                Fieldset(
                    'Parent/Guardian Details',
                    Div(
                        Field('guardian_first_name', wrapper_class='col'),
                        Field('guardian_middle_name', wrapper_class='col'),
                        Field('guardian_last_name', wrapper_class='col'),
                        css_class='form-row',
                    ),
                    Div(
                        Field('guardian_phone_number', wrapper_class='col'),
                        Field('guardian_email', wrapper_class='col'),
                        css_class='form-row',
                    ),
                    css_class='p-2 mb-2 border rounded',
                ),
                Submit('submit', 'Save Details', css_class='btn btn-primary'),
                css_class='p-3 border rounded',
            ),
        )


    student_reg_no = forms.CharField(label='Registration/ Admission Number')
    student_first_name = forms.CharField(label='First Name')
    student_middle_name = forms.CharField(label='Middle Name', required=False)
    student_last_name = forms.CharField(label='Sir Name')
    student_form = forms.IntegerField(label='Form/ Class', min_value=1)
    student_stream_name = forms.CharField(label='Stream')
    student_house = forms.CharField(label='Domitory/ House', required=False)
    student_kcpe_marks = forms.IntegerField(label='KCPE Marks', min_value=0, required=False)
    student_date_registered = forms.DateTimeField(label='Date Registered', initial=datetime.datetime.now())

    guardian_first_name = forms.CharField(label='First Name', required=False)
    guardian_middle_name = forms.CharField(label='Middle Name', required=False)
    guardian_last_name = forms.CharField(label='Sir Name', required=False)
    guardian_phone_number = forms.CharField(label='Phone Number', required=False)
    guardian_email = forms.CharField(label='Email', required=False)

    def clean_student_stream_name(self):
        stream_name = self.cleaned_data.get('student_stream_name')
        try:
            stream = Stream.objects.get(pk=stream_name)
        except Stream.DoesNotExist:
            raise forms.ValidationError('This stream is not found.')
        return stream_name


class GenerateClassListForm(forms.Form):
    '''
    Validate the form and stream used to generate a class
    list.
    '''
    form = forms.IntegerField(label='Form/ Class')
    stream_name = forms.CharField(label='Stream')
    file_type = forms.ChoiceField(label='Choose File Type', widget=forms.RadioSelect, choices=(('0', 'PDF'), ('1', 'EXCEL')))

    def clean_stream_name(self):
        stream_name = self.cleaned_data.get('stream_name')
        try:
            Stream.objects.get(pk=stream_name)
        except Stream.DoesNotExist:
            raise forms.ValidationError('This stream is not found.')

        return stream_name
    
    def clean(self, *args, **kwargs):
        super(GenerateClassListForm, self).clean(*args, **kwargs)
        form = self.cleaned_data.get('form', '')
        stream_name = self.cleaned_data.get('stream_name', '')
        if form and stream_name:
            query_set = StudentProfile.objects.filter(stream__pk=stream_name)
            students_list = [s for s in query_set if s.get_form() == form]
            if not students_list:
                raise forms.ValidationError('No students found in form %s %s.' %(form, stream_name))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'accounts:generate_class_list'
        self.helper.form_id = 'generate-class-list-form'
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
                    Field('stream_name', wrapper_class='col'),
                    css_class='form-row',
                ),
                Div(
                    Field('file_type', wrapper_class='col'),
                    css_class='form-row',
                ),
                Submit('submit', 'Generate', css_class='btn btn-primary'),
                css_class='border rounded p-3',
            )
        )