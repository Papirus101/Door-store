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
        fields = ['width', 'height', 'depth', 'sash', 'style', 'glass', 'material', 'closer', 'price',
                  'personal_margin', 'name', 'description']
        labels = {
            'description': 'Коментарий к заказу',
            'name': 'Название заказа ( видно только вам )'
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
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'personal_margin': forms.NumberInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, manager=False, *args, **kwargs):
        super(NewDoorOrder, self).__init__(*args, **kwargs)
        if not manager:
            self.fields['price'].widget = forms.HiddenInput()
            self.fields['personal_margin'].widget = forms.HiddenInput()
            self.fields['name'].widget = forms.HiddenInput()


class NewOrderForm(forms.ModelForm):
    user_phone = PhoneNumberField(label='Телефон', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Order
        fields = ['user_email', 'count_doors', 'user_phone', 'company_name']
        widgets = {
            'user_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'count_doors': forms.NumberInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, manager: bool = False, *args, **kwargs):
        super(NewOrderForm, self).__init__(*args, **kwargs)
        if manager is False:
            self.fields['company_name'].widget = forms.HiddenInput()
