from django.test import TestCase
from django.urls import reverse

from django_webtest import WebTest

from .forms import (
    AddSubjectForm,
)


class HomeViewTests(WebTest):

    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.settings_module_home_url = reverse('settings_module:home')
    
    def test_requires_login(self):
        '''
        Unauthenticated users should not access this view.
        '''
        page = self.app.get(self.settings_module_home_url)
        self.assertRedirects(
            page,
            self.login_url+'?next='+self.settings_module_home_url
        )
    
    def test_quick_links_rendered(self):
        '''
        This home view is a bunch of links to change/ update 
        various settings.
        '''
        page = self.app.get(self.settings_module_home_url, user='staff')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, reverse('settings_module:add_subject'))

class AddSubjectViewTests(WebTest):
    
    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.add_subject_url = reverse('settings_module:add_subject')

    def test_requires_login(self):
        page = self.app.get(self.add_subject_url)
        self.assertRedirects(
            page,
            self.login_url+'?next='+self.add_subject_url
        )

    def test_add_subject_form_rendered(self):
        '''
        A form to add a subject should be rendered.
        '''
        page = self.app.get(self.add_subject_url, user='staff')
        self.assertEqual(page.status_code, 200)
        self.assertTrue(len(page.forms) >= 1)

    def test_add_subject_form_with_no_data(self):
        '''
        The name field is required.
        '''
        page = self.app.get(self.add_subject_url, user='staff')
        page = page.form.submit()
        self.assertContains(page, 'This field is required.')
    
    def test_add_subject_form_with_valid_data(self):
        '''
        A name given for subject would be saved in db and 
        displayed on a table below this form with a link to 
        delete it. The displayed name should be capitalized.
        '''
        page = self.app.get(self.add_subject_url, user='staff')
        page.form['name']  = 'python'
        page = page.form.submit().follow()
        self.assertContains(page, 'Subject added successfully.')
        self.assertContains(page, 'Python')
        self.assertContains(page, reverse('settings_module:delete_subject', args=(1,)))
    
    def test_delete_subject(self):
        '''
        Displayed subjects have a link to delete them.
        '''
        page = self.app.get(self.add_subject_url, user='staff')
        page.form['name'] = 'Mathematics'
        page = page.form.submit().follow()
        page = self.app.get(reverse('settings_module:delete_subject', args=(1,)))
        self.assertRedirects(page, reverse('settings_module:add_subject'))


class AddSubjectFormTests(TestCase):

    def test_form_with_no_data(self):
        form = AddSubjectForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])
    
    def test_form_with_valid_data(self):
        form = AddSubjectForm({
            'name': 'Subject',
        })
        self.assertTrue(form.is_valid())
    
    def test_form_with_duplicate_data(self):
        form = AddSubjectForm({
            'name': 'Subject',
        })
        form.save()

        form = AddSubjectForm({
            'name': 'Subject',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['Subject with this Name already exists.'])