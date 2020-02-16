from django.test import TestCase
from django.contrib.auth import (
    get_user_model,
)
from django.urls import reverse
from django_webtest import WebTest

from .forms import (
    StaffLoginForm,
    RegisterUserForm,
    StaffProfileForm,
    StudentProfileForm,
)

from .models import (
    StaffProfile,
    StudentProfile,
    GuardianProfile,
)

# get our custom user
User = get_user_model()

STAFF_USERNAME = 'staff'
PASSWORD = 'pass'
PASSWORD2 = 'pass2'

def create_user(username, password, is_staff=False, is_student=False, is_guardian=False):
    '''
    Create a user with given username and password and set
    the flags if provided.
    '''
    user = User.objects.create_user(
        username=username,
        is_staff=is_staff,
        is_student=is_student,
        is_guardian=is_guardian
    )
    user.set_password(password)
    user.save()
    return user

def create_profile(is_staff=False, is_student=False, is_guardian=False, *args, **kwargs):
    '''
    Create a profile based on the given flag i.e. if is_staff = True
    create a staff profile. Otherwise return None.
    '''
    if is_staff:
        return StaffProfile.objects.create(*args, **kwargs)
    if is_student:
        return StudentProfile.objects.create(*args, **kwargs)
    if is_guardian:
        return GuardianProfile.objects.create(*args, **kwargs)
    return None

def login_as_staff(test_client):
    create_user(is_staff=True, username=STAFF_USERNAME, password=PASSWORD)
    test_client.login(username=STAFF_USERNAME, password=PASSWORD)

class UserModelTests(TestCase):
    
    def test_user_with_no_flags_set_and_no_profile(self):
        '''
        A user object with no explicity set profile should not
        have access to any profile.
        '''
        user = create_user(username='no flags', password='pass')
        self.assertFalse(hasattr(user, 'staff_profile'))
        self.assertFalse(hasattr(user, 'student_profile'))
        self.assertFalse(hasattr(user, 'guardian_profile'))
    
    def test_user_with_is_staff_true_and_a_staff_profile(self):
        '''
        A user with is_staff = True and a staff_profile should
        have access to the staff_profile.
        '''
        staff_user = create_user(is_staff=True, username=STAFF_USERNAME, password=PASSWORD)
        staff_profile = create_profile(
            is_staff=True,
            user=staff_user,
            staff_id='id',
            position='position'
        )
        self.assertTrue(hasattr(staff_user, 'staff_profile'))
        self.assertEqual(staff_user.staff_profile.id, staff_profile.id)
        self.assertEqual(staff_user.staff_profile.staff_id, 'id')
        
    def test_user_with_is_student_true_and_a_student_profile(self):
        '''
        A user with is_student = True and a student_profile should
        have access to the student_profile.
        '''
        student_user = create_user(is_student=True, username='student', password='password')
        student_profile = create_profile(
            is_student=True,
            user=student_user,
            reg_no='reg_no',
            form='2',
            stream='south',
            house='house'
        )
        self.assertTrue(hasattr(student_user, 'student_profile'))
        self.assertEqual(student_user.student_profile.id, student_profile.id)
        self.assertEqual(student_user.student_profile.reg_no, 'reg_no')
    
    def test_user_with_is_guardian_true_and_a_guardian_profile(self):
        '''
        A user with is_guardian = True and a guardian_profile should 
        have access to the guardian profile.
        '''
        # create a student and  a student profile
        student_user = create_user(is_student=True, username='student', password='pass')
        student_profile = create_profile(
            is_student=True,
            user=student_user,
            reg_no='reg_no',
            form='2',
            stream='north',
            house='house'
        )

        # create a guardian and a guardian profile, then associate with above student
        guardian_user = create_user(is_guardian=True, username='guardian', password='pass')
        guardian_profile = create_profile(
            is_guardian=True,
            user=guardian_user,
            student=student_profile
        )
        self.assertTrue(hasattr(guardian_user, 'guardian_profile'))
        self.assertEqual(guardian_user.guardian_profile.id, guardian_profile.id)
        self.assertEqual(guardian_user.guardian_profile.student, student_profile)


