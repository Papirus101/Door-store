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

from .models import CloserDoor, Door, MaterialDoor, Order, Profile, SashDoor, StyleDoor


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
    model = Profile
    template_name = 'door/order_list.html'

    def get_queryset(self):
        return Order.objects.filter(orders__user__username=self.kwargs['username']).order_by('-active')


class OrderDetail(LoginRequiredMixin, DetailView):
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


def calculate_sum_door(form) -> int:
    """ Высчитывает цену двери """
    form_material = form.cleaned_data['material']
    material_price = int(MaterialDoor.objects.get(name=form_material).price)
    width_price = int(form.cleaned_data['width']) * material_price
    height_price = int(form.cleaned_data['height']) * material_price
    depth_price = int(form.cleaned_data['depth']) * material_price
    sash_price = int(SashDoor.objects.get(name=form.cleaned_data['sash']).price)
    style_price = int(StyleDoor.objects.get(name=form.cleaned_data['style']).price)
    if form.cleaned_data['closer'] is True:
        closer_price = int(CloserDoor.objects.get(name=form.cleaned_data['closer']).price)
    else:
        closer_price = 0
    summ = width_price + height_price + depth_price + sash_price + style_price + closer_price
    print(width_price, height_price, depth_price, sash_price, style_price, closer_price)
    return summ


class ConstrucorDoor(View):

    def get(self, request, *args, **kwargs):
        form_door = NewDoorOrder()
        form_order = NewOrderForm()
        return render(request, 'door/constructor.html', {'form_door': form_door, 'form_order': form_order})

    def post(self, request, *args, **kwargs):
        form_door = NewDoorOrder(request.POST)
        form_order = NewOrderForm(request.POST)
        if form_door.is_valid() and form_order.is_valid():
            door = form_door.save()
            door.name = f'{door.material} {door.style}'
            door.save()
            if 'send_order' in request.POST:
                user = User.objects.filter(groups__name='Менеджер').annotate(count_orders=Count('profile__orders')).order_by('count_orders')[0]
                new_order = form_order.save()
                messages.success(request,
                                 f'Вы успешно оформили заявку, ваш менеджер {user.first_name} скоро с вами свяжется')
                user.profile.orders.add(new_order)
                return redirect('index')
            elif 'calculate_order' in request.POST:
                summ = calculate_door(door.pk)
                door.delete()
                return render(request, 'door/constructor.html',
                              {'form_door': form_door, 'form_order': form_order, 'price': summ})
        else:
            form = NewDoorOrder(request.POST)
            return render(request, 'door/constructor.html', {'form': form})


class EditOrderManager(View):

    def get_initial(self):
        order = Order.objects.get(id=self.kwargs['pk'])
        initial = {}
        initial['count'] = order.count_doors
        initial['phone'] = order.user_phone
        initial['email'] = order.user_email
        initial['description'] = order.door.description
        initial['width'] = order.door.width
        initial['height'] = order.door.height
        initial['depth'] = order.door.depth
        initial['sash'] = order.door.sash.pk
        initial['style'] = order.door.style.pk
        initial['glass'] = order.door.glass
        initial['material'] = order.door.material.pk
        initial['closer'] = order.door.closer.pk
        return initial

    def get(self, request, *args, **kwargs):
        form = NewDoorOrder(initial=self.get_initial())
        return render(request, 'door/constructor.html', {'form': form})

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        door = Door.objects.get(pk=order.door.pk)
        form = NewDoorOrder(request.POST, instance=door)
        if form.is_valid():
            if 'send_order' in request.POST:
                form.save()
                order.user_phone = form.cleaned_data['phone']
                order.user_email = form.cleaned_data['email']
                order.count_doors = form.cleaned_data['count']
                order.save()
                return HttpResponseRedirect(reverse('order_detail', kwargs={'pk': self.kwargs['pk']}))
            elif 'calculate_order' in request.POST:
                summ = calculate_door(order.door.pk)
                return render(request, 'door/constructor.html', {'form': form, 'price': summ})
