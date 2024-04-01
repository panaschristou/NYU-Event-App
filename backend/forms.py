from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Profile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text="", required=True)

    class Meta:
        model = get_user_model()
        # fields = ["username", "email", "password1", "password2"]
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@nyu.edu"):
            raise forms.ValidationError("Email must be from NYU domain (@nyu.edu)")
        return email

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()

        return user


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "description"]

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.fields["avatar"].required = False
