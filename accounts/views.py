from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView
from django.contrib.auth import (
    get_user_model,
    authenticate,
    login,
    logout
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.utils.translation import gettext as _

from .forms import (
    RegisterUserForm,
    StaffLoginForm,
    StaffProfileForm,
    RegisterStudentForm
)

User = get_user_model()

class HomeView(LoginRequiredMixin, TemplateView):
    '''
    Take the user to home/dashboard
    '''
    template_name = 'home.html'

@login_required
def register_staff(request):
    '''
    Show a form to register staff(user and staff profile),
    save it if it's valid.
    '''
    user_form = RegisterUserForm(request.POST or None)
    staff_profile_form = StaffProfileForm(request.POST or None)
    if user_form.is_valid() and staff_profile_form.is_valid():
        user = user_form.save(commit=False)
        password = user_form.cleaned_data.get('password')
        user.set_password(password)
        user.is_staff = True
        user.save()
        staff_profile = staff_profile_form.save(commit=False)
        staff_profile.user = user
        staff_profile.save()
        return redirect(reverse('accounts:list_staff'))

    return render(request, 'accounts/register_staff.html', {
        'user_form': user_form,
        'staff_profile_form': staff_profile_form
    })

class ListStaffView(LoginRequiredMixin, ListView):
    '''
    A list of all the staff members.
    '''
    template_name = 'accounts/list_staff.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        return User.objects.filter(is_staff=True)

class StaffLoginView(View):
    '''
    Login the user. Must have is_staff = True.
    '''
    form_class = StaffLoginForm
    template_name = 'accounts/staff_login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            'form': form
        })
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_staff:
                    login(request, user)
                    return redirect(reverse('accounts:home'))
                else:
                    logout(request)
                    form.add_error(field=None, error=forms.ValidationError(
                        _('Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.'),
                        code='forbiden'
                    ))
        return render(request, self.template_name, {'form': form})


class RegisterStudentView(LoginRequiredMixin, View):
    '''
    Display a form to enter student data and those of a guardian.
    Adds the given student and guardian together with their respective
    profiles if they are valid.
    '''
    form_class = RegisterStudentForm
    template_name = 'accounts/register_student.html'

    def get(self, request, *args, **kwargs):
        '''
        Render the register student template.
        '''
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        '''
        Construct a student_user, student_profile and a guardian_user
        from the submitted form. Uses the created student_user to create
        the guardian profile 
        '''
        pass
