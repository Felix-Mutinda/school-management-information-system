import csv

from django.shortcuts import render, redirect, get_object_or_404
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
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string

from fpdf import FPDF, HTMLMixin

from crispy_forms.layout import (
    Layout,
    Fieldset,
    Submit,
)

from .forms import (
    RegisterUserForm,
    StaffLoginForm,
    StaffProfileForm,
    RegisterStudentForm,
    StudentProfileForm,
    GenerateClassListForm,
    FilterStudentForm,
)
from .models import (
    GuardianProfile,
    Stream,
    StudentProfile,
)

from.helpers import (
    get_student_and_guardian_forms,
    add_subject_done_by_student
)

from exam_module.models import SubjectsDoneByStudent

User = get_user_model()

# generate pdf responses with fpdf
class HtmlPdf(FPDF, HTMLMixin):
    pass

class HomeView(LoginRequiredMixin, TemplateView):
    '''
    Take the user to dashboard
    '''
    template_name = 'dashboard.html'

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
                    next = request.GET.get('next')
                    if next:
                        return redirect(next)
                    return redirect(reverse('accounts:dashboard'))
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
    template_name = 'accounts/register_update_student.html'

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
        # handles higher level validation
        form = RegisterStudentForm(request.POST)
        if form.is_valid():
            # get forms through the helper
            student_user_form, student_profile_form, guardian_user_form = get_student_and_guardian_forms(form.cleaned_data)

            if (student_profile_form.is_valid()):
                student_user = student_user_form.save(commit=False)
                student_user.is_student = True
                student_user.save()
                student_profile = student_profile_form.save(commit=False)
                student_profile.user = student_user
                student_profile.save()
                guardian_user = guardian_user_form.save(commit=False)
                guardian_user.is_guardian = True
                guardian_user.save()
                guardian_profile = GuardianProfile.objects.create(
                    user=guardian_user,
                    student=student_profile
                )

                # subjects done by student
                subjects_done_by_student = form.cleaned_data.get('student_subjects_done_by_student')
                
                # update subjects done
                # first remove all entries in db.
                reg_no = form.cleaned_data.get('student_reg_no')
                sd_b4 = SubjectsDoneByStudent.objects.filter(student=StudentProfile.objects.get(reg_no=reg_no))
                for sd in sd_b4:
                    sd.delete()
                
                for sd in subjects_done_by_student: # from submitted form
                    add_subject_done_by_student(reg_no, sd)
                
                messages.success(request, 'Student successfully registered.')
                return redirect(reverse('accounts:register_student'))

            # a failure can occur in two ways:
            # - a duplicate reg_no
            # - a stream not in the given choices
            for field in student_profile_form.errors:
                if field == 'reg_no':
                    form.add_error('student_reg_no', student_profile_form.errors[field])
                elif field == 'stream':
                    form.add_error('student_stream_name', student_profile_form.errors[field])
                else:
                    form.add_error(None, student_profile_form.errors[field])

        return render(request, self.template_name, {'form': form})

class StudentsHomeView(LoginRequiredMixin, View):
    '''
    Quick links to get and manage students.
    '''
    template_name = 'accounts/students_home.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)

class GenerateClassListView(LoginRequiredMixin, View):
    '''
    Use a filter form to generate a class list.
    '''
    form_class = GenerateClassListForm
    template_name = 'accounts/generate_class_list.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'generate_class_list_form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            f = form.cleaned_data.get('form')
            stream_name = form.cleaned_data.get('stream_name')
            file_type = form.cleaned_data.get('file_type')

            # get students
            query_set = StudentProfile.objects.filter(stream__name=stream_name)
            students_list = [s for s in query_set if s.get_form() == f]

            if file_type == '0':
                pdf = HtmlPdf()
                pdf.add_page()

                # pdf.write_html(render_to_string('accounts/pdf/class_list.html', {
                #     'title': 'Form %d %s' % (f, stream_name.capitalize()),
                #     'students_list': students_list
                # }))

                # Effective page width, or just epw
                epw = pdf.w - 2*pdf.l_margin

                # table title
                title = 'Form %d %s' % (f, stream_name.capitalize())
                pdf.set_font('Times', 'B', 16)
                pdf.cell(epw, 0.0, title, align='C')
                pdf.ln(4)

                # text height
                th = pdf.font_size

                # table header
                pdf.set_font('Times', 'B', 14)
                pdf.cell(epw*0.05, th, 'No.', border=1, align='C') # 0.5% of epw
                pdf.cell(epw*0.15, th, 'Reg No.', border=1, align='C')
                pdf.cell(epw*0.40, th, 'Name', border=1, align='C')
                pdf.cell(epw*0.20, th, '', border=1, align='C')
                pdf.cell(epw*0.20, th, '', border=1, align='C')
                pdf.ln(th)

                # table body
                pdf.set_font('Times', '', 12)
                i = 1
                for student in students_list:
                    student_full_name = '%s %s %s' % (student.user.first_name, student.user.middle_name, student.user.last_name)
                    pdf.cell(epw*0.05, th, str(i), border=1) # 0.5% of epw
                    pdf.cell(epw*0.15, th, str(student.reg_no), border=1)
                    pdf.cell(epw*0.40, th, student_full_name, border=1)
                    pdf.cell(epw*0.20, th, '', border=1)
                    pdf.cell(epw*0.20, th, '', border=1)
                    pdf.ln()
                    i += 1


                response = HttpResponse(pdf.output(dest='S').encode('latin-1'))
                response['Content-Type'] = 'application/pdf'
                response['Content-Disposition'] = 'inline; filename="Form %s %s.pdf"' %(f,stream_name.capitalize())

                messages.success(request, 'File has been generated.')
                return response
            else:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Form %s %s.csv"' %(f,stream_name.capitalize())

                i = 1
                writer = csv.writer(response)
                for student in students_list:
                    # '#', 'reg_no', 'full name'
                    writer.writerow([i, student.reg_no, '%s %s %s' %(student.user.first_name, student.user.middle_name, student.user.last_name)])
                    i += 1
                messages.success(request, 'File has been generated.')
                return response

        return render(request, self.template_name, {'generate_class_list_form': form})

