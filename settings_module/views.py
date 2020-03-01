from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from exam_module.models import (
    Subject,
    GradingSystem,
)

from .forms import (
    AddSubjectForm,
    AddGradingSystemForm,
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

class AddGradingSystemView(LoginRequiredMixin, View):
    '''
    A grade corresponds to a greatest lower bound.
    '''
    form_class = AddGradingSystemForm
    template_name = 'settings_module/add_grading_system.html'

    def get(self, request, *args, **kwargs):

        add_grading_system_form = self.form_class()
        return render(request, self.template_name, {
            'add_grading_system_form': add_grading_system_form,
            'grading_systems': self.get_query_set(),
        })
    
    def post(self, request, *args, **kwargs):

        add_grading_system_form = self.form_class(request.POST)
        if add_grading_system_form.is_valid():
            add_grading_system_form.save()

            messages.success(request, 'Grading System updated successfully.')
            return redirect('settings_module:add_grading_system')

        return render(request, self.template_name, {
            'add_grading_system_form': add_grading_system_form,
            'grading_systems': self.get_query_set(),
        })

    def get_query_set(self):
        return GradingSystem.objects.all().order_by('-greatest_lower_bound')

@login_required
def delete_grading_system(request, grading_system_id):
    if request.method == 'GET':
        grading_system = get_object_or_404(GradingSystem, pk=grading_system_id)
        grading_system.delete()

        messages.error(request, 'Grading system entry has been deleted.')
        return redirect('settings_module:add_grading_system')