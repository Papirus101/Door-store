from django import template
from ..models import Profile
from ..logic.calculate import calculate_door

register = template.Library()


@register.simple_tag
def size_price(door_id):
    sum = calculate_door(door_id)
    return {'summ': sum}


@register.filter(name='has_manager') 
def has_group(user):
    return user.groups.filter(name='Менеджер').exists()


@register.filter(name='has_unread')
def has_unread(user):
    return Profile.objects.filter(pk=user.pk, orders__is_view=False).exists()