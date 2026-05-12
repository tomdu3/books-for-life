from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import UserProfile
from django import forms
from cloudinary.forms import CloudinaryFileField


# User SignUp Form
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=100,
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        }),
        required=False,
        help_text='',
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email is already in use. Please use a different email.'
            )
        return email

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # override the default form fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-label',
            'placeholder': 'Username (required)'
        })
        self.fields['username'].label = ''
        self.fields['username'].help_text = ''

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-label',
            'placeholder': 'Password (required)'
        })
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = ''
        self.fields['password1'].error_messages['invalid'] = (
            "The password doesn't meet the requirements."
        )

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-label',
            'placeholder': 'Confirm Password (required)'
        })
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = ''
        self.fields['password2'].error_messages['password_mismatch'] = (
            "The two password fields didn't match."
        )


# Update User Profile Form
class UpdateProfileForm(UserChangeForm):
    email = forms.EmailField(
        max_length=100,
        label='Email:',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        }),
        required=False,
        help_text='',
    )

    profile_image = CloudinaryFileField(
        label='Change Profile Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control form-label',
        })
    )

    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-label',
            'placeholder': 'New Password (blank for current password)'
        }),
        required=False
    )

    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-label',
            'placeholder': 'Confirm New Password'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = ('email', 'profile_image')


# Contact Form for sending email
class ContactForm(forms.Form):
    name = forms.CharField(
        label='',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name (required)',
            'id': 'name'
        })
    )
    email = forms.EmailField(
        label='',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (required)',
            'id': 'email'
        })
    )
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write your message (required)',
            'id': 'message'
        })
    )
