# 🎁 Gifto - Online Gift Shop

Gifto is a modern online gift shop web application built with Python and Django. 
Users can browse gifts, view product details, add products to their cart and wishlist, 
place orders, and manage their profiles.

The project also includes user authentication, product management, checkout, 
order management, and email functionality.

---

## 🚀 Live Demo

🌐 **Live Website:** https://gifto-4y2u.onrender.com/

---

## ✨ Features

### 👤 User Authentication
- User Registration
- User Login
- User Logout
- Password Change
- Password Reset
- User Profile Management
- Edit Profile

### 🛍️ Shopping Features
- Browse Products
- Product Details
- Product Search
- Add to Cart
- Update Cart Quantity
- Remove from Cart
- Wishlist
- Product Images
- Discounted Products

### 💳 Checkout & Orders
- Checkout System
- Order Placement
- Order Success Page
- Order History
- User-specific Orders

### 📧 Email
- Gmail SMTP Integration
- Password Reset Emails
- Order-related Email Functionality

### 👨‍💼 Admin / Management
- Product Management
- Add Product
- Edit Product
- Delete Product
- Order Management
- User Management through Django Admin

### 🎨 UI
- Responsive Design
- Bootstrap
- Custom CSS
- Font Awesome
- Responsive Layout
- Modern Gift Shop Interface

---

## 🛠️ Technologies Used

- Python
- Django
- SQLite
- HTML5
- CSS3
- JavaScript
- Bootstrap
- Font Awesome
- Django Authentication
- WhiteNoise
- Gunicorn
- Git & GitHub
- Render

---

## 📁 Project Structure

```text
Gifto/
│
├── myshop/
│   └── project/
│       ├── manage.py
│       │
│       ├── myshop/
│       │   ├── settings.py
│       │   ├── urls.py
│       │   ├── wsgi.py
│       │   └── context_processors.py
│       │
│       ├── shop/
│       │   ├── models.py
│       │   ├── views.py
│       │   ├── urls.py
│       │   ├── admin.py
│       │   └── migrations/
│       │
│       ├── Template/
│       │   ├── base.html
│       │   ├── index.html
│       │   ├── shop.html
│       │   ├── cart.html
│       │   ├── checkout.html
│       │   ├── login.html
│       │   ├── register.html
│       │   └── ...
│       │
│       ├── static/
│       │   ├── css/
│       │   ├── js/
│       │   ├── images/
│       │   └── fonts/
│       │
│       ├── media/
│       ├── db.sqlite3
│       └── requirements.txt
│
└── README.md
