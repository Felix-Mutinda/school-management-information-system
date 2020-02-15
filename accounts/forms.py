from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

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