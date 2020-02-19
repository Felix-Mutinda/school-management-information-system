from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    '''
    Extends the default auth model.
    '''
    middle_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    # is_staff => from base
    is_student = models.BooleanField(default=False)
    is_guardian = models.BooleanField(default=False)

class StaffProfile(models.Model):
    '''
    Contains attributes specific to a staff member.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return '%s\'s Profile' % self.user.first_name

class StudentProfile(models.Model):
    '''
    Contains attributes specific to a student.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    reg_no = models.CharField(max_length=20, unique=True)
    form = models.IntegerField(default=1)
    stream = models.CharField(max_length=20)
    kcpe_marks = models.IntegerField(default=0, null=True, blank=True)
    house = models.CharField(max_length=20, blank=True)
    date_registered = models.DateTimeField()
    
    def __str__(self):
        return '%s\'s Profile' % self.user.first_name

class GuardianProfile(models.Model):
    '''
    Contains attributes specific to a guardian.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guardian_profile')
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='guardian')

    def __str__(self):
        return '%s\'s Profile' % self.user.first_name