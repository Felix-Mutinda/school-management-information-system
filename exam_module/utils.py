from exam_module.models import GradingSystem


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
