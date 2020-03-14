from exam_module.models import GradingSystem, SubjectsDoneByStudent, Exam


def get_grade(marks):
    '''
    Resolve the grade from grading system based on marks.
    Otherwise return '**'.
    '''
    grading_system = GradingSystem.objects.all().order_by('-greatest_lower_bound')
    for item in grading_system:
        if marks >= item.greatest_lower_bound:
            return item.grade
    return '**'

def get_student_position(students_list, std, exam_types_names, term_name):
    '''
    Based on the given term_name and exam_types_names, determine an average 
    score for all the students in students_list. Returns the position of
    the given student(std) based on average scores in desceding order.
    '''
    tmp = []
    for student in students_list:
        exam_objects = Exam.objects.filter(
            student = student,
            term__name = term_name,
        )
        # just an extra precaution.
        # get the exam objects if their subjects belong to the
        # subjects done by this student.
        subjects_done_by_student = SubjectsDoneByStudent.objects.filter(student=student)
        exam_objects = [eo for eo in exam_objects if eo.subject.name in [sd.subject.name for sd in subjects_done_by_student]]
        tmp_entry = {
            'student': student,
            'total': 0.0,
            'avg': 0.0,
        }
        for exam_object in exam_objects:
            if exam_object.exam_type.name in exam_types_names:
                tmp_entry['total'] += float(exam_object.marks)

        tet = len(exam_types_names) # total exam types names
        no_of_subjects_done_by_student = SubjectsDoneByStudent.objects.filter(student=student).count()
        avg = round(tmp_entry['total'] / (tet * no_of_subjects_done_by_student), 2) # compute avegare
        tmp_entry['avg'] = avg
        tmp.append(tmp_entry)

    # sort tmp based on avg 
    tmp.sort(key=lambda t: t['avg'], reverse=True)

    # get position in tmp
    p = 1
    for tmp_entry in tmp:
        if tmp_entry['student'] ==  std:
            return p
        p += 1
    return '**'

def get_objects_as_choices(model):
    '''
    Returns a list of tuples (model.object.name, model.object.name.capitalize())
    for use in widget choices.
    '''
    CHOICES = [(obj.name, obj.name.capitalize()) for obj in model.objects.all()]
    return CHOICES
