from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ── Public Pages ──────────────────────────────────────────
    path('', views.index, name='index.html'),
    path('contact', views.contact, name='contact.html'),
    path('testimonial', views.testimonial, name='testimonial.html'),
    path('why', views.why, name='why.html'),
    path('shop', views.shop, name='shop.html'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    # Cart and Order URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:pk>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
     path('checkout/pay/<int:order_id>/', views.checkout_payment, name='checkout_payment'),
     path('checkout/verify/', views.checkout_verify, name='checkout_verify'),
     path('search/', views.search, name='search'),
     path('wishlist/', views.wishlist, name='wishlist'),
     path('wishlist/toggle/<int:pk>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('order/success/<int:pk>/', views.order_success, name='order_success'),
    path('my_orders/', views.my_orders, name='my_orders'),

    # ── Auth ──────────────────────────────────────────────────
    path('login', views.login_user, name='login'),
    path('logout_user', views.logout_user, name='logout'),
    path('register', views.register_user, name='register'),
    path('profile_user', views.profile_user, name='profile'),
    path('edit_profile_user', views.edit_profile, name='edit_profile_user'),
    path('change_password/', views.change_password, name='change_password'),

    # Password reset
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
         name='reset_password'),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_sent.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),

    # ── Product CRUD Dashboard ────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),
     path('dashboard/orders_by_user/', views.dashboard_orders_by_user, name='dashboard_orders_by_user'),
     path('dashboard/orders_by_user/<int:user_id>/', views.dashboard_orders_by_user_detail, name='dashboard_orders_by_user_detail'),

    # Shop products (GFT on /shop page)
    path('dashboard/add/', views.product_add, {'product_type': 'shop'}, name='product_add'),
    path('dashboard/edit/<int:pk>/', views.product_edit, {'product_type': 'shop'}, name='product_edit'),
    path('dashboard/delete/<int:pk>/', views.product_delete, {'product_type': 'shop'}, name='product_delete'),

    # Featured products (home page)
    path('dashboard/featured/add/', views.product_add, {'product_type': 'featured'}, name='featured_product_add'),
    path('dashboard/featured/edit/<int:pk>/', views.product_edit, {'product_type': 'featured'}, name='featured_product_edit'),
    path('dashboard/featured/delete/<int:pk>/', views.product_delete, {'product_type': 'featured'}, name='featured_product_delete'),

    # ── Payment ───────────────────────────────────────────────
    path('success', views.success, name='payment_status'),
    path('Book', views.book, name='book.html'),
]