class StaffLoginFormTests(TestCase):

    def test_form_with_no_input(self):
        '''
        A login with no filled fields raises a 
        validation error.
        '''
        form = StaffLoginForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])
        self.assertEqual(form.errors['password'], ['This field is required.'])
    
    def test_form_with_username_only(self):
        '''
        Username only raises a validation error.
        '''
        form = StaffLoginForm({
            'username': 'staff',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['This field is required.'])
    
    def test_form_with_password_only(self):
        '''
        Password only raises a validation error.
        '''
        form = StaffLoginForm({
            'password': 'pass',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

    def test_form_with_invalid_username_and_password(self):
        '''
        Filled username and password but don't match those in
        db.
        '''
        staff = create_user(is_staff=True, username=STAFF_USERNAME, password=PASSWORD)
        form = StaffLoginForm({
            'username': staff.username,
            'password': PASSWORD2
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ['Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.'])

    def test_form_with_valid_username_and_password(self):
        '''
        Correctly filled form should be valid.
        '''
        create_user(is_staff=True, username=STAFF_USERNAME, password=PASSWORD)
        form = StaffLoginForm({
            'username': STAFF_USERNAME,
            'password': PASSWORD
        })
        self.assertTrue(form.is_valid())

    def test_form_with_a_non_staff_user(self):
        '''
        Allow users with is_staff = True to login.
        '''
        create_user(username='non staff', password=PASSWORD2)
        form = StaffLoginForm({
            'username': 'non staff',
            'password': PASSWORD2
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ['Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.'])
        
class HomeViewTests(TestCase):
    
    def test_home_with_unauthenticated_user(self):
        '''
        If no logged in user, redirect to accounts/login.
        '''
        response = self.client.get(reverse('accounts:home'))
        self.assertRedirects(
            response=response,
            expected_url='/accounts/login/?next=/',
        )
    
    def test_home_with_authenticated_user(self):
        '''
        Home/dashboard should render correctly if the user
        is authenticated.
        '''
        login_as_staff(self.client)
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home')

class RegisterUserFormTests(TestCase):

    def test_unfilled_form(self):
        '''
        Unfilled form should give out error
        '''
        form = RegisterUserForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])
    
    def test_correctly_filled_form(self):
        '''
        Correctly filled form should save staff to db
        and the returned user attributes should match
        '''
        form = RegisterUserForm({
            'username': 'staff',
            'password': 'pass',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email@domain.com',
        })
        self.assertTrue(form.is_valid())
        staff = form.save(commit=False)
        staff.set_password('pass')
        staff.save()
        self.assertTrue(staff.check_password('pass'))
        self.assertEqual(staff.username, 'staff')
        self.assertEqual(staff.first_name, 'first_name')
        self.assertEqual(staff.last_name, 'last_name')
        self.assertEqual(staff.email, 'email@domain.com')

class StaffProfileFormTests(TestCase):

    def test_form_is_valid_with_no_data(self):
        '''
        Fields specific to a staff member are not 
        mandatory.
        '''
        form = StaffProfileForm({})
        self.assertTrue(form.is_valid())
    
    def test_form_is_valid_with_data(self):
        '''
        Fields are not mandatory.
        '''
        form = StaffProfileForm({
            'staff_id': 'id',
            'postition': 'staff'
        })
        self.assertTrue(form.is_valid())
    
class StudentProfileFormTests(TestCase):

    def test_form_with_no_data(self):
        '''
        Registration number 'reg_no' is required and unique.
        Form/class and stream are required.
        '''
        form = StudentProfileForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['reg_no'], ['This field is required.'])
        self.assertEqual(form.errors['form'], ['This field is required.'])
        self.assertEqual(form.errors['stream'], ['This field is required.'])

    def test_form_with_form_stream_and_unique_reg_no(self):
        '''
        A unique reg_no, a form and a stream make up a valid student profile.
        '''
        form = StudentProfileForm({
            'reg_no': '3594',
            'form': '1',
            'stream': 'east'
        })
        self.assertTrue(form.is_valid)
        student_user = create_user(is_student=True, username='student', password='pass')
        student_profile = form.save(commit=False)
        student_profile.user = student_user
        student_profile.save()
        self.assertEqual(student_profile.reg_no, '3594')

    def test_form_with_non_unique_reg_no(self):
        '''
        Reusing a reg_no raises a validation error.
        '''
        form1 = StudentProfileForm({
            'reg_no': '3594',
            'form': '2',
            'stream': 'north'
        })
        self.assertTrue(form1.is_valid())
        student_user = create_user(is_student=True, username='student', password='pass')
        student_profile = form1.save(commit=False)
        student_profile.user = student_user
        student_profile.save()

        form2 = StudentProfileForm({
            'reg_no': '3594',
            'form': '2',
            'stream': 'west'
        })
        self.assertFalse(form2.is_valid())
        self.assertEqual(form2.errors['reg_no'], ['This registration number is already taken.'])


class RegisterStaffView(WebTest):
    # csrf_checks = False

    def setUp(self):
        '''
        Initialize the /accounts/register/staff/ url.
        '''
        self.register_staff_url = reverse('accounts:register_staff')

    def test_register_staff_page_without_login(self):
        response = self.client.get(self.register_staff_url)
        self.assertRedirects(
            response,
            reverse('accounts:login')+'?next='+reverse('accounts:register_staff')
        )

    def test_register_staff_page_while_logged_in(self):
        '''
        Is the RegisterStaffForm being rendered.
        '''
        page = self.app.get(self.register_staff_url, user='staff')
        self.assertEqual(len(page.forms), 1)
        
    def test_form_error(self):
        '''
        If invalid/incomplete fields are submitted, the form 
        should be invalid.
        '''
        page = self.app.get(self.register_staff_url, user='staff')
        page = page.form.submit()
        self.assertContains(page, 'This field is required.')
    
    def test_form_success(self):
        '''
        Correctly filled form would be saved, redirected to a staff
        list page, and the added staff should appear there.
        '''
        page = self.app.get(self.register_staff_url, user='staff')
        page.form['username'] = 'staff2'
        page.form['password'] = 'password'
        # page = self.app.post(self.register_staff_url, user='staff')
        page = page.form.submit().follow()
        self.assertContains(page, 'staff2')
    
    def test_staff_profile_fields_prompted(self):
        '''
        In addition to the user fields, additional fields specific to
        a staff member are prompted.
        '''
        page = self.app.get(self.register_staff_url, user='staff')
        self.assertTrue('staff_id' in page.form.fields)
        self.assertTrue('position' in page.form.fields)
    
    def test_staff_profile_displayed_in_staff_list_page(self):
        '''
        In staff details 'staff_id' and 'position' have been 
        submitted, they should reflect on the staff list page.
        '''
        page = self.app.get(self.register_staff_url, user='staff')
        page.form['username'] = 'staff2'
        page.form['password'] = 'pass'
        page.form['staff_id'] = 'staff_id'
        page.form['position'] = 'secretary'
        page = page.form.submit().follow()
        self.assertContains(page, 'staff_id')
        self.assertContains(page, 'secretary')
    
    def test_register_staff_user_form_in_context(self):
        '''
        Register staff form should be passed in the context
        for display.
        '''
        page = self.app.get(self.register_staff_url, user='staff')
        self.assertTrue('user_form' in page.context)
        self.assertTrue(isinstance(page.context['user_form'], RegisterUserForm))
    
    def test_register_staff_profile_form_in_context(self):
        '''
        Register staff profile form should be passed in the context
        for display.
        '''
        page = self.app.get(self.register_staff_url, user='staff')
        self.assertTrue('staff_profile_form' in page.context)
        self.assertTrue(isinstance(page.context['staff_profile_form'], StaffProfileForm))
    
class StaffLoginView(WebTest):

    def setUp(self):
        '''
        '''
        self.page = self.app.get(reverse('accounts:login'))

    def test_form_is_rendered(self):
        '''
        Should view the login form
        '''
        self.assertEqual(self.page.status_code, 200)
        self.assertEqual(len(self.page.forms), 1)

    def test_form_with_no_data(self):
        '''
        Username and password fields are required.
        '''
        self.page = self.page.form.submit()
        self.assertContains(self.page, 'This field is required.')
    
    def test_form_with_username_only(self):
        '''
        Password field is required.
        '''
        self.page.form['username'] = STAFF_USERNAME
        self.page = self.page.form.submit()
        self.assertContains(self.page, 'This field is required.')

    def test_form_with_password_only(self):
        '''
        Username field is required.
        '''
        self.page.form['password'] = PASSWORD
        self.page = self.page.form.submit()
        self.assertContains(self.page, 'This field is required.')
    
    def test_form_with_invalid_username_and_password(self):
        '''
        Unknown users can't login.
        '''
        self.page.form['username'] = 'unknown'
        self.page.form['password'] = 'unknown'
        self.page = self.page.form.submit()
        self.assertContains(self.page, 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')
    
    def test_form_with_user_who_is_not_staff(self):
        '''
        Users with is_staff = False can't login.
        '''
        user = create_user(username='normal user', password='pass')
        self.page.form['username'] = user.username
        self.page.form['password'] = 'pass'
        self.page = self.page.form.submit()
        self.assertContains(self.page, 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')

    def test_form_with_a_staff_user(self):
        '''
        Users with is_staff=True can login with their
        credentials.
        '''
        create_user(is_staff=True, username=STAFF_USERNAME, password=PASSWORD)
        self.page.form['username'] = STAFF_USERNAME
        self.page.form['password'] = PASSWORD
        self.page = self.page.form.submit()
        self.assertRedirects(self.page, reverse('accounts:home'))

class StaffListViewTests(TestCase):

    def test_requires_login(self):
        '''
        To view staff members you must be logged in.
        '''
        response = self.client.get(reverse('accounts:list_staff'))
        self.assertRedirects(
            response,
            reverse('accounts:login')+'?next='+reverse('accounts:list_staff')
        )