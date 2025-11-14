EcoHaven Documentation
Overview

EcoHaven is an e-commerce application designed to connect buyers and sellers through a seamless and user-friendly platform. It includes product management, cart functionality, order processing, and user authentication.

Features

User registration and login (buyers and sellers)

Product listing with variations (color, size, price, stock)

Product overview with variation selection

Search and category filtering

Cart system with merging identical items

Checkout and order processing

Shop and profile viewing

API integration with Flutter mobile app

Technology Stack
Backend

Flask (Python)

MySQL database

Frontend

HTML, CSS, JavaScript

Flutter mobile app

Database Schema (Summary)
Users

id, fullname, email, password, usertype, activation

Products

id, name, description, category_id, seller_id, image

ProductVariations

id, product_id, color, size, stock, price

Cart

id, user_id

CartItems

id, cart_id, product_id, variation_id, quantity

Orders

id, user_id, total_payment, status

OrderItems

id, order_id, product_id, variation_id, quantity, price

API Endpoints
Product API

GET /api/products — Fetch all products

GET /api/products/<id> — Fetch product details

Cart API

POST /api/add_to_cart — Add item to cart

GET /api/products_cart — Fetch grouped cart items

POST /api/update_quantity — Update cart item quantity

Flutter Integration
HomePage

Fetches product list from API

Displays categories and a product grid

ProductDetailsPage

Displays product info, seller info

Variation selection

Add to cart or buy now

Cart Page

Merges identical items

Updates quantity in database

Known Issues

Duplicate color display on product overview

CSS not limiting text lines on product names

Future Enhancements

Improved seller dashboard

Push notifications

Enhanced product recommendation system
