from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from decimal import Decimal
import re
import razorpay

from .models import indexform, ContactForm, shopform, indexshop, UserProfile, Book, Order, OrderItem
from .models import Wishlist
from .forms import RegisterUserForm, UserProfileForm, ProductForm, FeaturedProductForm


# ─── Cart Helpers ────────────────────────────────────────────────────────────────

def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def cart_total_items(request):
    cart = get_cart(request)
    return sum(item['quantity'] for item in cart.values())

def cart_total_price(request):
    cart = get_cart(request)
    total = Decimal('0')
    for item in cart.values():
        total += Decimal(str(item['price'])) * item['quantity']
    return total


# ─── Public Pages ────────────────────────────────────────────────────────────────

def index(request):
    if request.method == 'POST':
        indexform(
            name=request.POST.get('NAME'),
            email=request.POST.get('EMAIL'),
            phone=request.POST.get('PHONE'),
            message=request.POST.get('MESSAGE')
        ).save()
        messages.success(request, 'Your message has been sent!')
    gift = indexshop.objects.all()
    return render(request, 'index.html', {'Gif': gift})


def contact(request):
    if request.method == 'POST':
        ContactForm(
            name=request.POST.get('NAME'),
            email=request.POST.get('EMAIL'),
            phone=request.POST.get('PHONE'),
            message=request.POST.get('MESSAGE')
        ).save()
        messages.success(request, 'Thank you! We will get back to you soon.')
    return render(request, 'contact.html')


def shop(request):
    products = shopform.objects.all()
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    return render(request, 'shop.html', {'GFT': products, 'wishlist_ids': wishlist_ids})


def testimonial(request):
    return render(request, 'testimonial.html')


def why(request):
    return render(request, 'why.html')


# ─── Product Detail ──────────────────────────────────────────────────────────────

def product_detail(request, pk):
    product = get_object_or_404(shopform, pk=pk)
    related = shopform.objects.exclude(pk=pk)[:4]
    return render(request, 'product_detail.html', {
        'product': product,
        'related': related,
    })


# ─── Cart Views ──────────────────────────────────────────────────────────────────

def cart_view(request):
    cart = get_cart(request)
    items = []
    total = Decimal('0')
    for pid, item in cart.items():
        subtotal = Decimal(str(item['price'])) * item['quantity']
        total += subtotal
        items.append({
            'id':       pid,
            'name':     item['name'],
            'price':    item['price'],
            'quantity': item['quantity'],
            'image':    item.get('image', ''),
            'subtotal': subtotal,
        })
    return render(request, 'cart.html', {'cart_items': items, 'cart_total': total})


def cart_add(request, pk):
    product = get_object_or_404(shopform, pk=pk)
    cart    = get_cart(request)
    pid     = str(pk)
    price   = product.price_numeric()

    if pid in cart:
        qty = int(request.POST.get('quantity', 1))
        cart[pid]['quantity'] += qty
    else:
        qty = int(request.POST.get('quantity', 1))
        cart[pid] = {
            'name':     product.Name,
            'price':    str(price),
            'quantity': qty,
            'image':    product.image.url if product.image else '',
        }
    save_cart(request, cart)
    messages.success(request, f'"{product.Name}" added to your cart!')
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/shop'))
    return redirect(next_url)


def cart_update(request, pk):
    cart = get_cart(request)
    pid  = str(pk)
    qty  = int(request.POST.get('quantity', 1))
    if pid in cart:
        if qty <= 0:
            del cart[pid]
        else:
            cart[pid]['quantity'] = qty
    save_cart(request, cart)
    return redirect('cart')


def cart_remove(request, pk):
    cart = get_cart(request)
    pid  = str(pk)
    if pid in cart:
        name = cart[pid]['name']
        del cart[pid]
        save_cart(request, cart)
        messages.success(request, f'"{name}" removed from cart.')
    return redirect('cart')


