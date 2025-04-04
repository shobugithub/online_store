from typing import Any
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . import models
from django import forms
from django.db.transaction import atomic
from online_shop.models import UserAccount


User = get_user_model()

class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Barcha form maydonlariga 'form-control' CSS klassini qo‘shish
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('The email is not found')
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError('Password is incorrect')
            except User.DoesNotExist:
                raise forms.ValidationError('The email is not found')

        return cleaned_data


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already exist')
        return email
    
    def clean_password(self):
        password1 = self.data.get('password')
        password2 = self.data.get('confirm_password')
        if password1 != password2:
            raise ValidationError('tasdiqlash paroli xato')
        return password1
    
    @atomic # dekorator tranzaksiya (transaction) ta’minlaydi, ya’ni kod ichida biron xato bo‘lsa, barcha o‘zgarishlar bekor qilinadi.
    def save(self, commit=False):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.is_active = False
        if commit:
            user.save()
        return user


class AccountUpdateForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'This {email} is already exist')
        return email
    
    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Passwords do not match')
        return password2
    

class EmailForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    from_email = forms.EmailField()
    to = forms.EmailField()

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('The email is not found')
        return email    


class ProductForm(ModelForm):
    class Meta:
        model = models.Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _, fields in self.fields.items():
            fields.widget.attrs.update({
                'class': 'form-control'
            })

