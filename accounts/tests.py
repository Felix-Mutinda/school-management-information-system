from django.test import TestCase
from django.contrib.auth import (
    get_user_model,
)
from django.urls import reverse
from django_webtest import WebTest

from .forms import RegisterUserForm

# get our custom user
User = get_user_model()

def create_staff_user(username, password):
    '''
    creates a staff user -> who can login, with
    the given username and password.
    '''
    user = User.objects.create_user(username=username)
    user.is_staff = True
    user.set_password(password)
    user.save()
    return user

def login_as_staff(test_client):
    username = 'staff'
    password = 'pass'
    create_staff_user(username=username, password=password)
    test_client.login(username=username, password=password)

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