# ─── Checkout & Orders ───────────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    items = []
    total = Decimal('0')
    for pid, item in cart.items():
        subtotal = Decimal(str(item['price'])) * item['quantity']
        total += subtotal
        items.append({**item, 'id': pid, 'subtotal': subtotal})

    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        phone   = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([name, email, phone, address]):
            messages.error(request, 'Please fill in all delivery details.')
        else:
            payment_method = request.POST.get('payment_method', 'cod')
            try:
                # Create order and items in both flows; for online we'll redirect to payment
                order = Order.objects.create(
                    user=request.user,
                    name=name,
                    email=email,
                    phone=phone,
                    address=address,
                    total_amount=total,
                    status='pending',
                )
                for pid, item in cart.items():
                    try:
                        product = shopform.objects.get(pk=int(pid))
                    except shopform.DoesNotExist:
                        product = None
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        name=item['name'],
                        price=Decimal(str(item['price'])),
                        quantity=item['quantity'],
                    )

                if payment_method == 'online':
                    # Create Razorpay order and show payment page
                    client = razorpay.Client(auth=(
                        'rzp_test_VQhEfe2NCXbbwI',
                        '2ibreCYL78DA3kjOhobCvz0f'
                    ))
                    rp_order = client.order.create(dict(amount=int(total * 100), currency='INR', receipt=f'order_{order.pk}'))
                    order.razorpay_order_id = rp_order.get('id')
                    order.save()
                    # Clear cart now; if payment fails, admin can reconcile
                    save_cart(request, {})
                    return render(request, 'checkout_payment.html', {'razorpay_payment': rp_order, 'order': order, 'razorpay_key': 'rzp_test_VQhEfe2NCXbbwI'})
                else:
                    # Cash on Delivery flow
                    save_cart(request, {})
                    messages.success(request, f'Order #{order.pk} placed successfully! 🎉')
                    return redirect('order_success', pk=order.pk)
            except Exception as e:
                print(f"Order placement error: {e}")
                messages.error(request, 'An unexpected error occurred while placing your order. Please try again.')
                return redirect('checkout')

    # Pre-fill from profile if available
    try:
        profile = request.user.userprofile
        prefill = {
            'name':    f"{profile.fname} {profile.lname}".strip() or request.user.get_full_name(),
            'email':   profile.email or request.user.email,
            'phone':   profile.contact,
            'address': profile.address,
        }
    except Exception:
        prefill = {
            'name':    request.user.get_full_name(),
            'email':   request.user.email,
            'phone':   '',
            'address': '',
        }

    return render(request, 'checkout.html', {
        'cart_items': items,
        'cart_total': total,
        'prefill':    prefill,
    })


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'my_orders.html', {'orders': orders})


def search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        from django.db.models import Q
        results = shopform.objects.filter(
            Q(Name__icontains=q) | Q(description__icontains=q)
        )
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    return render(request, 'search_results.html', {'query': q, 'results': results, 'wishlist_ids': wishlist_ids})


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    products = [w.product for w in items]
    return render(request, 'wishlist.html', {'products': products})


@login_required
def wishlist_toggle(request, pk):
    product = get_object_or_404(shopform, pk=pk)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        action = 'removed'
    else:
        action = 'added'
    if request.is_ajax() or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'action': action, 'product_id': pk})
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


# ─── Auth Views ──────────────────────────────────────────────────────────────────

def login_user(request):
    if request.user.is_authenticated:
        return redirect('index.html')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', '/'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('index.html')


def register_user(request):
    if request.user.is_authenticated:
        return redirect('index.html')
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            messages.success(request, 'Account created! Welcome to Giftos 🎁')
            return redirect('profile')
    else:
        form = RegisterUserForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile_user(request):
    return render(request, 'profile.html')


