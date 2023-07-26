from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django import forms
from app.models import Donation
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = {
            "first_name": "Imię",
            "last_name": "Nazwisko",
            "email": "Adres E-mail",
            "username": "Adres E-mail",
            "password1": "Hasło",
            "password2": "Hasło",
        }
class DonationForm(ModelForm):
    class Meta:
        model = Donation
        fields = ["quantity", "categories", "institution", "address", "phone_number", "city", "zip_code",
                  "pick_up_date", "pick_up_time", "pick_up_comment", "user"]
class UserEditForm(ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = get_user_model()

        fields = {
            "first_name": "Imię",
            "last_name": "Nazwisko",
            "email": "Adres Email",
        }
class UserEditPasswordForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password_repeat = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()

        fields = {
            'password': 'password',
            'new_password': 'new_password',
            'new_password_repeat': 'new_password_repeat',
        }

class ForgotPasswordForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = {
            "email": "Adres Email",
        }

def validate_length(password):
    if len(password) < 8:
        raise ValidationError("Hasło musi zawierać conajmniej 8 znaków.")

def validate_has_uppercase(password):
    has_uppercase = False
    for letter in password:
        if letter.isupper():
            has_uppercase = True
            break

    if not has_uppercase:
        raise ValidationError("Hasło musi zawierać conajmniej jedną wielką literę.")

def validate_has_lowercase(password):
    has_lowercase = False
    for letter in password:
        if not letter.isupper():
            has_lowercase = True
            break

    if not has_lowercase:
        raise ValidationError("Hasło musi zawierać conajmniej jedną małą literę.")

def validate_has_digit(password):
    has_digit = False
    for letter in password:
        if letter.isdigit():
            has_digit = True
            break

    if not has_digit:
        raise ValidationError("Hasło musi zawierać conajmniej jedną cyfrę.")

def validate_has_special_character(password):
    specials = """ 
        !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    """
    has_special = False
    for letter in password:
        if letter in specials:
            has_special = True
            break

    if not has_special:
        raise ValidationError("Hasło musi zawierać conajmniej jeden znak specjalny.")

class ForgotPasswordNewPasswordForm(ModelForm):
    new_password = forms.CharField(
        label='Nowe hasło',
        widget=forms.PasswordInput,
        validators=[validate_length, validate_has_uppercase, validate_has_lowercase, validate_has_digit, validate_has_special_character]
    )
    confirm_password = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = {}