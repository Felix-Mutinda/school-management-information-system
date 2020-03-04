from .forms import (
    RegisterUserForm,
    StudentProfileForm,
)

from .models import Stream, StudentProfile

from exam_module.models import Subject, SubjectsDoneByStudent

# Registering and updating users requires reading values
# from the general RegisterStudentForm and breaking it 
# into 3 forms. A RegisterUserForm for the student, a 
# StudentProfileForm and a RegisterUserForm for the student's
# guardian. This helper takes a dict of values, constructs and
# returns the three forms.
# To update a student instance is required.
def get_student_and_guardian_forms(d, student=None):
    '''
    Takes a dict like object with fields necessary for a 
    student registration. Builds and returns three forms
    in a tuple(f1, f2, f3):
    f1 = student_user_form
    f2 = student_profile_form
    f3 = guardian_user_form
    '''
    f1 = RegisterUserForm({
        'username': 'student_%s' % d.get('student_reg_no'),
        'first_name': d.get('student_first_name'),
        'middle_name': d.get('student_middle_name'),
        'last_name': d.get('student_last_name'),
        # password is required.
        'password': '*',
    }, instance=student.user if student else None)

    f2 = StudentProfileForm({
        'reg_no': d.get('student_reg_no'),
        'form': d.get('student_form'),
        'stream': Stream.objects.get(name=d.get('student_stream_name')),
        'house': d.get('student_house'),
        'kcpe_marks': d.get('student_kcpe_marks'),
        'date_registered': d.get('student_date_registered'),
    }, instance=student if student else None)

    f3 = RegisterUserForm({
        'username': 'guardian_to_student_%s' % d.get('student_reg_no'),
        'first_name': d.get('guardian_first_name'),
        'middle_name': d.get('guardian_middle_name'),
        'last_name': d.get('guardian_last_name'),
        'phone_number': d.get('guardian_phone_number'),
        'email': d.get('guardian_email'),
        # password is required.
        'password': '*',
    }, instance=student.guardian.user if student else None)

    return (f1, f2, f3)

def add_subject_done_by_student(reg_no, subject_name):
    '''
    Get a student with the given reg_no and add an 
    entry in SubjectsDoneByStudent to represent a 
    subject done by this student. Only adds if the
    entry does not exist.
    '''
    student = StudentProfile.objects.get(reg_no=reg_no)
    subject = Subject.objects.get(name=subject_name)

    try:
        _ = SubjectsDoneByStudent.objects.get(student=student, subject=subject)
    except SubjectsDoneByStudent.DoesNotExist:
        _ = SubjectsDoneByStudent.objects.create(student=student, subject=subject)
    return _