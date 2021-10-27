from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import Door, Profile, Order

from phonenumber_field.formfields import PhoneNumberField


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Подтверждение пароля",
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Почта", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='Ваше имя', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'first_name')


class ProfileRegister(forms.ModelForm):
    phone = PhoneNumberField(label='Телефон', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['phone']


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class NewDoorOrder(forms.ModelForm):

    class Meta:
        model = Door
        fields = ['width', 'height', 'depth', 'sash', 'style', 'glass', 'material', 'closer', 'description']
        labels = {
            'description': 'Коментарий к заказу'
        }
        widgets = {
            'width': forms.NumberInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'depth': forms.NumberInput(attrs={'class': 'form-control'}),
            'sash': forms.Select(attrs={'class': 'form-control'}),
            'style': forms.Select(attrs={'class': 'form-control'}),
            'glass': forms.NullBooleanSelect(attrs={'class': 'form-control'}),
            'material': forms.Select(attrs={'class': 'form-control'}),
            'closer': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class NewOrderForm(forms.ModelForm):
    user_phone = PhoneNumberField(label='Телефон', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Order
        fields = ['user_email', 'count_doors', 'user_phone']
        widgets = {
            'user_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'count_doors': forms.NumberInput(attrs={'class': 'form-control'}),
        }
