# GreatShop 🛍️

![GreatShop Banner](https://github.com/vipulc2580/GreatShop/blob/main/static/images/logo.png)  
*A modern and responsive eCommerce platform built with Django, designed for a seamless shopping experience.*

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Acknowledgements](#acknowledgements)

## Introduction

GreatShop is a full-featured online shopping website developed using Django. It supports product listings, shopping cart, user authentication, PayPal integration, coupon discounts, and a powerful admin panel for order and user management. The goal is to deliver a smooth and intuitive user experience for customers, vendors, and admins alike.

## Features

- **User Authentication**  
  User registration, login, logout, and profile management.

- **Product Browsing**  
  Visually appealing and responsive product listings with categories and search.

- **Product Detail Page**  
  Includes image gallery, detailed description, rating display, and Add to Cart functionality.

- **Shopping Cart**  
  Add, remove, and update product quantities dynamically.

- **Checkout & Orders**  
  Streamlined checkout process with order summary, address form, and PayPal integration.

- **Coupon & Discounts System**  
  Personalized coupon generation, 2-day expiry, automatic application, and admin CSV upload.

- **Admin Dashboard**  
  Manage products, orders, users, and discount coupons through Django admin.

- **Email Notifications**  
  Email verification and coupon distribution system integrated via Django background tasks.

## Technologies Used

- **Backend:** Python, Django, Django REST Framework  
- **Frontend:** HTML5, CSS3, Bootstrap, JavaScript, jQuery  
- **Database:** SQLite (default), can be configured for PostgreSQL/MySQL  
- **Others:** PayPal SDK, Celery (for background tasks), Redis, AJAX

## Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/vipulc2580/GreatShop.git
   cd GreatShop
    ```

2. **Create and activate a virtual environment:**
    ```python 
      python -m venv env
      env\Scripts\activate  # On macOS/Linux use: source env/bin/activate
    ```

3. **Install dependencies:**
    ```python
    
       pip install -r requirements.txt
    ```    

4. **Apply migrations:**
    ```python 
      python manage.py makemigrations
      python manage.py migrate
    ```

5. **Create a superuser (for admin access):**
    ```python
      python manage.py createsuperuser
    ```
6. **Run the development server**
   ```python
       python manage.py runserver
   ```

7. **Access the application:**
    Visit http://127.0.0.1:8000 in your browser.

# Usage
  ## Customer Experience:
  - Register/login to your account.
  - Browse through products and view details.
  - Add items to the cart and proceed to checkout using PayPal.
  - Apply discount coupons during checkout (if any).
  
  ## Admin Panel:
  - Access via /admin URL.
  - Add/edit/delete products, view orders, manage users, upload coupon CSVs.

  ## Email & Coupons:
  - Email verification during signup.
  - Personalized discount coupons sent via email (valid for 2 days).
 
 # Acknowledgements
  - Big thanks to the Django community and open-source contributors.
  - Special appreciation for tools and libraries like Bootstrap, PayPal SDK, Celery, and Redis.
  - Inspired by modern eCommerce platforms to make shopping simple and enjoyable! 💚
