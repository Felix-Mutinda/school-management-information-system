from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    '''
    Take the user to home/dashboard
    '''
    return render(request, 'home.html', {})