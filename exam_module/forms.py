from django import forms

from accounts.models import (
    StudentProfile,
)

from .models import (
    Subject,
    ExamType,
    Term
)

class CreateExamForm(forms.Form):
    '''
    Handle higher level validity i.e. required fields
    and Correct data type.
    '''
    student_reg_no = forms.CharField(max_length=20)
    subject_name = forms.CharField()
    exam_type_name = forms.CharField()
    term_name = forms.CharField()
    date_done = forms.DateTimeField()
    marks = forms.DecimalField(max_digits=4, decimal_places=2)

class CreateManyExamsFilterForm(forms.Form):
    '''
    Fields used to retrieve a group of students for 
    batch exam entry.
    '''
    form = forms.IntegerField()
    stream = forms.CharField()
    subject_name = forms.CharField()
    exam_type_name = forms.CharField()
    term_name = forms.CharField()
    date_done = forms.DateTimeField()

    def clean_subject_name(self):
        '''
        The given subject name should exist in db.
        '''
        if 'subject_name' in self.cleaned_data:
            subject_name = self.cleaned_data.get('subject_name')
            try:
                subject = Subject.objects.get(name=subject_name)
            except Subject.DoesNotExist:
                raise forms.ValidationError('This subject is not found.')
        
            return subject_name

    def clean_exam_type_name(self):
        '''
        The given exam type name should exist in db.
        '''
        if 'exam_type_name' in self.cleaned_data:
            exam_type_name = self.cleaned_data.get('exam_type_name')
            try:
                exam_type = ExamType.objects.get(name=exam_type_name)
            except ExamType.DoesNotExist:
                raise forms.ValidationError('This exam type is not found.')
        
            return exam_type_name

    def clean_term_name(self):
        '''
        The given term name should exist in db.
        '''
        if 'term_name' in self.cleaned_data:
            term_name = self.cleaned_data.get('term_name')
            try:
                term = Term.objects.get(name=term_name)
            except Term.DoesNotExist:
                raise forms.ValidationError('This term is not found.')
        
            return term_name

    def clean(self, *args, **kwargs):
        '''
        There should be students in the given form, stream on that
        particular date_done year.
        '''

        super(CreateManyExamsFilterForm, self).clean(*args, **kwargs)
        if 'date_done' in self.cleaned_data:
            date_done = self.cleaned_data.get('date_done')
            year_offset = date_done.year
            if 'form' in self.cleaned_data and 'stream' in self.cleaned_data:
                form = self.cleaned_data.get('form')
                stream = self.cleaned_data.get('stream')
                query_set = StudentProfile.objects.filter(stream=stream)
                students_list = [s for s in query_set if s.get_form(year_offset) == form]
                if not students_list:
                    raise forms.ValidationError(
                        'There are no students found in form %s %s in the year %s.' %(
                            form,
                            stream,
                            year_offset,
                        )
                    )