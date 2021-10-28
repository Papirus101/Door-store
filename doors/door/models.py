from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from phonenumber_field.modelfields import PhoneNumberField


class Door(models.Model):
    name = models.CharField('Дверь', max_length=150, blank=True)
    slug = models.SlugField('Ссылка на дверь ( генерируется автоматически )')
    description = models.TextField('Описание двери', blank=True, null=True)
    image = models.ImageField(
        'Картинка двери', upload_to='door/image_door/', blank=True, null=True)
    price = models.IntegerField(
        'Цена двери ( не обязательно )', blank=True, null=True)
    personal_margin = models.IntegerField('Персональная наценка', default=0, blank=True)
    show_on_index = models.BooleanField(
        'Показывать на главной странице', default=False)
    width = models.IntegerField('Ширина проёма')
    height = models.IntegerField('Высота проёма')
    depth = models.IntegerField('Глубина проёма')
    sash = models.ForeignKey('SashDoor', on_delete=models.PROTECT, related_name='sash', verbose_name='Количество створок',
                             blank=True, null=True)
    style = models.ForeignKey('StyleDoor', on_delete=models.SET_NULL, related_name='styles', verbose_name='Стиль двери',
                              blank=True, null=True)
    glass = models.BooleanField('Наличие стекла в двери', default=False)
    material = models.ForeignKey('MaterialDoor', on_delete=models.SET_NULL, related_name='materials', verbose_name='Материал двери',
                                 blank=True, null=True)
    closer = models.ForeignKey('CloserDoor', on_delete=models.SET_NULL,
                               related_name='closer', verbose_name='Тип доводчика', blank=True, null=True)

    class Meta:
        verbose_name = 'дверь'
        verbose_name_plural = 'двери'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse('door_detail', kwargs={"slug": self.slug})


class SashDoor(models.Model):
    name = models.CharField('Количество створок', max_length=20)
    slug = models.SlugField()
    price = models.IntegerField('Наценка за количество створок')

    class Meta:
        verbose_name = 'количество створок'
        verbose_name_plural = 'количество створок'

    def __str__(self):
        return str(self.name)


class StyleDoor(models.Model):
    name = models.CharField('Название стиля', max_length=100)
    image = models.ImageField(
        'Картинка двери в таком стиле', upload_to='door/style/')
    slug = models.SlugField()
    price = models.IntegerField('Наценка за этот стиль')

    class Meta:
        verbose_name = 'стиль'
        verbose_name_plural = 'стили'

    def __str__(self) -> str:
        return self.name


class MaterialDoor(models.Model):
    name = models.CharField('Название материала', max_length=100)
    slug = models.SlugField()
    description = models.TextField('Описание материала')
    image = models.ImageField('Картинка материала',
                              upload_to='door/materials/')
    price = models.IntegerField('Цена за 1м^2')

    class Meta:
        verbose_name = 'материал'
        verbose_name_plural = 'материалы'

    def __str__(self) -> str:
        return self.name


class CloserDoor(models.Model):
    name = models.CharField('Название доводчика', max_length=150)
    slug = models.SlugField()
    price = models.IntegerField('Наценка за определенный доводчик')

    class Meta:
        verbose_name = 'доводчик'
        verbose_name_plural = 'доводчики'

    def __str__(self) -> str:
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(blank=True)
    birth_day = models.DateField(null=True, blank=True)
    photo = models.ImageField(
        'Фото пользователя', upload_to='user/photo/', blank=True, null=True,
        default='user/photo/none_user.png')
    orders = models.ManyToManyField('Order', related_name='orders', verbose_name='заказы', blank=True)

    def get_absolute_url(self):
        return reverse('profile', kwargs={"pk": self.user.pk})


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Order(models.Model):
    door = models.ForeignKey(Door, on_delete=models.CASCADE,
                             related_name='doors', verbose_name='Дверь', null=True, blank=True)
    count_doors = models.PositiveIntegerField('Количество дверей', default=1, blank=True)
    user_phone = PhoneNumberField()
    user_email = models.EmailField('Почта', blank=True, null=True)
    active = models.BooleanField('Заказ находится в работе', default=True)
    date_start = models.DateField('Дата старта заказа', auto_now=True)
    date_finish = models.DateField(
        'Дата окончания заказа', blank=True, null=True)
    is_view = models.BooleanField('Просмотрено', default=False)
    company_name = models.CharField('Название компании', max_length=255, blank=True)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self) -> str:
        return f'Заказ №{self.door.pk}'

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})
