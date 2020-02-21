import datetime
from django import forms
from django.contrib.auth import (
    get_user_model,
    authenticate,
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field

from .models import (
    StaffProfile,
    StudentProfile
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
    student_reg_no = forms.CharField()
    student_first_name = forms.CharField()
    student_middle_name = forms.CharField(required=False)
    student_last_name = forms.CharField()
    student_form = forms.IntegerField(min_value=1)
    student_stream = forms.CharField()
    student_house = forms.CharField(required=False)
    student_kcpe_marks = forms.IntegerField(min_value=0, required=False)
    student_date_registered = forms.DateTimeField(initial=datetime.datetime.now())

    guardian_first_name = forms.CharField(required=False)
    guardian_middle_name = forms.CharField(required=False)
    guardian_last_name = forms.CharField(required=False)
    guardian_phone_number = forms.CharField(required=False)
    guardian_email = forms.CharField(required=False)

