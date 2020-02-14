from django.test import TestCase
from django.contrib.auth import (
    get_user_model,
)
from django.urls import reverse

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
        username = 'staff'
        password = 'pass'
        create_staff_user(username=username, password=password)
        self.client.login(username=username, password=password)
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home')