@login_required
def edit_profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'editprofile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            update_session_auth_hash(request, form.save())
            messages.success(request, 'Password changed!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'changepassword.html', {'form': form})


# ─── Product CRUD Dashboard ──────────────────────────────────────────────────────

@login_required
def dashboard(request):
    from django.db.models import Sum

    shop_products = shopform.objects.all()
    featured_products = indexshop.objects.all()
    orders = Order.objects.all()
    total_orders = orders.count()
    revenue_agg = orders.aggregate(total_revenue=Sum('total_amount'))
    total_revenue = revenue_agg.get('total_revenue') or 0

    return render(request, 'dashboard.html', {
        'shop_products':     shop_products,
        'featured_products': featured_products,
        'orders':            orders,
        'total_orders':      total_orders,
        'total_revenue':     total_revenue,
    })


@login_required
def dashboard_orders_by_user(request):
    from django.db.models import Sum, Count
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('index.html')

    # Aggregate orders grouped by user
    user_stats = (
        Order.objects.values(
            'user__id', 'user__username', 'user__first_name', 'user__last_name', 'user__email'
        )
        .annotate(order_count=Count('id'), total_spent=Sum('total_amount'))
        .order_by('-order_count')
    )

    return render(request, 'dashboard_orders_by_user.html', {'user_stats': user_stats})


@login_required
def dashboard_orders_by_user_detail(request, user_id):
    from django.db.models import Sum
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('index.html')

    orders = Order.objects.filter(user__id=user_id).prefetch_related('items')
    total = orders.aggregate(total_spent=Sum('total_amount')).get('total_spent') or 0
    user = None
    if orders.exists():
        user = orders.first().user
    return render(request, 'dashboard_orders_by_user_detail.html', {'orders': orders, 'total': total, 'user': user})


@login_required
def product_add(request, product_type='shop'):
    FormClass = ProductForm if product_type == 'shop' else FeaturedProductForm
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added!')
            return redirect('dashboard')
    else:
        form = FormClass()
    return render(request, 'product_form.html', {'form': form, 'action': 'Add', 'product_type': product_type})


@login_required
def product_edit(request, pk, product_type='shop'):
    if product_type == 'shop':
        product, FormClass = get_object_or_404(shopform, pk=pk), ProductForm
    else:
        product, FormClass = get_object_or_404(indexshop, pk=pk), FeaturedProductForm
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated!')
            return redirect('dashboard')
    else:
        form = FormClass(instance=product)
    return render(request, 'product_form.html', {'form': form, 'action': 'Edit', 'product': product, 'product_type': product_type})


@login_required
def product_delete(request, pk, product_type='shop'):
    product = get_object_or_404(shopform if product_type == 'shop' else indexshop, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted!')
        return redirect('dashboard')
    return render(request, 'product_confirm_delete.html', {'product': product, 'product_type': product_type})


# ─── Admin: Order Management ─────────────────────────────────────────────────────

@login_required
def dashboard_orders(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('index.html')
    orders = Order.objects.all().prefetch_related('items')
    return render(request, 'dashboard_orders.html', {'orders': orders})


@login_required
def update_order_status(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('index.html')
    order  = get_object_or_404(Order, pk=pk)
    status = request.POST.get('status')
    valid  = [s[0] for s in Order.STATUS_CHOICES]
    if status in valid:
        order.status = status
        order.save()
        messages.success(request, f'Order #{order.pk} status updated to "{order.get_status_display()}"')
    return redirect('dashboard_orders')


# ─── Payment Views ───────────────────────────────────────────────────────────────

def book(request):
    if request.method == 'POST':
        name   = request.POST.get('name')
        phone  = request.POST.get('phone')
        email  = request.POST.get('email')
        amount = request.POST.get('amount')
        msg    = request.POST.get('message')
        client = razorpay.Client(auth=('rzp_test_VQhEfe2NCXbbwI', '2ibreCYL78DA3kjOhobCvz0f'))
        rp     = client.order.create(dict(amount=(int(amount) * 100), currency='INR'))
        booking = Book.objects.create(name=name, phone=phone, email=email, amount=amount, message=msg, order_id=rp['id'])
        rp.update({'name': name, 'amount': amount, 'order_id': rp['id']})
        return render(request, 'book.html', {'razorpay_payment': rp})
    return render(request, 'book.html', {})


def success(request):
    response    = request.POST
    params_dict = {
        'razorpay_order_id':   response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature':  response['razorpay_signature'],
    }
    client = razorpay.Client(auth=('rzp_test_VQhEfe2NCXbbwI', '2ibreCYL78DA3kjOhobCvz0f'))
    try:
        client.utility.verify_payment_signature(params_dict)
        b = Book.objects.get(order_id=response['razorpay_order_id'])
        b.razorpay_payment_id = response['razorpay_payment_id']
        b.paid = True
        b.save()
    except Exception as e:
        print(f"Payment error: {e}")
    return render(request, 'success.html', {'status': False})


@login_required
def checkout_payment(request, order_id):
    # Renders the payment page if we need to retry or view payment details
    order = get_object_or_404(Order, pk=order_id)
    if not order.razorpay_order_id:
        messages.error(request, 'No payment session found for that order.')
        return redirect('dashboard')
    rp = {'id': order.razorpay_order_id, 'amount': int(order.total_amount * 100)}
    return render(request, 'checkout_payment.html', {'razorpay_payment': rp, 'order': order, 'razorpay_key': 'rzp_test_VQhEfe2NCXbbwI'})


def checkout_verify(request):
    # Endpoint called by client after successful payment to verify signature
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=400)
    payload = request.POST
    order_id = payload.get('razorpay_order_id')
    payment_id = payload.get('razorpay_payment_id')
    signature = payload.get('razorpay_signature')
    client = razorpay.Client(auth=(
        'rzp_test_VQhEfe2NCXbbwI',
        '2ibreCYL78DA3kjOhobCvz0f'
    ))
    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature,
    }
    try:
        client.utility.verify_payment_signature(params_dict)
        order = Order.objects.filter(razorpay_order_id=order_id).first()
        if order:
            order.razorpay_payment_id = payment_id
            order.paid = True
            order.status = 'processing'
            order.save()
            return JsonResponse({'ok': True})
        else:
            return JsonResponse({'ok': False, 'error': 'Order not found'}, status=404)
    except Exception as e:
        print(f"Payment verification error: {e}")
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)