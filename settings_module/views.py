from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from exam_module.models import (
    Subject,
)

from .forms import (
    AddSubjectForm,
)


class HomeView(LoginRequiredMixin, View):
    '''
    Home page.
    '''
    template_name = 'settings_module/home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class AddSubjectView(LoginRequiredMixin, View):
    '''
    Adds a subject to db.
    '''
    form_class = AddSubjectForm
    template_name = 'settings_module/add_subject.html'

    def get(self, request, *args, **kwargs):
        add_subject_form = self.form_class()
        subjects = Subject.objects.all()

        return render(request, self.template_name, {
            'add_subject_form': add_subject_form,
            'subjects': subjects,
        })
    
    def post(self, request, *args, **kwargs):
        add_subject_form = self.form_class(request.POST)
        subjects = Subject.objects.all()

        if add_subject_form.is_valid():
            add_subject_form.save()
            messages.success(request, 'Subject added successfully.')
            return redirect('settings_module:add_subject')

        return render(request, self.template_name, {
            'add_subject_form': add_subject_form,
            'subjects': subjects,
        })

# delete a given subject
@login_required
def delete_subject(request, subject_id):
    if request.method == 'GET':
        subject = get_object_or_404(Subject, pk=subject_id)
        subject.delete()

        messages.error(request, 'Subject has been deleted.')
        return redirect('settings_module:add_subject')