class FilterStudentView(LoginRequiredMixin, View):
    '''
    Filter students.
    '''
    form_class = FilterStudentForm
    template_name = 'accounts/filter_student.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            reg_no = form.cleaned_data.get('reg_no')
            return redirect('accounts:update_student', reg_no=reg_no)
        return render(request, self.template_name, {'form': form})

# common layout
from .forms import register_update_student_common_layout
class UpdateStudentView(LoginRequiredMixin, View):
    '''
    Update students
    '''
    form_class = RegisterStudentForm
    template_name = 'accounts/register_update_student.html'

    def get(self, request, reg_no, *args, **kwargs):
        student = get_object_or_404(StudentProfile, reg_no=reg_no)
        form = RegisterStudentForm({ # populate form with this students details
            'student_reg_no': student.reg_no,
            'student_first_name': student.user.first_name,
            'student_middle_name': student.user.middle_name,
            'student_last_name': student.user.last_name,
            'student_form': student.get_form(),
            'student_stream_name': student.stream.name,
            'student_house': student.house,
            'student_kcpe_marks': student.kcpe_marks,
            'student_date_registered': student.date_registered,
            'student_subjects_done_by_student': [sd.subject.name for sd in SubjectsDoneByStudent.objects.filter(student=student)],

            'guardian_first_name': student.guardian.user.first_name,
            'guardian_middle_name': student.guardian.user.middle_name,
            'guardian_last_name': student.guardian.user.last_name,
            'guardian_phone_number': student.guardian.user.phone_number,
            'guardian_email': student.guardian.user.email,
        })
        form.helper.form_class = 'update-student-form'
        form.helper.form_method = 'post'
        form.helper.form_action = reverse('accounts:update_student', args=(reg_no,))
        form.helper.layout = Layout(
            Fieldset(
                'Update Student',
                register_update_student_common_layout,
                Submit('submit', 'Update Details', css_class='btn btn-primary'),
                css_class='p-3 border rounded',
            )
        )
        return render(request, self.template_name, {'form': form})

    def post(self, request, reg_no, *args, **kwargs):
        '''
        Updates details of the student with the given reg_no
        '''
        student = get_object_or_404(StudentProfile, reg_no=reg_no)
        form = self.form_class(request.POST)
        if form.is_valid():
            # get forms through the helper
            student_user_form, student_profile_form, guardian_user_form = get_student_and_guardian_forms(form.cleaned_data, student) # student instance

            if (student_profile_form.is_valid()):
                student_user_form.save()
                student_profile_form.save()
                guardian_user_form.save()
                
                # subjects done by student
                subjects_done_by_student = form.cleaned_data.get('student_subjects_done_by_student')
                
                # update subjects done
                # first remove all entries in db.
                reg_no = form.cleaned_data.get('student_reg_no')
                sd_b4 = SubjectsDoneByStudent.objects.filter(student=StudentProfile.objects.get(reg_no=reg_no))
                for sd in sd_b4:
                    sd.delete()
                
                for sd in subjects_done_by_student: # from submitted form
                    add_subject_done_by_student(reg_no, sd)
                    
                messages.success(request, 'Student Details Updated Successfully.')
                return redirect(reverse('accounts:update_student', args=(student.reg_no,)))

            # a failure can occur in two ways:
            # - a duplicate reg_no
            # - a stream not in the given choices
            for field in student_profile_form.errors:
                if field == 'reg_no':
                    form.add_error('student_reg_no', student_profile_form.errors[field])
                elif field == 'stream':
                    form.add_error('student_stream_name', student_profile_form.errors[field])
                else:
                    form.add_error(None, student_profile_form.errors[field])

        return render(request, self.template_name, {'form': form})