from django import forms

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
    