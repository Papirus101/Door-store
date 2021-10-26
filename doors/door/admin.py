from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Door, SashDoor, StyleDoor, MaterialDoor, CloserDoor, Order, Profile


@admin.register(Door, MaterialDoor, SashDoor, StyleDoor, CloserDoor)
class DoorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class UserInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Дополнительная информация'


class UserAdmin(UserAdmin):
    inlines = (UserInline, )


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('date_start', 'date_finish',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Order, OrderAdmin)
