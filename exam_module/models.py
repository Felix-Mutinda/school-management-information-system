from django.db import models

from accounts.models import StudentProfile

class Subject(models.Model):
    '''
    Represents all the subjects offered. e.g English,
    Mathematics, ...
    '''
    name = models.CharField(max_length=20, null=False, blank=False, unique=True)

class ExamType(models.Model):
    '''
    Represents all the exam types/categories offered.
    e.g Cat 1, Cat 2, Mid-term, ...
    '''
    name = models.CharField(max_length=20, null=False, blank=False, unique=True)

class Term(models.Model):
    '''
    Represents all the  terms/semesters in a year.
    e.g 1,2,3 or 1.1,1.2,1.3,... or a,b,c,...
    '''
    name = models.CharField(max_length=20, null=False, blank=False, unique=True)

class Exam(models.Model):
    '''
    This is the actual exam object. 
    It represents:
        who did it?
        which subject?
        which exam_type?
        which term?
        when?
        ...
    '''
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, to_field='reg_no')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    date_done = models.DateTimeField()
    marks = models.DecimalField(max_digits=4, decimal_places=2)

class GradingSystem(models.Model):
    '''
    Maps a given decimal value to a grade.
    '''
    grade = models.CharField(max_length=20, unique=True)
    greatest_lower_bound = models.DecimalField(max_digits=4, decimal_places=2, unique=True)
