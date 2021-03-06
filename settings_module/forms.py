from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Fieldset,
    Field,
    HTML,
    Submit,
)

from exam_module.models import (
    Subject,
    GradingSystem,
    ExamType,
    Term,
)

from accounts.models import (
    Stream,
)

class AddSubjectForm(forms.ModelForm):
    name =  forms.CharField(label='Subject Name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'settings_module:add_subject'
        self.helper.form_id = 'add-subject-form'
        self.helper.layout = Layout(
            Fieldset(
                'Add Subject',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Field(
                    'name'
                ),
                Submit('submit', 'Add', css_class='btn btn-primary'),
                css_class='p-3 border rounded' # fieldset
            )
        )

    class Meta:
        model = Subject
        fields = [
            'name',
        ]
    
    def clean_name(self):
        '''
        Lower then capitalize the field value to be saved in db.
        '''
        return self.cleaned_data.get('name').lower().capitalize()

class AddGradingSystemForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'settings_module:add_grading_system'
        self.helper.form_id = 'add-grading-system-form'
        self.helper.layout = Layout(
            Fieldset(
                'Grading Sytem',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Field(
                    'grade'
                ),
                Field(
                    'greatest_lower_bound'
                ),
                Submit('submit', 'Save', css_class='btn btn-primary'),
                css_class='p-3 border rounded' # fieldset
            )
        )

    class Meta:
        model = GradingSystem
        fields = [
            'grade',
            'greatest_lower_bound',
        ]

        error_messages = {
            'grade': {
                'unique': 'This grade already exists.'
            },

            'greatest_lower_bound': {
                'unique': 'This greatest lower bound is already associated with a grade.'
            }
        }

    def clean_grade(self):
        '''
        To ensure uniqueness, grades are saved uppercase.
        '''
        return self.cleaned_data.get('grade').upper()


class AddExamTypeForm(forms.ModelForm):
    name =  forms.CharField(label='Exam Type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'settings_module:add_exam_type'
        self.helper.form_id = 'add-exam-type-form'
        self.helper.layout = Layout(
            Fieldset(
                'Add Exam Type',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Field(
                    'name'
                ),
                Submit('submit', 'Add', css_class='btn btn-primary'),
                css_class='p-3 border rounded' # fieldset
            )
        )

    class Meta:
        model = ExamType
        fields = [
            'name',
        ]
    
    def clean_name(self):
        '''
        Lower then capitalize the field value to be saved in db.
        '''
        return self.cleaned_data.get('name').lower().capitalize()


class AddTermForm(forms.ModelForm):
    name =  forms.CharField(label='Term')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'settings_module:add_term'
        self.helper.form_id = 'add-term-form'
        self.helper.layout = Layout(
            Fieldset(
                'Add Term',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Field(
                    'name'
                ),
                Submit('submit', 'Add', css_class='btn btn-primary'),
                css_class='p-3 border rounded' # fieldset
            )
        )

    class Meta:
        model = Term
        fields = [
            'name',
        ]
    
    def clean_name(self):
        '''
        Lower then capitalize the field value to be saved in db.
        '''
        return self.cleaned_data.get('name').lower().capitalize()

class AddStreamForm(forms.ModelForm):
    name =  forms.CharField(label='Stream')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'settings_module:add_stream'
        self.helper.form_id = 'add-stream-form'
        self.helper.layout = Layout(
            Fieldset(
                'Add Stream',
                HTML(
                    '''
                    {% include '_messages.html' %}
                    '''
                ),
                Field(
                    'name'
                ),
                Submit('submit', 'Add', css_class='btn btn-primary'),
                css_class='p-3 border rounded' # fieldset
            )
        )

    class Meta:
        model = Stream
        fields = [
            'name',
        ]
    
    def clean_name(self):
        '''
        Lower then capitalize the field value to be saved in db.
        '''
        return self.cleaned_data.get('name').lower().capitalize()
