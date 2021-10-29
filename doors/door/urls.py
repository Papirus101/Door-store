from django.urls import path
from .views import ConstrucorDoor, DoorDetail, EditOrderManager, Index, OrderDetail, OrdersList, ProfileView, \
    register, login_user, logout_user, CheckEdit

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('orders/open/<str:username>/', OrdersList.as_view(), name='orders_open'),
    path('order/<int:pk>/', OrderDetail.as_view(), name='order_detail'),
    path('order/edit/<int:pk>/', EditOrderManager.as_view(), name='edit_order_manager'),
    path('order/send_check/<int:pk>/', CheckEdit.as_view(), name='send_edt_check'),
    # path('order/send_check_order/<int:pk>', )
    path('constructor/', ConstrucorDoor.as_view(), name='constructor'),
    path('door/<str:slug>/', DoorDetail.as_view(), name='door_detail'),
]
