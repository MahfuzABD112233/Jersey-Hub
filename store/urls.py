from django.urls import path
from . import views


urlpatterns = [
    # Products
    path('', views.home, name='home'),

path(
    'products/',
    views.product_list,
    name='product_list'
),

    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),

    # Cart
    path(
        'cart/',
        views.cart_view,
        name='cart'
    ),

    path(
        'cart/add/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/increase/<int:product_id>/',
        views.increase_quantity,
        name='increase_quantity'
    ),

    path(
        'cart/decrease/<int:product_id>/',
        views.decrease_quantity,
        name='decrease_quantity'
    ),

    path(
        'cart/remove/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    # Authentication
    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    # Order Processing
    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
        'orders/',
        views.order_history,
        name='order_history'
    ),

    path(
        'order/<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),
]