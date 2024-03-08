from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.forms import UserRegistrationForm


class UserRegistrationFormTest(TestCase):

    def test_form_valid(self):
        # Test that the form is valid with correct data
        form_data = {
            "username": "testuser",
            "email": "testuser@nyu.edu",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_email_validation(self):
        # Test that the form is invalid if the email is not from nyu.edu
        form_data = {
            "username": "testuser",
            "email": "testuser@gmail.com",  # Incorrect domain
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "email", form.errors
        )  # The form should have an error associated with 'email'

    def test_password_mismatch(self):
        # Test that the form is invalid if the passwords do not match
        form_data = {
            "username": "testuser",
            "email": "testuser@nyu.edu",
            "password1": "testpassword123",
            "password2": "testpassword321",  # Passwords do not match
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "password2", form.errors
        )  # Error should be associated with 'password2'

    def test_missing_fields(self):
        # Test that the form is invalid if required fields are missing
        form_data = {
            "username": "",  # Missing username
            "email": "testuser@nyu.edu",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "username", form.errors
        )  # Error should be associated with 'username'
