from django.contrib.auth.models import Group
from django.template import Context, Template
from django.test import TestCase

from .models import Door, SashDoor, StyleDoor, MaterialDoor, CloserDoor, Order

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client

from .logic.calculate import calculate_door

User = get_user_model()


class DoorTestClass(TestCase):

    def setUp(self) -> None:
        """ Создаёт данные для тесстов """
        # Создаёт обычного пользователя
        self.user = User.objects.create(username='test_username')
        self.user.set_password('password')
        self.user.save()
        # Создаёт количество створок двери
        self.sash = SashDoor.objects.create(name='1', slug='test-sash', price=1)
        # Создёт тестовое изображение
        image = SimpleUploadedFile('test-image.jpg', content=b'', content_type='image/jpg')
        # Создаёт стиль двери
        self.style = StyleDoor.objects.create(name='Лучший стиль', slug='test-style', price=1, image=image)
        # Создаёт тестовый материал
        self.material = MaterialDoor.objects.create(name='Тестовый материал', slug='test-material',
                                                    description='Тестовый материал', image=image,
                                                    price=100)
        # Создаёт тестовый доводчик
        self.closer = CloserDoor.objects.create(name='Доводчик', slug='test-closer', price=1)
        # Создаёт тестовую дверь
        self.door = Door.objects.create(name='Тестовая дверь', slug='test-door', width=1, height=1, depth=1,
                                        sash=self.sash, style=self.style, material=self.material, closer=self.closer)
        # Создаёт тестового менеджера
        self.user_manager = User.objects.create(username='manager_user')
        self.user_manager.set_password('manager_pass')
        self.user_manager.save()
        self.manager_group = Group.objects.create(name='Менеджер')
        self.user_manager.groups.add(self.manager_group)
        # Создаёт тестовый заказ
        self.order = Order.objects.create(door=self.door, count_doors=1, user_phone='+79883158831',
                                          user_email='test_mail@mail.ru', company_name='test company')
        self.user_manager.profile.orders.add(self.order)

    def test_calculate_door(self):
        """ Тестирует функцию автоатичекого расчёта стоимости двери """
        self.assertEqual(calculate_door(self.door.pk), 303)

    def test_get_absolute_url_door(self):
        """ Тестирует получение абсолютной ссылки двери """
        self.assertEqual(self.door.get_absolute_url(), '/door/test-door/')

    def test_get_absolute_url_order(self):
        """ Тестирует получение абсолютно ссылки заказа """
        self.assertEqual(self.order.get_absolute_url(), f'/order/{self.order.pk}/')

    def test_form_door(self):
        """ Тестирует отображение формы двери """
        client = Client()
        auth = client.login(username='test_username', password='password')
        response = client.get('/constructor/')
        self.assertTrue(response.context['form_door']['price'].is_hidden)
        self.assertTrue(response.context['form_door']['personal_margin'].is_hidden)
        self.assertTrue(response.context['form_door']['name'].is_hidden)

    def test_form_order(self):
        """ Тестирует отображение формы заказа """
        client = Client()
        auth = client.login(username='manager_user', password='manager_pass')
        response = client.get('/constructor/')
        self.assertFalse(response.context['form_order']['company_name'].is_hidden)

    def test_has_manager_tag(self):
        """ Тестирует simple tag has_manger """
        context = Context({
          'user': self.user_manager,
          'not_user': self.user
        })
        template = Template(
            "{% load door_tags %}"
            "<h1>{{ user|has_manager }}</h1>"
            "<h1>{{ not_user|has_manager }}</h1>"
        )
        rendered = template.render(context)
        self.assertInHTML('<h1>True</h1>', rendered)
        self.assertInHTML('<h1>False</h1>', rendered)

    def test_has_unread_tag(self):
        """ Тестирует simple tag has_unread """
        context = Context({
            'user': self.user_manager
        })
        template = Template(
            "{% load door_tags %}"
            "<h1>{{ user|has_unread }}</h1>"
        )
        rendered = template.render(context)
        self.assertInHTML('<h1>True</h1>', rendered)
