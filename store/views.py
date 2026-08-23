from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Order, OrderItem

def product_list(request):
    query = request.GET.get('q', '').strip()

    products = Product.objects.all()

    if query:
        products = products.filter(
            name__icontains=query
        )

    return render(
        request,
        'store/product_list.html',
        {
            'products': products,
            'query': query
        }
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    return render(
        request,
        'store/product_detail.html',
        {'product': product}
    )




def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    current_quantity = cart.get(product_id, 0)

    if current_quantity < product.stock:
        cart[product_id] = current_quantity + 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def cart_view(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total = Decimal('0.00')

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
        except Product.DoesNotExist:
            continue

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(
        request,
        'store/cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


def increase_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    current_quantity = cart.get(product_id, 0)

    if current_quantity < product.stock:
        cart[product_id] = current_quantity + 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')

def register_view(request):

    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.success(
            request,
            'Registration successful.'
        )

        return redirect('product_list')

    return render(
        request,
        'store/register.html'
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            messages.success(
                request,
                'Login successful.'
            )

            return redirect('product_list')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(
        request,
        'store/login.html'
    )


def logout_view(request):
    logout(request)

    messages.success(
        request,
        'You have been logged out.'
    )

    return redirect('product_list')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    cart_items = []
    total = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':

        with transaction.atomic():

            locked_products = []
            final_total = Decimal('0.00')

            for item in cart_items:
                product = Product.objects.select_for_update().get(
                    id=item['product'].id
                )

                quantity = item['quantity']

                if quantity > product.stock:
                    messages.error(
                        request,
                        f'Not enough stock for {product.name}.'
                    )
                    return redirect('cart')

                final_total += product.price * quantity

                locked_products.append({
                    'product': product,
                    'quantity': quantity
                })

            order = Order.objects.create(
                user=request.user,
                total_amount=final_total,
                status='Completed'
            )

            for item in locked_products:
                product = item['product']
                quantity = item['quantity']

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )

                product.stock -= quantity
                product.save(update_fields=['stock'])

            request.session['cart'] = {}
            request.session.modified = True

            messages.success(
                request,
                'Order placed successfully.'
            )

            return redirect(
                'order_detail',
                order_id=order.id
            )

    return render(
        request,
        'store/checkout.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'store/order_history.html',
        {
            'orders': orders
        }
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'store/order_detail.html',
        {
            'order': order
        }
    )

def home(request):
    featured_products = Product.objects.all()[:3]

    return render(
        request,
        'store/home.html',
        {
            'featured_products': featured_products
        }
    )