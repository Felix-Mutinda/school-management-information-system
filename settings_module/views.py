from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from exam_module.models import (
    Subject,
    GradingSystem,
    ExamType,
    Term,
)

from accounts.models import (
    Stream,
)

from .forms import (
    AddSubjectForm,
    AddGradingSystemForm,
    AddExamTypeForm,
    AddTermForm,
    AddStreamForm,
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


class AddExamTypeView(LoginRequiredMixin, View):
    '''
    Adds an exam_type to db.
    '''
    form_class = AddExamTypeForm
    template_name = 'settings_module/add_exam_type.html'

    def get(self, request, *args, **kwargs):
        add_exam_type_form = self.form_class()
        exam_types = ExamType.objects.all()

        return render(request, self.template_name, {
            'add_exam_type_form': add_exam_type_form,
            'exam_types': exam_types,
        })
    
    def post(self, request, *args, **kwargs):
        add_exam_type_form = self.form_class(request.POST)
        exam_types = ExamType.objects.all()

        if add_exam_type_form.is_valid():
            add_exam_type_form.save()
            messages.success(request, 'Exam Type added successfully.')
            return redirect('settings_module:add_exam_type')

        return render(request, self.template_name, {
            'add_exam_type_form': add_exam_type_form,
            'exam_types': exam_types,
        })

# delete a given exam_type
@login_required
def delete_exam_type(request, exam_type_id):
    if request.method == 'GET':
        exam_type = get_object_or_404(ExamType, pk=exam_type_id)
        exam_type.delete()

        messages.error(request, 'Exam Type has been deleted.')
        return redirect('settings_module:add_exam_type')

class AddTermView(LoginRequiredMixin, View):
    '''
    Adds a term to db.
    '''
    form_class = AddTermForm
    template_name = 'settings_module/add_term.html'

    def get(self, request, *args, **kwargs):
        add_term_form = self.form_class()
        terms = Term.objects.all()

        return render(request, self.template_name, {
            'add_term_form': add_term_form,
            'terms': terms,
        })
    
    def post(self, request, *args, **kwargs):
        add_term_form = self.form_class(request.POST)
        terms = Term.objects.all()

        if add_term_form.is_valid():
            add_term_form.save()
            messages.success(request, 'Term added successfully.')
            return redirect('settings_module:add_term')

        return render(request, self.template_name, {
            'add_term_form': add_term_form,
            'terms': terms,
        })

# delete a given term
@login_required
def delete_term(request, term_id):
    if request.method == 'GET':
        term = get_object_or_404(Term, pk=term_id)
        term.delete()

        messages.error(request, 'Term has been deleted.')
        return redirect('settings_module:add_term')


class AddStreamView(LoginRequiredMixin, View):
    '''
    Adds a stream to db.
    '''
    form_class = AddStreamForm
    template_name = 'settings_module/add_stream.html'

    def get(self, request, *args, **kwargs):
        add_stream_form = self.form_class()
        streams = Stream.objects.all()

        return render(request, self.template_name, {
            'add_stream_form': add_stream_form,
            'streams': streams,
        })
    
    def post(self, request, *args, **kwargs):
        add_stream_form = self.form_class(request.POST)
        streams = Stream.objects.all()

        if add_stream_form.is_valid():
            add_stream_form.save()
            messages.success(request, 'Stream added successfully.')
            return redirect('settings_module:add_stream')

        return render(request, self.template_name, {
            'add_stream_form': add_stream_form,
            'streams': streams,
        })

# delete a given stream
@login_required
def delete_stream(request, stream_id):
    if request.method == 'GET':
        stream = get_object_or_404(Stream, pk=stream_id)
        stream.delete()

        messages.error(request, 'Stream has been deleted.')
        return redirect('settings_module:add_stream')
