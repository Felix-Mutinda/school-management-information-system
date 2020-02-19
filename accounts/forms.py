import datetime
from django import forms
from django.contrib.auth import (
    get_user_model,
    authenticate,
)

from .models import (
    StaffProfile,
    StudentProfile
)

User = get_user_model()

class StaffLoginForm(forms.Form):
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

