from django.test import TestCase
from django.contrib.auth import (
    get_user_model,
)
from django.urls import reverse
from django_webtest import WebTest

from .forms import (
    StaffLoginForm,
    RegisterUserForm
)

# get our custom user
User = get_user_model()

STAFF_USERNAME = 'staff'
PASSWORD = 'pass'
PASSWORD2 = 'pass2'

def create_user(username, password, commit=True):
    '''
    Create a user with given username and password.
    If commit is True, commit, otherwise don't.
    '''
    user = User.objects.create_user(username=username)
    user.set_password(password)
    if commit:
        user.save()
    return user

def create_staff_user(username, password):
    '''
    creates a staff user -> who can login, with
    the given username and password.
    '''
    user = create_user(username=username, password=password, commit=False)
    user.is_staff = True
    user.save()
    return user

def login_as_staff(test_client):
    create_staff_user(username=STAFF_USERNAME, password=PASSWORD)
    test_client.login(username=STAFF_USERNAME, password=PASSWORD)

class UserModelTests(TestCase):
    pass

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
        staff = create_staff_user(username=STAFF_USERNAME, password=PASSWORD)
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
        create_staff_user(username=STAFF_USERNAME, password=PASSWORD)
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
        create_staff_user(username=STAFF_USERNAME, password=PASSWORD)
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