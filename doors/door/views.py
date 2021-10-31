from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from django.views.generic.base import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import NewDoorOrder, ProfileRegister, UserRegisterForm, LoginUserForm, NewOrderForm
from .logic.calculate import calculate_door

from .models import Door, Order, Profile

from django.core.mail import send_mail


class Index(ListView):
    model = Door
    template_name = 'door/index.html'

    def get_queryset(self):
        return Door.objects.filter(show_on_index=True)


class DoorDetail(DetailView):
    model = Door


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'door/user_detail.html'


class OrdersList(LoginRequiredMixin, ListView):
    """ Список заказов """
    model = Profile
    template_name = 'door/order_list.html'

    def get_queryset(self):
        return Order.objects.filter(orders__user__username=self.kwargs['username']).order_by('-active', '-pk').select_related('door')


class OrderDetail(LoginRequiredMixin, DetailView):
    """ Отдаёт детали заказа """
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_check = get_object_or_404(Order, pk=self.kwargs['pk'])
        if not order_check.is_view:
            order_check.is_view = True
            order_check.save()
        else:
            pass
        return context


def register(request):
    """ Регистрация пользователя """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        form_profile = ProfileRegister(request.POST)
        if form.is_valid() and form_profile.is_valid():
            user = form.save()
            user.refresh_from_db()
            form_profile = ProfileRegister(request.POST, instance=user.profile)
            form_profile.save()
            messages.success(request, 'Вы успешно зарегистрировались')
            return redirect('login')
        else:
            messages.warning(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()
        form_profile = ProfileRegister()
    return render(request, 'door/register.html', {'form': form, 'form_profile': form_profile})


def login_user(request):
    """ Авторизация пользователя """
    if request.method == 'POST':
        form = LoginUserForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
        else:
            messages.warning(request, 'Ошибка авторизации, проверьте свой логин и пароль')
            form = LoginUserForm()
    else:
        form = LoginUserForm()
    return render(request, 'door/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('index')


def save_order(user, form_order, door) -> None:
    """ Сохраняет новый заказ и выдаёт пользователю """
    new_order = form_order.save()
    new_order.door = door
    new_order.save()
    user.profile.orders.add(new_order)


class ConstrucorDoor(View):
    """ Конструктор двери """

    def get(self, request, *args, **kwargs):
        form_door = NewDoorOrder(request.user)
        form_order = NewOrderForm(request.user)
        return render(request, 'door/constructor.html', {'form_door': form_door, 'form_order': form_order})

    def post(self, request, *args, **kwargs):
        form_door = NewDoorOrder(request.user, request.POST)
        form_order = NewOrderForm(request.user, request.POST)
        if form_door.is_valid() and form_order.is_valid():
            door = form_door.save()
            door.name = f'Новая заявка # {door.pk}'
            door.save()
            if 'send_order' in request.POST:
                user = \
                    User.objects.filter(groups__name='Менеджер').annotate(
                        count_orders=Count('profile__orders')).order_by(
                        'count_orders')[0]
                save_order(user, form_order, door)
                messages.success(request,
                                 f'Вы успешно оформили заявку, ваш менеджер {user.first_name} скоро с вами свяжется')
                return redirect('index')
            elif 'add_order' in request.POST:
                user = User.objects.get(username=request.user.username)
                save_order(user, form_order, door)
                messages.success(request,
                                 f'Заявка успешно добавлена')
                return redirect('index')
            elif 'calculate_order' in request.POST:
                summ = calculate_door(door.pk)
                door.delete()
                return render(request, 'door/constructor.html',
                              {'form_door': form_door, 'form_order': form_order, 'price': summ})
        else:
            form_door = NewDoorOrder(request.user, request.POST)
            form_order = NewOrderForm(request.user, request.POST)
            return render(request, 'door/constructor.html', {'form_door': form_door, 'form_order': form_order})


class EditOrderManager(View):
    """ Редактирование заказа менеджером """

    def get(self, request, *args, **kwargs):
        order = Order.objects.get(pk=kwargs['pk'])
        form_door = NewDoorOrder(request.user, instance=order.door)
        form_order = NewOrderForm(request.user, instance=order)
        return render(request, 'door/constructor.html', {'form_door': form_door, 'form_order': form_order})

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(pk=kwargs['pk'])
        form_door = NewDoorOrder(request.user, request.POST, instance=order.door)
        form_order = NewOrderForm(request.user, request.POST, instance=order)
        if form_door.is_valid() and form_order.is_valid():
            door = form_door.save(commit=False)
            order = form_order.save(commit=False)
            if 'add_order' in request.POST:
                door.save()
                order.save()
                return HttpResponseRedirect(reverse('order_detail', kwargs={'pk': self.kwargs['pk']}))
            elif 'calculate_order' in request.POST:
                summ = calculate_door(door.pk)
                context = {'form_door': form_door, 'form_order': form_order, 'price': summ}
        else:
            form_door = NewDoorOrder(request.user, request.POST, instance=order.door)
            form_order = NewOrderForm(request.user, request.POST, instance=order)
            context = {'form_door': form_door, 'form_order': form_order}
        return render(request, 'door/constructor.html', context)


class CheckEdit(DetailView):
    """ Подготовка к отправке счёта """
    model = Order
    template_name = 'door/check_edit.html'
    context_object_name = 'order'


def send_order(request):
    pass