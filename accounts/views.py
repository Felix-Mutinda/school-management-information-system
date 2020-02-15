from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth import get_user_model

from .forms import RegisterUserForm

User = get_user_model()

@login_required
def home(request):
    '''
    Take the user to home/dashboard
    '''
    return render(request, 'home.html', {})

@login_required
def register_staff(request):
    '''
    Show a form to register staff, save it if it's valid.
    '''
    form = RegisterUserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.is_staff = True
        user.save()
        return redirect(reverse('accounts:list_staff'))

    return render(request, 'accounts/register_staff.html', {
        'user_form': form,
    })


class ListStaffView(ListView):
    '''
    A list of all the staff members.
    '''
    template_name = 'accounts/list_staff.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        return User.objects.filter(is_staff=True)
    