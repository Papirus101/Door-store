from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

from .models import Door, Profile, Order

from phonenumber_field.formfields import PhoneNumberField

from .templatetags.door_tags import has_group

import datetime
import locale


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

    def __init__(self, user, *args, **kwargs):
        super(NewDoorOrder, self).__init__(*args, **kwargs)
        if not has_group(user):
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

    def __init__(self, user, *args, **kwargs):
        super(NewOrderForm, self).__init__(*args, **kwargs)
        if not has_group(user):
            self.fields['company_name'].widget = forms.HiddenInput()


class OrderCheckForm(forms.Form):
    kpp = forms.CharField(label='КПП оптправителя', max_length=250, widget=forms.TextInput(attrs={'class': 'form-control'}))
    inn = forms.IntegerField(label='ИНН отправителя', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    index = forms.IntegerField(label='Индекс отправителя', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label='Адрес отправителя', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    num_check = forms.IntegerField(label='Счёт №', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    day = forms.IntegerField(label='Счёт от (число месяца)', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    month = forms.CharField(label='Счёт от ( месяц прописью )', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    year = forms.IntegerField(label='Счёт от ( последние две цифры года )', widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(OrderCheckForm, self).__init__(*args, **kwargs)
        today = datetime.date.today()
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        today = today.strftime('%d-%B-%y').split('-')
        print(today)
        self.fields['day'].initial = today[0]
        self.fields['month'].initial = today[1]
        self.fields['year'].initial = today[2]