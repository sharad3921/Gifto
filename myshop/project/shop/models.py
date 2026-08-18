from django.db import models
from django.contrib.auth.models import User


class ContactForm(models.Model):
    name    = models.CharField(max_length=50)
    email   = models.EmailField(max_length=50)
    phone   = models.CharField(max_length=10)
    message = models.TextField()


class indexform(models.Model):
    name    = models.CharField(max_length=50)
    email   = models.EmailField(max_length=50)
    phone   = models.CharField(max_length=10)
    message = models.TextField()


class shopform(models.Model):
    image       = models.ImageField(upload_to='shopform')
    Name        = models.CharField(max_length=100)
    Price       = models.CharField(max_length=50)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.Name

    def price_numeric(self):
        """Return price as a float, stripping currency symbols."""
        import re
        cleaned = re.sub(r'[^\d.]', '', str(self.Price))
        try:
            return float(cleaned)
        except ValueError:
            return 0.0


class indexshop(models.Model):
    image = models.ImageField(upload_to='indexshop')
    Name  = models.CharField(max_length=100)
    Price = models.CharField(max_length=50)

    def __str__(self):
        return self.Name


class UserProfile(models.Model):
    user      = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    fname     = models.CharField(max_length=50)
    lname     = models.CharField(max_length=50)
    bio       = models.TextField()
    email     = models.EmailField()
    birthdate = models.DateField(blank=True, null=True)
    contact   = models.CharField(max_length=10)
    gender    = models.CharField(max_length=20)
    address   = models.TextField()

    def __str__(self):
        return f"{self.fname} {self.lname}"


class Book(models.Model):
    name                = models.CharField(max_length=100)
    phone               = models.CharField(max_length=10, null=True)
    email               = models.EmailField(max_length=25)
    amount              = models.CharField(max_length=5)
    message             = models.TextField()
    order_id            = models.CharField(max_length=100, blank=True)
    paid                = models.BooleanField(default=False)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name + (" paid" if self.paid else " not paid")


# ─── Order System ────────────────────────────────────────────────────────────────

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
    ]
    STATUS_ICONS = {
        'pending':    '⏳',
        'processing': '🔧',
        'shipped':    '🚚',
        'delivered':  '✅',
        'cancelled':  '❌',
    }
    STATUS_COLORS = {
        'pending':    '#f5a623',
        'processing': '#3366ff',
        'shipped':    '#9b59b6',
        'delivered':  '#27ae60',
        'cancelled':  '#e74c3c',
    }

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    name         = models.CharField(max_length=100)
    email        = models.EmailField()
    phone        = models.CharField(max_length=15)
    address      = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)
    # Payment fields
    razorpay_order_id   = models.CharField(max_length=120, blank=True)
    razorpay_payment_id = models.CharField(max_length=120, blank=True)
    paid                = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} — {self.name}"

    def status_icon(self):
        return self.STATUS_ICONS.get(self.status, '')

    def status_color(self):
        return self.STATUS_COLORS.get(self.status, '#888')


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(shopform, on_delete=models.SET_NULL, null=True)
    name     = models.CharField(max_length=100)   # snapshot at time of purchase
    price    = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.name}"


class Wishlist(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(shopform, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} → {self.product.Name}"