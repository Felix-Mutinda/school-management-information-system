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