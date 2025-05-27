from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash, session,jsonify,Response, make_response
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
import os
from flask_mail import Mail, Message
import base64
from werkzeug.utils import secure_filename
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from fpdf import FPDF
from io import BytesIO

from datetime import datetime, timedelta

# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'ecoheaven_db'
}

app = Flask(__name__)
app.secret_key = 'abcd' 
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

##mobile 
#login
@app.route('/api/login', methods=['POST'])
def get_buyer():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM users 
        WHERE email = %s 
        AND role_id IN (1, 4) 
        AND approval = 1;
    """, (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        # Get buyer_id only if role is 1 (buyer)
        buyer_id_value = None
        if user['role_id'] == 1:
            cursor.execute("SELECT buyer_id FROM buyers WHERE email = %s", (email,))
            buyer_id = cursor.fetchone()
            buyer_id_value = int(buyer_id['buyer_id']) if buyer_id else None
        else: 
            cursor.execute("SELECT rider_id FROM riders WHERE email = %s", (email,))
            buyer_id = cursor.fetchone()
            buyer_id_value = int(buyer_id['rider_id']) if buyer_id else None

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Login successful",
            "buyer_id": buyer_id_value,
            "role_id": user['role_id']
        }), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({"message": "Invalid credentials or not approved"}), 401


    
#homepage
@app.route('/api/products')
def get_products():
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Main products query
        cursor.execute("""
            SELECT 
                p.id, p.Product_Name, p.Description, p.Price,
                p.Stock_Quantity, p.Status, p.Seller_Id, p.Image,
                p.category, s.shop_description, s.profile_pic,
                s.shop_logo, s.shop_name
            FROM products p
            JOIN sellers s ON p.Seller_Id = s.Seller_Id
            WHERE p.Status = 'Active'
        """)
        products = cursor.fetchall()

        if not products:
            return jsonify({'products': []})

        # Get all product IDs for batch query
        product_ids = [str(product['id']) for product in products]
        
        # Batch ratings query
        cursor.execute(f"""
            SELECT 
                product_id, 
                ROUND(AVG(rate), 1) AS average_rate
            FROM rating
            WHERE product_id IN ({','.join(product_ids)})
            GROUP BY product_id
        """)
        ratings = {row['product_id']: row['average_rate'] for row in cursor.fetchall()}

        # Batch sales count query (if order_items table exists)
        cursor.execute(f"""
           SELECT 
       product_id, 
                COUNT(*) AS total_sold
            FROM orders
            WHERE  order_status = 'Completed' AND product_id IN ({','.join(product_ids)})
            GROUP BY product_id
        """)
        sales = {row['product_id']: row['total_sold'] for row in cursor.fetchall()}

        # Build response
        products_list = []
        for product in products:
            products_list.append({
                'id': product['id'],
                'Product_Name': product['Product_Name'],
                'Description': product['Description'],
                'Price': product['Price'],
                'Stock_Quantity': product['Stock_Quantity'],
                'Status': product['Status'],
                'Seller_Id': product['Seller_Id'],
                'Image': product['Image'],
                'category': product['category'],
                'shop_description': product['shop_description'],
                'profile_pic': product['profile_pic'],
                'shop_logo': product['shop_logo'],
                'shop_name': product['shop_name'],
                'rating': ratings.get(product['id'], 0),
                'sold': sales.get(product['id'], 0)  # Placeholder until sales query is implemented
            })

        return jsonify({'products': products_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

            

@app.route('/api/products_cart', methods=['GET'])
def get_products_cart():
    buyer_id = request.args.get('buyer_id')
    print(buyer_id)

    if not buyer_id:
        return jsonify({'status': 'error', 'message': 'Missing buyer_id'}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                p.Product_Name, 
                c.quantity, 
                p.Price, 
                p.Image,
                p.category,
                p.Description, 
                s.Shop_Name, 
                p.Id AS product_id, 
                v.color, 
                v.size, 
                c.id AS cart_id, 
                p.Price * c.quantity AS total
                       
            FROM cart_items c
            JOIN products p ON c.Product_Id = p.Id
            JOIN sellers s ON p.Seller_Id = s.seller_id
            LEFT JOIN productvariations v ON c.variation_id = v.id
            WHERE c.Buyer_Id = %s
        """, (buyer_id,))

        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({'status': 'success', 'cart_items': {}, 'total_payment': 0})

        cart_items_grouped = {}
        for item in cart_items:
            shop_name = item['Shop_Name']
            if shop_name not in cart_items_grouped:
                cart_items_grouped[shop_name] = []
            cart_items_grouped[shop_name].append({
                'product_id': item['product_id'],
                'product_name': item['Product_Name'],
                'quantity': item['quantity'],
                'price': item['Price'],
                'image': item['Image'],
                'color': item.get('color'),
                'size': item.get('size'),
                'cart_id': item['cart_id'],
                'total': item['total'],
                'category' :item['category'],
                'description': item['Description']
            })

        total_payment = sum(item['total'] for item in cart_items)
        

        return jsonify({
            'status': 'success',
            'cart_items': cart_items_grouped,
            'total_payment': total_payment
        })

    except Exception as e:
        
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cursor.close()
        connection.close()

@app.route('/checkoutPostMobile', methods=['POST'])
def checkoutPostMobile():
    
    user_id =  request.form.get('buyer_id')
    buying = request.form.get('buying')
    quantity = request.form.get('quantity')
    variation_id = request.form.get('variation_id')
    product_id = request.form.get('product_id')
    cart_items = request.form.get('cart_ids[]', '').split(',')
    # print(f' buyer id {user_id}')
    # print(f'buying {buying}')
    # print(f'qantity{quantity}')
    # print(f'variation{variation_id}')
    # print(f'product id {product_id}')
    # print(f'cart iterms {cart_items}')


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if buying == '1':
        # Direct Buy
        query = """
            SELECT *, 
                   productvariations.color, 
                   productvariations.size, 
                   productvariations.id AS variation_id,
                   products.Price * %s AS total_price
            FROM products
            JOIN productvariations ON productvariations.id = %s
            JOIN sellers ON products.Seller_Id = sellers.seller_id
            WHERE productvariations.id = %s
              AND products.Id = %s
        """
        cursor.execute(query, (quantity, variation_id, variation_id, product_id))
        checkout_items = cursor.fetchall()
        # print(checkout_items)

        for item in checkout_items:
            cursor.execute('''
                INSERT INTO orders (buyer_id, product_id, seller_id, order_status, 
                                    quantity, total_price, variation_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, item['Id'], item['Seller_Id'], 'pending', quantity, item['total_price'], item['variation_id']))
        connection.commit()
        # print(f'user 1d {user_id} , itemid {item['Id']}')

        return "completed"

    else:
        # Cart Checkout
        # print("ito dapat pag zero'")
        if not cart_items:
            flash('No items in the cart.', 'warning')
            return redirect(url_for('cart'))

        placeholders = ', '.join(['%s'] * len(cart_items))
        # print(cart_items)
        query = f"""
            SELECT cart_items.*, 
                   (cart_items.quantity * products.Price) AS total_price,
                   products.Product_Name, products.Price, 
                   productvariations.color, productvariations.size, 
                   products.Image, products.Seller_Id
            FROM cart_items
            JOIN productvariations ON cart_items.variation_id = productvariations.Id
            JOIN products ON cart_items.product_id = products.Id
            JOIN sellers ON products.Seller_Id = sellers.seller_id
            WHERE cart_items.id IN ({placeholders}) AND cart_items.buyer_id = %s
        """
        cursor.execute(query, cart_items + [user_id])
        checkout_items = cursor.fetchall()
        # print(f'ito sa chek out isang item land dapat !!!!!!!!!{checkout_items}')
        

        for item in checkout_items:
            cursor.execute('''
                INSERT INTO orders (buyer_id, product_id, seller_id, order_status,
                                    quantity, total_price, variation_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, item['product_id'], item['Seller_Id'], 'pending', item['quantity'], item['total_price'], item['variation_id']))

        # Clear cart
        delete_query = f"DELETE FROM cart_items WHERE id IN ({placeholders}) AND buyer_id = %s"
        cursor.execute(delete_query, cart_items + [user_id])

        connection.commit()
        cursor.close()

        flash('Your order has been placed successfully!', 'success')
        return  "Your order has been placed successfully!"




@app.route('/buyer_dashboard/add_to_cart/mobile', methods=['POST'])
def add_to_cart_mobile():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))  
    buyer_id = request.form.get('buyer_id')
    description = request.form.get('description')
    productName = request.form.get('productName')
    color = request.form.get('selected_color')
    size = request.form.get('selected_size')
    shop_name = request.form.get('shop_name')
    price = float(request.form.get('price', 0)) 
    product_image = request.form.get('product_image')

    # print("[DEBUG] Received Data:")
    # print("product_id:", product_id)
    # print("quantity:", quantity)
    # print("buyer_id:", buyer_id)
    # print("description:", description)
    # print("productName:", productName)
    # print("color:", color)
    # print("size:", size)
    # print("shop_name:", shop_name)
    # print("price:", price)
    # print("product_image:", product_image)

    if not all([product_id, buyer_id, productName, description, price]):
        # print("[DEBUG] Missing required fields.")
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS variation_count FROM productvariations WHERE product_id = %s", (product_id,))
        has_variations = cursor.fetchone()['variation_count'] > 0
        # print("[DEBUG] Has variations:", has_variations)

        variation_data = None
        if has_variations:
            if color and size:
                cursor.execute("SELECT id FROM productvariations WHERE color = %s AND size = %s AND product_id = %s", (color, size, product_id))
            elif color:
                cursor.execute("SELECT id FROM productvariations WHERE color = %s AND size IS NULL AND product_id = %s", (color, product_id))
            elif size:
                cursor.execute("SELECT id FROM productvariations WHERE size = %s AND color IS NULL AND product_id = %s", (size, product_id))
            
            variation_data = cursor.fetchone()
            # print("[DEBUG] Variation data:", variation_data)

            if variation_data is None:
                print("[DEBUG] Variation not found.")
                return jsonify({'status': 'error', 'message': 'The selected variety is not available.'}), 400

        variation_id = variation_data['id'] if variation_data else 0

        # print("[DEBUG] Using variation_id:", variation_id)

        cursor.execute("SELECT * FROM cart_items WHERE buyer_id = %s AND product_id = %s AND variation_id = %s", 
                       (buyer_id, product_id, variation_id))
        existing_item = cursor.fetchone()
        # print("[DEBUG] Existing cart item:", existing_item)

        if existing_item:
            new_quantity = existing_item['quantity'] + quantity
            cursor.execute("""
                UPDATE cart_items 
                SET quantity = %s
                WHERE id = %s
            """, (new_quantity, existing_item['id']))
            # print("[DEBUG] Cart updated with new quantity:", new_quantity)
        else:
            total_price = price * quantity
            cursor.execute("""
                INSERT INTO cart_items (buyer_id, product_id, quantity, product_name, price, Description, shop_name, product_image, variation_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (buyer_id, product_id, quantity, productName, price, description, shop_name, product_image, variation_id))
            print("[DEBUG] New item inserted into cart.")

        connection.commit()
        return jsonify({'status': 'success', 'message': f'{productName} added to your cart.'}), 200

    except Exception as e:
        connection.rollback()
        print("[DEBUG] Exception occurred:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cursor.close()
        connection.close()
        print("[DEBUG] Database connection closed.")



#delete one product 
@app.route('/delete_cart_item_mobile', methods=['POST'])
def delete_cart_item_mobile():
    item_id = request.form.get('item_id')
    buyer_id = request.form.get('buyer_id')
    print(item_id)

    if not item_id or not buyer_id:
        return jsonify({'status': 'error', 'message': 'Item ID or Buyer ID missing'}), 400

    try:
        item_id = int(item_id)
        buyer_id = int(buyer_id)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid ID format'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM cart_items WHERE id = %s AND buyer_id = %s", (item_id, buyer_id))
        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({'status': 'success', 'message': 'Item deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Item not found'}), 404
    except Exception as e:
        connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/delete_cart_allitem_mobile', methods=['POST'])
def delete_cart_allitem_mobile():
    buyer_id = request.form.get('buyer_id')

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM cart_items WHERE buyer_id = %s", (buyer_id,))
        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({'status': 'success', 'message': 'Items deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'No items found'}), 404
    except Exception as e:
        connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/user-ordersmoble', methods=['POST'])
def user_ordersmobile():
    user_id = request.form.get('buyer_id')
    print(user_id)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch orders with product details
    cursor.execute('''
        SELECT 
            orders.order_id,
            orders.created_at,
            orders.quantity,
            orders.total_price + 35 AS total_price,
            orders.order_status,
            products.product_name,
            products.image AS product_image,
            products.Price,
            productvariations.color,
            productvariations.size
        FROM orders
        JOIN products ON orders.product_id = products.Id
        JOIN productvariations ON orders.variation_id = productvariations.id
        WHERE orders.buyer_id = %s
        ORDER BY orders.created_at DESC;
    ''', (user_id,))
    
    orders = cursor.fetchall()

    print(orders)
    for order in orders:
        order['created_at'] = order['created_at'].isoformat()

    
    # Instead of grouping by date, return individual products
    cursor.close()
    connection.close()
    
    return jsonify({
        'status': 'success',
        'orders': orders  # Return a list of orders without grouping by date
    })

@app.route('/buyer_dashboard/seller-profileMobile/<shop_name>', methods=['GET'])
def buyersellerprofileMobile(shop_name):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    print(shop_name)
    try:
        # Get seller info
        cursor.execute("SELECT * FROM sellers WHERE shop_name = %s", (shop_name,))
        seller = cursor.fetchone()
        if not seller:
            return jsonify({'error': 'Shop not found'}), 404

        # Get products with stats
        cursor.execute("""
            SELECT p.Id, p.Product_Name, p.image, p.price, p.description,
                   IFNULL(SUM(o.quantity), 0) AS total_sold,
                   ROUND(AVG(r.rate), 1) AS average_rate
            FROM products p
            LEFT JOIN orders o ON o.product_id = p.Id AND o.order_status = 'Completed'
            LEFT JOIN rating r ON r.product_id = p.Id
            LEFT JOIN sellers s ON s.seller_id = p.Seller_Id
            WHERE s.shop_name = %s
            GROUP BY p.Id
        """, (shop_name,))
        products = cursor.fetchall()
        

        return jsonify({
            'shop_name': seller['shop_name'],
            'shop_image': seller.get('profile_image', ''),
            'location': seller.get('location', ''),
            'products': products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/buyer_dashboard/buyer_profile/mobile', methods=['POST'])
def Buyer_profile_mobile():
    buyer_id = request.form.get('buyer_id')
    print("Buyer ID:", buyer_id)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * 
            FROM addresses_buyer 
            JOIN buyers ON addresses_buyer.buyer_id = buyers.buyer_id 
            WHERE buyers.buyer_id = %s;
        """, (buyer_id,))
        user = cursor.fetchone()
        print("User:", user)

        if user:
            user_data = {
                'Fname': user['Fname'],
                'Mname': user['Mname'],
                'Lname': user['Lname'],
                'gender': user['gender'],
                'houseNo': user['houseNo'],
                'street': user['street'],
                'barangay': user['barangay'],
                'city': user['city'],
                'Province': user['Province'],
                'postal_code': user['postal_code'],
                'email': user['email'],
                'contact_num': user['mobile_number'],
                'birthday': user['birthdate'],
                # Optional profile pic if available
                'profile_pic': user['profile_pic'],
            }
            return jsonify(user_data)
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

    finally:
        cursor.close()
        connection.close()
        
UPLOAD_FOLDER = 'static/uploads/'

@app.route('/assets/upload/<filename>')
def uploaded_file_mobile(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/update_cart_quantity_mobile', methods=['POST'])
def update_cart_quantity_mobile():
    item_id = request.form.get('item_id')
    quantity_str = request.form.get('quantity')
    print(item_id)
    print(quantity_str)

    if not item_id or not quantity_str:
        return jsonify({'status': 'error', 'message': 'Invalid item or quantity'}), 400

    try:
        new_quantity = int(quantity_str)
        if new_quantity < 1:
            return jsonify({'status': 'error', 'message': 'Quantity must be at least 1'}), 400
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Quantity must be a number'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # First check if the item exists
        cursor.execute("SELECT price FROM cart_items WHERE id = %s", (item_id,))
        item = cursor.fetchone()

        if item is None:
            return jsonify({'status': 'error', 'message': f"Item not found in the cart for item ID: {item_id}"}), 404

        price = item[0]
        total_price = price * new_quantity

        # Update quantity now that we know it exists
        cursor.execute("""
            UPDATE cart_items 
            SET quantity = %s 
            WHERE id = %s
        """, (new_quantity, item_id))

        connection.commit()

        return jsonify({'status': 'success', 'new_total_price': total_price})

    except Exception as e:
        connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cursor.close()
        connection.close()

#mobile chat
@app.route('/chatMobile/<string:shop_name>/<int:buyer_id>', methods=['GET', 'POST'])
def chatMobile(shop_name, buyer_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get seller_id from shop_name
        cursor.execute("SELECT seller_id FROM sellers WHERE shop_name = %s", (shop_name,))
        seller = cursor.fetchone()
        if not seller:
            return jsonify({'error': 'Seller not found'}), 404
        
        seller_id = seller['seller_id']

        if request.method == 'POST':
            data = request.json
            message = data.get('message')
            
            if not message:
                return jsonify({'error': 'Message cannot be empty'}), 400

            # ALWAYS use buyer_id as sender for this endpoint
            cursor.execute(
                "INSERT INTO messages (sender_id, receiver_id, message, timestamp) VALUES (%s, %s, %s, %s)",
                (buyer_id, seller_id, message, datetime.now())  # Buyer → Seller
            )
            connection.commit()

        # Fetch chat messages
        cursor.execute(
            """
            SELECT sender_id, receiver_id, message, timestamp 
            FROM messages
            WHERE (sender_id = %s AND receiver_id = %s) 
               OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
            """, 
            (buyer_id, seller_id, seller_id, buyer_id)
        )
        messages = cursor.fetchall()

        return jsonify({'messages': messages})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/chatMobile', methods=['GET'])
def allchatMobile():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    buyer_id = request.args.get('buyer_id')
    if not buyer_id:
        return jsonify({'error': 'buyer_id required'}), 400

    cursor.execute("""
        SELECT 
            s.shop_name, 
            s.shop_logo, 
            m.message AS last_message, 
            m.timestamp AS last_message_time,
            m.sender_id, 
            m.receiver_id
        FROM sellers s
        JOIN messages m ON s.seller_id = m.receiver_id
        WHERE 
            m.sender_id = %s
            AND m.timestamp = (
                SELECT MAX(timestamp) 
                FROM messages 
                WHERE sender_id = m.sender_id AND receiver_id = m.receiver_id
            );
    """, (buyer_id,))

    chats = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(chats)

@app.route('/searchMobile', methods=['GET'])
def searchmobile():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    search = request.args.get('search', '').strip()

    cursor.execute("SELECT * FROM products WHERE Product_Name LIKE %s", ('%' + search + '%',))
    products = cursor.fetchall()
    for product in products:
        product_id = product['Id']

        # Calculate total sold quantity
        cursor.execute("""
            SELECT SUM(orders.quantity) AS total_sold
            FROM orders
            WHERE orders.order_status = 'Completed'
            AND orders.product_id = %s;
        """, (product_id,))
        sold = cursor.fetchone()
        product['total_sold'] = sold['total_sold'] if sold and sold['total_sold'] else 0

        # Calculate average rating
        cursor.execute("""
            SELECT ROUND(AVG(rate), 1) AS average_rate
            FROM rating
            WHERE product_id = %s;
        """, (product_id,))
        rate = cursor.fetchone()
        product['Rating'] = rate['average_rate'] if rate and rate['average_rate'] else 0

    cursor.close()
    connection.close()
    return jsonify(products)


@app.route('/notificationMobile')
def notificationMobile():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    buyer_id = request.args.get('buyer_id')  # Changed from form to args
    print(buyer_id)
    
    try:
        cursor.execute("""SELECT *
                        FROM buyers_reported 
                        JOIN sellers ON sellers.seller_id = buyers_reported.seller_id
                        WHERE buyer_id = %s""", (buyer_id,))
        reports = cursor.fetchall()

        cursor.execute(""" SELECT 
                        n.cancel_reason, 
                        s.shop_name,
                        o.updated_at,
                        o.total_price
                    FROM notification_buyer n
                    JOIN orders o ON o.order_id = n.order_id
                    JOIN sellers s ON s.seller_id = n.seller_id
                    WHERE o.buyer_id =%s""",  # Fixed join condition
                      (buyer_id,))
        cancelled = cursor.fetchall()

        cursor.execute(""" SELECT 
                        o.*,
                        p.product_name,
                        p.price,
                        p.category,
                        s.shop_name
                        
                    FROM orders o
                    JOIN products p ON p.Id = o.product_id
                    JOIN sellers s on s.seller_id = o.seller_id
                    WHERE o.buyer_id =%s
                    ORDER BY o.updated_at DESC""", (buyer_id,))
        orders = cursor.fetchall()
        
    finally:
        cursor.close()
        connection.close()
    
    return {
        'reports': reports,
        'orders': orders,
        'cancelled': cancelled
    }



@app.route('/update-profile-imagemobile', methods=['POST'])
def update_profile_imageMobile():
    try:
        # Get buyer_id from form data
        buyer_id = request.form.get('buyer_id')
        if not buyer_id:
            return jsonify({'error': 'buyer_id is required'}), 400

        # Check if image exists
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image = request.files['image']
        if image.filename == '':
            return jsonify({'error': 'Empty image'}), 400

        if not allowed_file(image.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Generate secure filename
        filename = f"profile_{buyer_id}_{secure_filename(image.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save file
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image.save(filepath)

        # Update database
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE buyers 
            SET profile_pic = %s 
            WHERE buyer_id = %s
        """, (filename, buyer_id))
        
        connection.commit()
        return jsonify({'success': True, 'filename': filename}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        cursor.close()
        connection.close()

@app.route('/update-account-infomobile', methods=['POST'])
def update_account_infoMobile():
    try:
        buyer_id = request.form.get('buyer_id')
        email = request.form.get('email')
        password = request.form.get('password')

        if not buyer_id:
            return jsonify({'error': 'buyer_id is required'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        # Get user_id
        cursor.execute("SELECT user_id FROM buyers WHERE buyer_id = %s", (buyer_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_id = user['user_id']

        # Update users table
        if password:
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                UPDATE users 
                SET email = %s, password = %s
                WHERE user_id = %s
            """, (email, hashed_password, user_id))
        else:
            cursor.execute("""
                UPDATE users 
                SET email = %s
                WHERE user_id = %s
            """, (email, user_id))

        # Update buyers table
        cursor.execute("""
            UPDATE buyers 
            SET email = %s
            WHERE buyer_id = %s
        """, (email, buyer_id))

        connection.commit()
        return jsonify({'success': True}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        cursor.close()
        connection.close()

@app.route('/update-account-personal-infoMoblie', methods=['POST'])
def update_account_personal_infoMobile():
    try:
        buyer_id = request.form.get('buyer_id')
        fname = request.form.get('fname')
        mname = request.form.get('mname')
        lname = request.form.get('lname')
        contact_num = request.form.get('number')
        gender = request.form.get('gender')

        if not buyer_id:
            return jsonify({'error': 'buyer_id is required'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE buyers
            SET Fname = %s, Mname = %s, Lname = %s, 
                contact_num = %s, gender = %s
            WHERE buyer_id = %s
        """, (fname, mname, lname, contact_num, gender, buyer_id))

        connection.commit()
        return jsonify({'success': True}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        cursor.close()
        connection.close()

@app.route('/update-address-buyerMobile', methods=['POST'])
def update_address_buyemobile():
    try:
        buyer_id = request.form.get('buyer_id')
        houseNo = request.form.get('houseNo')
        street = request.form.get('street')
        barangay = request.form.get('barangay')
        city = request.form.get('city')
        province = request.form.get('Province')
        postal_code = request.form.get('postal')

        if not buyer_id:
            return jsonify({'error': 'buyer_id is required'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if address exists
        cursor.execute("SELECT 1 FROM addresses_buyer WHERE buyer_id = %s", (buyer_id,))
        address_exists = cursor.fetchone()

        if address_exists:
            cursor.execute("""
                UPDATE addresses_buyer
                SET houseNo = %s, street = %s, barangay = %s, 
                    city = %s, Province = %s, postal_code = %s
                WHERE buyer_id = %s
            """, (houseNo, street, barangay, city, province, postal_code, buyer_id))
        else:
            cursor.execute("""
                INSERT INTO addresses_buyer 
                (houseNo, street, barangay, city, Province, postal_code, buyer_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (houseNo, street, barangay, city, province, postal_code, buyer_id))

        connection.commit()
        return jsonify({'success': True}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        cursor.close()
        connection.close()

@app.route('/buyer_dashboard/update_profile', methods=['POST'])
def update_profileMobile():
    connection = get_db_connection()
    cursor = connection.cursor()

    
    try:
        data = request.form
        buyer_id = data.get('buyer_id')

        if not buyer_id:
            return jsonify({'error': 'buyer_id is required'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        # Update buyers table (personal info)
        buyer_fields = ['Fname', 'Mname', 'Lname', 'email', 'mobile_number', 'birthdate']
        buyer_updates = []
        buyer_values = []
        
        for field in buyer_fields:
            value = data.get(field)
            if value is not None:
                buyer_updates.append(f"{field} = %s")
                buyer_values.append(value)

        if buyer_updates:
            buyer_sql = f"UPDATE buyers SET {', '.join(buyer_updates)} WHERE buyer_id = %s"
            cursor.execute(buyer_sql, buyer_values + [buyer_id])

        # Update address table
        address_fields = ['houseNo', 'street', 'barangay', 'city', 'Province', 'postal_code']
        address_updates = []
        address_values = []
        
        for field in address_fields:
            value = data.get(field)
            if value is not None:
                address_updates.append(f"{field} = %s")
                address_values.append(value)

        if address_updates:
            # Check if address exists first
            cursor.execute("SELECT 1 FROM addresses_buyer WHERE buyer_id = %s", (buyer_id,))
            address_exists = cursor.fetchone()
            
            if address_exists:
                address_sql = f"""
                    UPDATE addresses_buyer 
                    SET {', '.join(address_updates)} 
                    WHERE buyer_id = %s
                """
                cursor.execute(address_sql, address_values + [buyer_id])
            else:
                insert_sql = """
                    INSERT INTO addresses_buyer 
                    (houseNo, street, barangay, city, Province, postal_code, buyer_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, address_values + [buyer_id])

        connection.commit()
        return jsonify({'success': True, 'message': 'Profile updated'}), 200

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/get-buyer-address', methods=['POST'])
def get_buyer_address():
    buyer_id = request.form.get('buyer_id')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT b.Fname, b.Lname, a.houseNo, a.street, a.barangay, a.city, a.Province, a.postal_code
        FROM buyers b
        JOIN addresses_buyer a ON b.buyer_id = a.buyer_id
        WHERE b.buyer_id = %s
        LIMIT 1
    """, (buyer_id,))
    address = cur.fetchone()
    cur.close()
    conn.close()
    if address:
        return jsonify(address)
    else:
        return jsonify({}), 404

#147
@app.route('/rider_dashboardmobile', methods=['GET', 'POST'])
def rider_dashboardMobile():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    rider_id = request.args.get('rider_id')

    print(rider_id)
    if request.method == 'GET':
        # Optional: you can use rider_id to filter assigned orders if needed
        try:
            cursor.execute("""
           SELECT 
                orders.order_id, 
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname, 
                CONCAT(addresses_buyer.houseNo, ' ', addresses_buyer.street, ' ', 
                    addresses_buyer.barangay, ' ', addresses_buyer.city, ' ', 
                    addresses_buyer.Province) AS Fulladdress
            FROM orders
            JOIN buyers ON orders.buyer_id = buyers.buyer_id
            JOIN addresses_buyer ON buyers.buyer_id = addresses_buyer.buyer_id
            JOIN assignrider ON assignrider.order_id = orders.order_id
            WHERE assignrider.delivery_status = 'Assigned' AND assignrider.rider_id = %s
        """, (rider_id,))
            orders = cursor.fetchall()
            return jsonify(orders)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()

    elif request.method == 'POST':
        order_id = request.form.get('order_id')
        rider_id = request.form.get('rider_id')

        if not order_id or not rider_id:
            return jsonify({'error': 'Missing order_id or rider_id'}), 400

        try:
            cursor.execute("""
                UPDATE orders
                SET rider_id = %s, order_status = 'Assigned'
                WHERE order_id = %s AND rider_id IS NULL
            """, (rider_id, order_id))
            connection.commit()

            if cursor.rowcount == 0:
                return jsonify({'error': 'Order not found or already assigned'}), 404

            return jsonify({'message': 'Order assigned successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()

@app.route('/assign_delivery', methods=['POST'])
def assign_delivery():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        rider_id = request.form.get('rider_id')
        order_id = request.form.get('order_id')

        if not rider_id or not order_id:
            return jsonify({'error': 'Missing rider_id or order_id'}), 400

        # Insert into assignrider
        cursor.execute("""
            INSERT INTO assignrider (rider_id, order_id, delivery_status)
            VALUES (%s, %s, 'Assigned')
        """, (rider_id, order_id))

        # Update order status
        cursor.execute("""
            UPDATE orders SET order_status = 'Out For Delivery' WHERE order_id = %s
        """, (order_id,))

        connection.commit()
        return jsonify({'message': 'Delivery assigned and order status updated successfully'}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        connection.close()
@app.route('/ongoing_deliveries', methods=['GET'])
def ongoing_deliveries():
    rider_id = request.args.get('rider_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
           SELECT DISTINCT
                o.order_id, 
                CONCAT(b.Fname, ' ', b.Mname, ' ', b.Lname) AS fullname, 
                CONCAT(ab.houseNo, ' ', ab.street, ' ', ab.barangay, ' ', ab.city, ' ', ab.Province) AS Fulladdress,
                o.total_price,
                b.mobile_number
            FROM orders o
            JOIN buyers b ON o.buyer_id = b.buyer_id
            JOIN addresses_buyer ab ON b.buyer_id = ab.buyer_id
            JOIN assignrider ar ON o.order_id = ar.order_id
            WHERE o.order_status = 'Out For Delivery' 
            AND ar.rider_id = %s
        """, (rider_id,))
        return jsonify(cursor.fetchall())
    finally:
        cursor.close()
        connection.close()


@app.route('/rider-deliveredMobile', methods=['POST'])
def rider_deliveredMobile():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        order_id = request.form.get('order_id')
        rider_id = request.form.get('rider_id')  # Get from POST data, not session

        if not rider_id or not order_id:
            return jsonify({'error': 'Missing rider_id or order_id'}), 400

        # Update assignrider table
        cursor.execute("""
            UPDATE assignrider SET delivery_status = 'Completed' 
            WHERE rider_id = %s AND order_id = %s
        """, (rider_id, order_id))     

        # Update orders table
        # cursor.execute("""
        #     UPDATE orders SET order_status = 'Completed' WHERE order_id = %s
        # """, (order_id,))

        connection.commit()
        return jsonify({'message': 'Order successfully updated to completed!'}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/completed_deliveries', methods=['GET'])
def completed_deliveries():
    rider_id = request.args.get('rider_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
           SELECT 
                orders.order_id,
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname,
                CONCAT(addresses_buyer.houseNo, ' ', addresses_buyer.street, ' ', 
                    addresses_buyer.barangay, ' ', addresses_buyer.city, ' ', 
                    addresses_buyer.Province) AS full_address,
                MAX(orders.updated_at) AS date
            FROM orders
            JOIN buyers ON orders.buyer_id = buyers.buyer_id
            JOIN addresses_buyer ON buyers.buyer_id = addresses_buyer.buyer_id
            JOIN assignrider ON orders.order_id = assignrider.order_id
            WHERE orders.order_status = 'Completed' 
            AND assignrider.rider_id = %s
            GROUP BY orders.order_id
            ORDER BY date DESC;
        """, (rider_id,))
        return jsonify(cursor.fetchall())
    finally:
        cursor.close()
        connection.close()

@app.route('/rider_profile', methods=['GET'])
def rider_profile():
    rider_id = request.args.get('rider_id')
    if not rider_id:
        return jsonify({'error': 'Missing rider_id parameter'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                riders.rider_id,
                riders.Fname,
                riders.Lname,
                riders.mobile_number,
                riders.profile_pic,
                CONCAT(addresses_rider.houseNo, ' ', addresses_rider.street, ' ', 
                    addresses_rider.barangay, ' ', addresses_rider.city, ' ', 
                    addresses_rider.Province) AS address
            FROM riders
            JOIN addresses_rider ON riders.rider_id = addresses_rider.rider_id
            WHERE riders.rider_id = %s
        """, (rider_id,))
        rider_info = cursor.fetchone()
        if not rider_info:
            return jsonify({'error': 'Rider not found'}), 404
        return jsonify(rider_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/update_order_status_cancelled_userMobile', methods=['POST'])
def update_order_status_cancelled_userMobile():
    try:
        buyer_id = request.form.get('buyer_id')
        order_id = request.form.get('order_id')
        cancel_reason = request.form.get('reason')

        if not buyer_id or not order_id or not cancel_reason:
            return jsonify({
                'success': False,
                'message': 'Missing required data: buyer_id, order_id, or reason.'
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert notification for the seller
        insert_notification_query = """
            INSERT INTO notification_seller (buyer_id, cancel_reason, order_id)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_notification_query, (buyer_id, cancel_reason, order_id))

        # Update the order status to 'Cancelled'
        update_order_query = """
            UPDATE orders SET order_status = 'Cancelled' WHERE order_id = %s
        """
        cursor.execute(update_order_query, (order_id,))

        connection.commit()

        return jsonify({
            'success': True,
            'message': 'Order status updated to Cancelled and notification sent.'
        })

    except Exception as e:
        print(f"Unexpected error: {e}")
        if 'connection' in locals():
            connection.rollback()
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred.'
        }), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/buyer_dashboard/change_password', methods=['POST'])
def change_password():
    buyer_id = request.form.get('buyer_id')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    
    if not buyer_id or not old_password or not new_password:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get the user's password hash using a JOIN
        cursor.execute("""
            SELECT users.password, users.user_id
            FROM users
            JOIN buyers ON buyers.user_id = users.user_id
            WHERE buyers.buyer_id = %s
        """, (buyer_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': 'Buyer not found'}), 404

        # Validate old password
        if not check_password_hash(user['password'], old_password):
            return jsonify({'status': 'error', 'message': 'Current password is incorrect'}), 401

        # Update to new password hash
        new_password_hash = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_password_hash, user['user_id']))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Password changed successfully'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

@app.route('/api/request_reset_token', methods=['POST'])
def request_reset_token():
    email = request.form.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email required'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Retrieve user based on email
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            return jsonify({'status': 'error', 'message': 'Email not registered'}), 404

        # Create a token for password reset link
        token = s.dumps(email, salt='reset-password')
        reset_link = url_for('reset_password_page', token=token, _external=True)
        print(email)

        msg = Message(
            "Password Reset Request",
            recipients=[email],
            sender='ecohaven28@gmail.com'
            
        )
        msg.body = f"To reset your password, click the link below:\n\n{reset_link}"

        mail.send(msg)
        
        return jsonify({'status': 'success', 'message': 'Reset email sent'}), 200
        

    except Exception as e:
        app.logger.error(f"Error sending email: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to send email'}), 500


@app.route('/track_orderMobile/<int:order_id>', methods=['GET'])
def track_ordermobile(order_id):
    buyer_id_str = request.args.get('buyer_id')
    if not buyer_id_str:
        return jsonify({"error": "Missing buyer_id parameter"}), 400

    try:
        buyer_id = int(buyer_id_str)
    except ValueError:
        return jsonify({"error": "Invalid buyer_id parameter"}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch order details
        cursor.execute("""
            SELECT
                orders.order_id, 
                orders.created_at, 
                orders.total_price,
                orders.order_status,
                orders.quantity, 
                products.product_name, 
                products.image, 
                productvariations.color, 
                productvariations.size
            FROM orders
            JOIN products ON orders.product_id = products.Id
            JOIN productvariations ON orders.variation_id = productvariations.id
            WHERE orders.order_id = %s AND orders.buyer_id = %s;
        """, (order_id, buyer_id))
        
        order_details = cursor.fetchone()
        if not order_details:
            return jsonify({"error": "Order not found"}), 404

        # Fetch delivery status
        cursor.execute("""
            SELECT delivery_status
            FROM assignrider
            WHERE order_id = %s
                       LIMIT 1;;
        """, (order_id,))
        delivery_result = cursor.fetchone()
        delivery_status = delivery_result['delivery_status'] if delivery_result else None

        # Add delivery_status to order_details
        order_details['delivery_status'] = delivery_status

        print(order_details)

        return jsonify(order_details), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()

#159
@app.route('/api/markOrderCompleted', methods=['POST'])
def update_order_statusMobile():
    order_id = request.form.get('order_id')
    
    if not order_id:
        return jsonify({'success': False, 'message': 'Missing order_id parameter'}), 400

    print(f"Debug: Received order_id for update: {order_id}")
    
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE orders SET order_status = 'Completed' WHERE order_id = %s",
            (order_id,)
        )
        connection.commit()
    except Exception as e:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'success': False, 'message': f'Error updating order: {str(e)}'}), 500

    cursor.close()
    connection.close()
    
    return jsonify({'success': True, 'message': f'Order {order_id} marked as Completed.'}), 200

@app.route('/submit-ratingmobile', methods=['POST'])
def submit_ratingmobile():
    order_id = request.form.get('order_id')
    rating = request.form.get('rating')
    description = request.form.get('description')
    buyer_id = request.form.get('buyer_id')  # ✅ Grab buyer_id

    print(f"Received rating submission: order_id={order_id}, rating={rating}, description={description}, buyer_id={buyer_id}")

    if not order_id or not rating or not buyer_id:
        return jsonify({'success': False, 'message': 'Order ID, rating, and buyer ID are required.'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT product_id FROM orders WHERE order_id = %s", (order_id,))
        product = cursor.fetchone()
        if not product:
            raise ValueError("Order ID not found.")
        product_id = product['product_id']

        image3 = request.files.get('picture')
        image = None
        if image3 and allowed_file(image3.filename):
            image = secure_filename(image3.filename)
            image3.save(os.path.join(app.config['UPLOAD_FOLDER'], image))

        query = """INSERT INTO rating (product_id, rate, description, product_pic, buyer_id)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (product_id, rating, description, image, buyer_id))
        connection.commit()

        print("Rating successfully submitted.")
        print(image)
        return jsonify({'success': True, 'message': 'Rating successfully submitted.'}), 200

    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Database error: {err}")
        return jsonify({'success': False, 'message': 'Database error occurred.'}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        cursor.close() 
        connection.close()

@app.route('/product-reviews/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT rating.*, 
                   CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS Fullname
            FROM rating 
            JOIN buyers ON buyers.buyer_id = rating.buyer_id
            WHERE product_id = %s
            ORDER BY rating.rating_id DESC
        """, (product_id,))
        reviews = cursor.fetchall()
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# @app.route('/api/products')
# def get_products():
#     try:
#         # Use db_config to create the connection
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor(dictionary=True)

#         cursor.execute("""
#             SELECT id, Product_Name, Description, Price, Stock_Quantity, Status, Seller_Id, Image, category
#             FROM products
#         """)
#         products = cursor.fetchall()

#         products_list = []
#         for product in products:
#             products_list.append({
#                 'id': product['id'],
#                 'Product_Name': product['Product_Name'],
#                 'Description': product['Description'],
#                 'Price': product['Price'],
#                 'Stock_Quantity': product['Stock_Quantity'],
#                 'Status': product['Status'],
#                 'Seller_Id': product['Seller_Id'],
#                 'Image': product['Image'],
#                 'category': product['category'],
#                 'total_sold': 0,  # This should be updated with the total sold logic if needed
#                 'rating': 0,      # This should be updated with the average rating logic if needed
#             })

#         return jsonify({'products': products_list})

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         # Ensure cursor and connection are closed properly
#         if cursor:
#             cursor.close()
#         if connection:
#             connection.close()



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)





UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}


#for image
@app.template_filter('b64encode')
def b64encode_filter(data):
    """Encode binary data to base64 for use in templates."""
    if data:
        return base64.b64encode(data).decode('utf-8')  
    return ""
def get_default_profile_pic():
    with open('static/uploads/profile-icon-design-free-vector.jpg', 'rb') as file:
        binary_data = file.read()
    return binary_data

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    return mysql.connector.connect(**db_config)



# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ecohaven28@gmail.com' 
app.config['MAIL_PASSWORD'] = 'xkzc bypv ggyu yjdz'  
mail = Mail(app)

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Retrieve user based on email
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            # Check if the user is approved
            if user['approval'] == 0:
                return redirect(url_for('login', error="Your account is not approved yet"))
            if user['active'] == 'DEACTIVE':
                return redirect(url_for('login', error="Your account is has banned"))
            
            # Verify hashed password
            if check_password_hash(user['password'], password):
                session['id'] = user['user_id']
                session['role'] = user['role_id']

                # Role-based redirection
                if session['role'] == 1:
                    return redirect(url_for('buyer_dashboard'))
                elif session['role'] == 2:
                    return redirect(url_for('seller_dashboard'))
                elif session['role'] == 3:
                    return redirect(url_for('admin_dashboard'))
                elif session['role'] == 4:
                    return redirect(url_for('rider_dashboard'))
            else:
                # Invalid password
                return redirect(url_for('login', error="Invalid email or password"))
        else:
            # User not found
            return redirect(url_for('login', error="User not found"))
    
    # Render login page if GET request
    return render_template('Login-page/LoginPage.html', error=request.args.get('error'))

@app.route('/admin_dashboard')
def admin_dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT * FROM users
        WHERE users.role_id = 1 AND users.approval = 1""")
        buyers = cursor.fetchall()


        cursor.execute("""SELECT * FROM users
        WHERE users.role_id = 2 AND users.approval = 1""")
        sellers = cursor.fetchall()
        cursor.execute("""
            SELECT 
                ROUND(SUM(o.total_price), 2) AS totalprice,
                ROUND(SUM(o.total_price) * 0.05, 2) AS total_price_5_percent
            FROM orders o
            
            WHERE o.order_status = 'Completed'
        """)
        commission_data = cursor.fetchone()  # Single row result

        total_commission = commission_data['total_price_5_percent'] or 0
    finally:
        cursor.close()
        connection.close()


    buyersregister = len(buyers)
    sellersregister = len(sellers)


    return render_template('admin-page/dashboard.html', sellersregister = sellersregister , buyersregister = buyersregister
                           , total_commission=total_commission)

    
#===========================================================acccount management========================================================================
@app.route('/admin_dashboard/account-management',methods=['GET', 'POST'])
def admin_account_management():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT *
            FROM users
            JOIN sellers ON sellers.user_id = users.user_id
            WHERE users.approval = 1 AND users.active = 'ACTIVE';
        """)
        users_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template('admin-page/account-management/account-management.html', users_data=users_data)
#1234
@app.route('/block-user-seller-form/<int:user_id>', methods=['GET'])
def block_user_form(user_id):
    print(user_id)
    return render_template('admin-page/account-management/block-notif.html', user_id=user_id)
#dective_seller
@app.route('/block-user-seller/<int:user_id>', methods=['POST'])
def block_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for more readable results
    block_reason = request.form.get('block_reason')

    try:
        # Fetch user full name
        cursor.execute(
            """
                    SELECT 
                CASE 
                    WHEN b.user_id IS NOT NULL THEN CONCAT(b.Lname, ' ', b.Fname, ' ', COALESCE(b.Mname, ''))
                    WHEN s.user_id IS NOT NULL THEN CONCAT(s.Lname, ' ', s.Fname, ' ', COALESCE(s.Mname, ''))
                END AS FullName
            FROM users 
            LEFT JOIN buyers b ON b.user_id = users.user_id
            LEFT JOIN sellers s ON s.user_id = users.user_id
            WHERE users.user_id = %s
            """, 
            (user_id,)
        )
        fullname_result = cursor.fetchone()
        if not fullname_result:
            print("User not found.")
            return redirect(url_for('admin_account_management', error="User not found."))

        fullname = fullname_result['FullName']

        # Fetch recipient email
        cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
        email_result = cursor.fetchone()
        if not email_result:
            print("Email not found.")
            return redirect(url_for('admin_account_management', error="Email not found."))

        recipient_email = email_result['email']

        # Update user status to DEACTIVE
        cursor.execute("UPDATE users SET active = 'DEACTIVE' WHERE user_id = %s", (user_id,))
        connection.commit()

        # Prepare email message
        emailmessage = f"""Dear {fullname},

We regret to inform you that your EcoHaven account has been banned due to the following reason(s):

[{block_reason}]

This decision was made after a careful review to ensure the safety and integrity of our platform. If you believe this action was taken in error or would like to appeal, please contact our support team for assistance.

We appreciate your understanding in this matter and remain committed to maintaining a secure and trusted platform for all users.

Sincerely,
The EcoHaven Team
"""

        # Send email notification
        msg = Message(
            subject="Important Notice: Your EcoHaven Account Has Been Banned",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        msg.body = emailmessage
        mail.send(msg)

        print(f"User {user_id} has been blocked and notified.")
    except Exception as e:
        print(f"Failed to block user: {str(e)}")
        return redirect(url_for('admin_account_management', error=f"Failed to block user: {str(e)}"))
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_account_management', error="User has been blocked and notified."))



#===============================================================================


@app.route('/account-management/registered-buyer',methods=['GET', 'POST'])
def admin_management_registered_buyer():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
           SELECT *, CONCAT(buyers.Fname, ', ', buyers.Mname, ', ', buyers.Lname) AS fullname
                        FROM `users`
                        JOIN buyers ON buyers.user_id = users.user_id
                        WHERE `users`.`approval` = 1 AND users.active = 'ACTIVE';
        """)
        users_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template('admin-page/account-management/registered-buyer.html', users_data=users_data)

#123
@app.route('/block_user-form/<int:user_id>', methods=['GET'])
def block_user_buyer_form(user_id):
    print(user_id)
    return render_template('admin-page/account-management/block-notif.html', user_id=user_id)

#===================================================approvalbuyer=======================================================================

@app.route('/account-management/requestAcc-buyer')
def admin_management_requestAcc_buyer():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
           SELECT *, CONCAT(buyers.Fname, ', ', buyers.Mname, ', ', buyers.Lname) AS fullname
                        FROM `users`
                        JOIN buyers ON buyers.user_id = users.user_id
                        WHERE `users`.`approval` = 0 AND users.active = "ACTIVE";
        """)
        users_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template ('admin-page/account-management/buyer-approval.html', users_data=users_data )



@app.route('/account-management/detailsAcc-buyer/<int:user_id>')
def admin_management_detailsAcc_buyer(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT *,
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname
            FROM users
            JOIN buyers ON buyers.user_id = users.user_id
            JOIN addresses_buyer ON addresses_buyer.buyer_id = buyers.buyer_id 
            WHERE users.approval = 0 
            AND users.user_id = %s;
        """, (user_id,))
        
        users_data = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching user details: {e}")
        users_data = []  # Return empty data on error

    finally:
        cursor.close()
        connection.close()

    return render_template('admin-page/account-management/buyer-approval-details.html', users_data=users_data)



@app.route('/approve_user/<int:user_id>', methods=['POST'])
def approve_user_buyer(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch the user's full name
        cursor.execute(
            """
            SELECT 
                CASE 
                    WHEN b.user_id IS NOT NULL THEN CONCAT(b.Lname, ' ', b.Fname, ' ', COALESCE(b.Mname, ''))
                    WHEN s.user_id IS NOT NULL THEN CONCAT(s.Lname, ' ', s.Fname, ' ', COALESCE(s.Mname, ''))
                END AS FullName
            FROM users 
            LEFT JOIN buyers b ON b.user_id = users.user_id
            LEFT JOIN sellers s ON s.user_id = users.user_id
            WHERE users.user_id = %s
            """,
            (user_id,)
        )
        fullname_result = cursor.fetchone()
        fullname = fullname_result['FullName'] if fullname_result and fullname_result['FullName'] else None

        if not fullname:
            print("User not found.")
            return redirect(url_for('admin_blocked_list_buyers', error="User not found."))

        # Fetch recipient email from the form
        recipient_email = request.form.get('email')
        if not recipient_email:
            print("Recipient email not provided.")
            return redirect(url_for('admin_management_requestAcc_buyer', error="Recipient email not provided."))

        # Update user approval status
        cursor.execute("UPDATE users SET approval = 1 WHERE user_id = %s", (user_id,))
        connection.commit()

        # Prepare the email content
        message_content = f"""Dear {fullname},

We are delighted to inform you that your EcoHaven account has been successfully approved. 
You now have full access to our platform, where you can discover and enjoy a wide range of home and garden products.

If you have any questions or require assistance as you navigate the platform, please feel free to reach out to our support team.

Welcome to EcoHaven, and thank you for being part of our community.

Sincerely,
The EcoHaven Team"""

        # Send the approval email
        msg = Message(
            subject="Congratulations! Your EcoHaven Account Has Been Approved",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        msg.body = message_content
        mail.send(msg)
        print(f"Approval email sent to {recipient_email}")

    except Exception as e:
        connection.rollback()  # Rollback in case of any failure
        print(f"An error occurred: {e}")
        return redirect(url_for('admin_management_requestAcc_buyer', error="An error occurred during approval."))

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_management_requestAcc_buyer', success="User approved successfully."))



@app.route('/reject_user/<int:user_id>', methods=['POST'])
def reject_user_buyer(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()


    try:
        if request.method == 'POST':
            recipient_email = request.form['email']
            message_content = "Your account has not  approved for fake identity."

            cursor.execute("UPDATE users SET active = 'DEACTIVE' WHERE user_id = %s", (user_id,))
            connection.commit()
            msg = Message(
                subject="Email from Flask",
                sender=app.config['MAIL_USERNAME'],
                recipients=[recipient_email]
            )
            msg.body = message_content
            mail.send(msg)
            
       
    except Exception as e:
        print(e)
        
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_management_requestAcc_buyer' ))

#================================================================================================================

@app.route('/account-management/requestAcc-seller')
def admin_management_requestAcc_seller():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
           SELECT *, CONCAT(sellers.Fname, ', ', sellers.Mname, ', ', sellers.Lname) AS fullname
                        FROM `users`
                        JOIN sellers ON sellers.user_id = users.user_id
                        WHERE `users`.`approval` = 0 AND `users`.`active` = 'ACTIVE';
        """)
        users_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template ('admin-page/account-management/seller-approval.html', users_data=users_data )


@app.route('/account-management/detailsAcc-seller/<int:user_id>')
def admin_management_detailsAcc_seller(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
                SELECT *, 
                CONCAT(sellers.Fname, ', ', sellers.Mname, ', ', sellers.Lname) AS fullname
            FROM `users`
            JOIN sellers ON sellers.user_id = users.user_id
            JOIN addresses_seller ON addresses_seller.seller_id = sellers.seller_id 
            WHERE `users`.`approval` = 0 
            AND users.user_id = %s;
        """, (user_id,))
        users_data = cursor.fetchall()     
    finally:
        cursor.close()
        connection.close()
    return render_template('admin-page/account-management/seller-approval-details.html', users_data=users_data)

@app.route('/approve-user-seller/<int:user_id>', methods=['POST'])
def approve_user_seller(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Fetch full name of the user
        cursor.execute(
            """
            SELECT 
                CASE 
                    WHEN b.user_id IS NOT NULL THEN CONCAT(b.Lname, ' ', b.Fname, ' ', COALESCE(b.Mname, ''))
                    WHEN s.user_id IS NOT NULL THEN CONCAT(s.Lname, ' ', s.Fname, ' ', COALESCE(s.Mname, ''))
                END AS FullName
            FROM users 
            LEFT JOIN buyers b ON b.user_id = users.user_id
            LEFT JOIN sellers s ON s.user_id = users.user_id
            WHERE users.user_id = %s
            """,
            (user_id,)
        )
        fullname_result = cursor.fetchone()
        if not fullname_result or not fullname_result['FullName']:
            print("User not found.")
            return redirect(url_for('admin_blocked_list_buyers', error="User not found."))
        
        fullname = fullname_result['FullName']
        
        # Fetch recipient email from the database
        cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
        email_result = cursor.fetchone()
        recipient_email = email_result['email'] if email_result else None

        if not recipient_email:
            print("Recipient email not found.")
            return redirect(url_for('admin_management_requestAcc_seller', error="Recipient email not found."))

        # Prepare and send the email
        message_content = f"""Dear {fullname},

We are delighted to inform you that your EcoHaven account has been successfully approved. 
You now have full access to our platform, where you can discover and enjoy a wide range of home and garden products.

If you have any questions or require assistance as you navigate the platform, please feel free to reach out to our support team.

Welcome to EcoHaven, and thank you for being part of our community.

Sincerely,
The EcoHaven Team"""
        
        # Update approval status
        cursor.execute("UPDATE users SET approval = 1 WHERE user_id = %s", (user_id,))
        connection.commit()

        # Send the email
        msg = Message(
            subject="Congratulations! Your EcoHaven Account Has Been Approved",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        msg.body = message_content
        mail.send(msg)
        print(f"Email successfully sent to {recipient_email}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_management_requestAcc_seller',error = "notif successful"))


#================================================================


@app.route('/rejection-seller-form/<int:user_id>', methods=['GET'])
def reject_user_form(user_id):
    print(user_id)
    return render_template('admin-page/account-management/reject-notif.html', user_id=user_id)

@app.route('/reject-user-seller/<int:user_id>', methods=['POST'])
def reject_user_seller(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    reject_reason = request.form.get('reject_reason')
    
    if not reject_reason:
        print("Rejection reason not provided.")
        return redirect(url_for('admin_management_requestAcc_seller', error="Rejection reason not provided."))

    try:
        # Fetch recipient email
        cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
        email_result = cursor.fetchone()
        recipient_email = email_result['email'] if email_result else None

        if not recipient_email:
            print('User not found.')
            return redirect(url_for('admin_account_management', error="User not found."))

        # Fetch full name
        cursor.execute(
            """
            SELECT 
                CASE 
                    WHEN b.user_id IS NOT NULL THEN CONCAT(b.Lname, ' ', b.Fname, ' ', COALESCE(b.Mname, ''))
                    WHEN s.user_id IS NOT NULL THEN CONCAT(s.Lname, ' ', s.Fname, ' ', COALESCE(s.Mname, ''))
                END AS FullName
            FROM users 
            LEFT JOIN buyers b ON b.user_id = users.user_id
            LEFT JOIN sellers s ON s.user_id = users.user_id
            WHERE users.user_id = %s
            """,
            (user_id,)
        )
        fullname_result = cursor.fetchone()
        fullname = fullname_result['FullName'] if fullname_result and fullname_result['FullName'] else "User"

        # Prepare rejection email content
        message_content = f"""Dear {fullname},

Thank you for applying to join the EcoHaven community. After a thorough review, we regret to inform you that your registration has not been approved for the following reason(s):

{reject_reason}

If you believe this decision was made in error or wish to address the mentioned issue(s), please contact our support team at your earliest convenience.

We value your interest in EcoHaven and encourage you to reapply once the concerns are resolved.

Sincerely,
The EcoHaven Team"""

        # Update user status to 'DEACTIVE'
        cursor.execute("UPDATE users SET active = 'DEACTIVE' WHERE user_id = %s", (user_id,))
        connection.commit()

        # Send rejection email
        msg = Message(
            subject="Update on Your EcoHaven Account Registration",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        msg.body = message_content
        mail.send(msg)
        print(f"Email sent to {recipient_email} with reason: {reject_reason}")

    except Exception as e:
        connection.rollback()  # Rollback on error
        print(f"Error: {e}")
        return redirect(url_for('admin_account_management', error="An error occurred while processing the rejection."))

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_management_requestAcc_seller', error="Rejection completed successfully."))


#==============================================================================================================================

@app.route('/account-management/archived')
def admin_management_archived():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
            users.*, 
            CONCAT (sellers.Fname,'',sellers.Mname,'',sellers.Fname ) AS sellerfullname,
            sellers.shop_logo AS seller_logo,
            CONCAT(buyers.Fname,'',buyers.Mname,'',buyers.Lname) AS buyerfullname,
            buyers.profile_pic
        FROM 
            users
        LEFT JOIN 
            sellers ON sellers.user_id = users.user_id
        LEFT JOIN 
            buyers ON buyers.user_id = users.user_id
        WHERE 
            users.active = 'DEACTIVE' AND users.approval = 0;


        """)
        users_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template('admin-page/account-management/archieved.html', users_data=users_data)

@app.route('/approve_user/unblock/<int:user_id>', methods=['POST'])
def approve_user_unblock(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
   

    try:
        cursor.execute("UPDATE users SET active = 'ACTIVE' WHERE user_id = %s", (user_id,))
        connection.commit()
        
    except Exception as e:
        print(e)
        
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_management_archived'))

@app.route('/reject_user/delete/<int:user_id>', methods=['POST'])
def approve_user_delete(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()


    try:
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        connection.commit()
       
    except Exception as e:
        print(e)
        
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_management_archived' ))



#===============================================================================================================================================
#156
@app.route('/admin_dashboard/blocked-list')
def admin_blocked_list():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                users.*, 
                sellers.shop_name AS seller_fname, 
                sellers.shop_logo AS seller_logo
            FROM 
                users
            JOIN 
                sellers ON sellers.user_id = users.user_id
            WHERE 
                users.active = 'DEACTIVE' AND users.approval = 1;
        """)
        users_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template('admin-page/blocked-list/blocked-list.html', users_data=users_data)
#256
@app.route('/block_user/unblock/<int:user_id>', methods=['POST'])
def blocke_user_unblock(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for better readability

    try:
        # Fetch user full name
        cursor.execute(
            """
           SELECT 
                CASE 
                    WHEN b.user_id IS NOT NULL THEN CONCAT(b.Lname, ' ', b.Fname, ' ', COALESCE(b.Mname, ''))
                    WHEN s.user_id IS NOT NULL THEN CONCAT(s.Lname, ' ', s.Fname, ' ', COALESCE(s.Mname, ''))
                END AS FullName
            FROM users 
            LEFT JOIN buyers b ON b.user_id = users.user_id
            LEFT JOIN sellers s ON s.user_id = users.user_id
            WHERE users.user_id = %s
            """,
            (user_id,)
        )
        fullname_result = cursor.fetchone()
        if not fullname_result:
            print("User not found.")
            return redirect(url_for('admin_blocked_list_buyers', error="User not found."))

        fullname = fullname_result['FullName']

        # Fetch recipient email
        cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
        email_result = cursor.fetchone()
        if not email_result:
            print("Email not found.")
            return redirect(url_for('admin_blocked_list_buyers', error="Email not found."))

        recipient_email = email_result['email']
        print(f"Debug: Recipient email - {recipient_email}")

        # Update user status to ACTIVE
        cursor.execute("UPDATE users SET active = 'ACTIVE' WHERE user_id = %s", (user_id,))
        connection.commit()

        # Prepare and send email
        msg = Message(
            subject="Account Reinstated - Welcome Back!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        msg.body = f"""
Dear {fullname},

We are pleased to inform you that the ban on your EcoHaven account has been lifted. You now have full access to your account and all features of our platform.

We encourage you to review our platform’s terms and policies to ensure a smooth and compliant experience moving forward. Should you have any questions or concerns, please do not hesitate to contact our support team.

Thank you for your cooperation and continued engagement with EcoHaven.

Sincerely,
The EcoHaven Team
"""
        mail.send(msg)
        print("Debug: Email sent successfully.")
    except Exception as e:
        print(f"Error: {str(e)}")
        return redirect(url_for('admin_blocked_list_buyers', error=f"An error occurred: {str(e)}"))
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('admin_blocked_list_buyers', error="User unblocked and notified successfully."))

#356
@app.route('/admin_dashboard/blocked-list_buyers')
def admin_blocked_list_buyers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
           SELECT 
                users.*, 
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS seller_fname,
                buyers.profile_pic
            FROM 
                users
            JOIN 
                buyers ON buyers.user_id = users.user_id
            WHERE 
                users.active = 'DEACTIVE' 
                AND users.approval = 1;
        """)
        users_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template('admin-page/blocked-list/buyer-blocked-list.html', users_data=users_data)

@app.route('/block_user/unblock-buyer/<int:user_id>', methods=['POST'])
def blocke_user_unblock_buyers(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for better readability

    try:
        # Fetch user full name
        cursor.execute(
            """
           SELECT 
                CASE 
                    WHEN b.user_id IS NOT NULL THEN CONCAT(b.Lname, ' ', b.Fname, ' ', COALESCE(b.Mname, ''))
                    WHEN s.user_id IS NOT NULL THEN CONCAT(s.Lname, ' ', s.Fname, ' ', COALESCE(s.Mname, ''))
                END AS FullName
            FROM users 
            LEFT JOIN buyers b ON b.user_id = users.user_id
            LEFT JOIN sellers s ON s.user_id = users.user_id
            WHERE users.user_id = %s
            """,
            (user_id,)
        )
        fullname_result = cursor.fetchone()
        if not fullname_result:
            print("User not found.")
            return redirect(url_for('admin_blocked_list_buyers', error="User not found."))

        fullname = fullname_result['FullName']

        # Fetch recipient email
        cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
        email_result = cursor.fetchone()
        if not email_result:
            print("Email not found.")
            return redirect(url_for('admin_blocked_list_buyers', error="Email not found."))

        recipient_email = email_result['email']
        print(f"Debug: Recipient email - {recipient_email}")

        # Update user status to ACTIVE
        cursor.execute("UPDATE users SET active = 'ACTIVE' WHERE user_id = %s", (user_id,))
        connection.commit()

        # Prepare and send email
        msg = Message(
            subject="Account Reinstated - Welcome Back!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        msg.body = f"""
Dear {fullname},

We are pleased to inform you that the ban on your EcoHaven account has been lifted. You now have full access to your account and all features of our platform.

We encourage you to review our platform’s terms and policies to ensure a smooth and compliant experience moving forward. Should you have any questions or concerns, please do not hesitate to contact our support team.

Thank you for your cooperation and continued engagement with EcoHaven.

Sincerely,
The EcoHaven Team
"""
        mail.send(msg)
        print("Debug: Email sent successfully.")
    except Exception as e:
        print(f"Error: {str(e)}")
        return redirect(url_for('admin_blocked_list_buyers', error=f"An error occurred: {str(e)}"))
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_blocked_list_buyers', error="User unblocked and notified successfully."))



#=======================================================================================================================

@app.route('/admin_dashboard/report')
def admin_report():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT *
            FROM 
                report_sellerproduct
            JOIN 
                sellers ON sellers.seller_id = report_sellerproduct.seller_id
        """)
        reports = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()


    return render_template('admin-page/report/report.html',reports =reports)

@app.route('/admin_dashboard/report/<int:report_id>', methods=['GET'])
def reportdetails(report_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch the specific report based on report_id
        cursor.execute("""
            SELECT report_sellerproduct.*, CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS Fullname
            FROM report_sellerproduct
            JOIN buyers ON buyers.buyer_id = report_sellerproduct.buyer_id
            WHERE report_sellerproduct.id = %s;
        """, (report_id,))
        
        report = cursor.fetchone()  # Fetch a single report
        
  

    finally:
        cursor.close()
        connection.close()

    return render_template("admin-page/report/details.html", report=report)


@app.route('/admin_dashboard/reported-buyers')
def admin_report_buyers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT *,CONCAT(buyers.Fname,'',buyers.Mname,'',buyers.Lname) AS fullname
            FROM 
                buyers_reported
            JOIN 
                buyers ON buyers.buyer_id = buyers_reported.buyer_id;
        """)
        reports = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()
    return render_template('admin-page/report/reported-buyers.html',reports =reports)



@app.route('/admin_dashboard/reported-buyer/<int:report_id>', methods=['GET'])
def reporteddetails_buyer(report_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch the specific report based on report_id
        cursor.execute("""
            SELECT buyers_reported.*, CONCAT(sellers.Fname, ' ', sellers.Mname, ' ', sellers.Lname) AS Fullname
            FROM buyers_reported
            JOIN sellers ON sellers.seller_id = buyers_reported.seller_id
            WHERE buyers_reported.id  = %s;
        """, (report_id,))
        
        report = cursor.fetchone()  # Fetch a single report
        
  

    finally:
        cursor.close()
        connection.close()

    return render_template("admin-page/report/details-reported-buyer.html", report=report)





#banner
@app.route('/upload-banner', methods=['POST'])
def upload_banner():
    connection = get_db_connection()
    cursor = connection.cursor()  # Remove `dictionary=True` unless necessary
    image = request.files.get('bannerFile')

    if not image or not allowed_file(image.filename):
        print("Invalid or no file selected.")
        return redirect(url_for('admin_dashboard', error="Invalid file type or no file selected."))

    try:
        # Ensure unique filename
        image_filename = secure_filename(image.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        counter = 1
        while os.path.exists(save_path):  # Avoid overwriting files
            name, ext = os.path.splitext(image_filename)
            image_filename = f"{name}_{counter}{ext}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            counter += 1

        image.save(save_path)  # Save the uploaded file

        # Insert into database
        query = "INSERT INTO baner (banner_filename) VALUES (%s)"
        cursor.execute(query, (image_filename,))
        connection.commit()
        print("Banner successfully inserted into the database.")

    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")
        return redirect(url_for('admin_dashboard', error="Failed to upload banner."))

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_dashboard', success="Banner uploaded successfully."))








# =======================================================================================================================================================
# All register
@app.route('/register', methods=['POST'])
def register():
    # Get form data
    email = request.form['email'] #username
    password = request.form['password']
    user_type = int(request.form['user_type'])

    try:
        if user_type == 1:
            return redirect(url_for('createBuyerForm',provided_email=email, provided_password=password))
        elif user_type == 2:
            return redirect(url_for('createSellerForm', provided_email=email, provided_password=password))

    except Exception as err:
        return redirect(url_for('signup', error=f"Error: {err}"))

# Buyer
def buyerinfo():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM addresses_buyer
            JOIN buyers ON addresses_buyer.buyer_id = buyers.buyer_id
            WHERE buyers.user_id = %s;
        """, (session['id'],))
        
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['user_id']
            Fname = user['Fname']
            Mname = user['Mname']
            Lname = user['Lname']
            houseNo = user['houseNo']
            street = user['street']
            barangay = user['barangay']
            city = user['city']
            Province = user['Province']
            postal_code = user['postal_code']
            email = user['email']
            contact_num = user['mobile_number']
            description = user.get('description', '')  # Use .get() in case 'description' is not present
        else:
            # Set defaults if no user data is found
            Fname = ''
            Mname = ''
            Lname = ''
            houseNo = ''
            street = ''
            barangay = ''
            city = ''
            Province = ''
            postal_code = ''
            email = ''
            contact_num = ''
            description = ''

    finally:
        cursor.close()
        connection.close()
    
    return Fname, Mname, Lname, email, contact_num, houseNo, street, barangay, city, Province, postal_code, description




def product_description(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
        SELECT
            products.Id,
            products.Product_Name,
            products.Description,
            products.Price,
            products.Image,
            sellers.seller_id,
            sellers.shop_name,
            sellers.profile_pic,
            sellers.shop_logo         
        FROM products
        JOIN sellers ON products.seller_id = sellers.seller_id
        WHERE products.Id = %s
        """, (product_id,))
        
        product = cursor.fetchone()
        if product:
            seller_id = product['seller_id']
            product_name = product['Product_Name']
            description = product['Description']
            price = product['Price']
            product_pic = product['Image']
            sellerpic= product['profile_pic']
            sellershopname= product ['shop_name']
            product_id = product['Id']
            seller_logo= product['shop_logo']
            


        else:
            product_id,product_name, description, price, product_pic,sellerpic,sellershopname,seller_id = None, None, None, None,None,None,None, None
    finally:
        cursor.close()
        connection.close()
    
    return seller_logo , product_name, description, price, product_pic, sellerpic, sellershopname, product_id

@app.route('/buyer_dashboard/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity',1))  
    buyer_id = session.get('buyer_id')  
    description = request.form.get('description')
    productName = request.form.get('productName')
    color = request.form.get('selected_color')
    size = request.form.get('selected_size')
    shop_name = request.form.get('shop_name')
    price = float(request.form.get('price', 0)) 
    product_image = request.form['product_image']
    buying = request.form.get('buying')
    print("quantity",quantity)
    print("color",color)
    print("size",size)
    
    

    
    # Ensure all fields are filled
    if not all([product_id, buyer_id, productName, description, price]):
        flash("Missing required fields.")
        return redirect(url_for('productOverview', product_id=product_id))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary cursor

       # Determine the SQL query based on the values of size and color
    cursor.execute("SELECT COUNT(*) AS variation_count FROM productvariations WHERE product_id = %s", (product_id,))
    has_variations = cursor.fetchone()['variation_count'] > 0

    # Attempt to find the correct variation if variations exist
    variation_data = None
    if has_variations:
        if color and size:  # Both color and size provided
            cursor.execute("SELECT id FROM productvariations WHERE color = %s AND size = %s AND product_id = %s", (color, size, product_id))
        elif color:  # Only color provided
            cursor.execute("SELECT id FROM productvariations WHERE color = %s AND size IS NULL AND product_id = %s", (color, product_id))
        elif size:  # Only size provided
            cursor.execute("SELECT id FROM productvariations WHERE size = %s AND color IS NULL AND product_id = %s", (size, product_id))
        
        variation_data = cursor.fetchone()

    # Redirect with an error if variations are required but none selected
    if has_variations and variation_data is None:
        return redirect(url_for('productOverview', product_id=product_id, error="THE variety is not available."))
    
    variation_id = variation_data['id'] if variation_data else 0


  # Get the variation ID
    #print("variation",variation_id)

    try:
        # Check if the item is already in the cart
        cursor.execute("SELECT * FROM cart_items WHERE buyer_id = %s AND product_id = %s AND variation_id = %s", (buyer_id, product_id,variation_id))
        existing_item = cursor.fetchone()

        if existing_item:
            # If existing_item is a tuple, this will raise an error
           new_quantity = existing_item['quantity'] + quantity  # Access as a dictionary
           cursor.execute("""
                UPDATE cart_items 
                SET quantity = %s
                WHERE id = %s
            """, (new_quantity, existing_item['id']))
        else:
            # Insert new item into the cart
            total_price = price * quantity
            cursor.execute("""
                INSERT INTO cart_items (buyer_id, product_id, quantity, product_name, price, Description, shop_name, product_image, variation_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (buyer_id, product_id, quantity, productName, price, description, shop_name, product_image, variation_id ))
            flash(f"{productName} added to your cart.")
    
        connection.commit()

    except Exception as e:
        connection.rollback()
        flash(f"An error occurred: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('productOverview', product_id=product_id, error=f'{productName} added to your cart.'))
#============================================================searchbuyer========================================================


@app.route('/search' )
def search():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = buyerid()
    search = request.args.get('search', '').strip()
    #print("ni search",search)

    if not search:  
        return redirect(url_for('buyer_dashboard'))  # Replace 'homepage' with your actual homepage route

    cursor.execute("SELECT * FROM products WHERE Product_Name LIKE %s", ('%' + search + '%',))
    products = cursor.fetchall()
    for product in products:
                product_id = product['Id']

                # Calculate total sold quantity
                cursor.execute("""
                    SELECT SUM(orders.quantity) AS total_sold
                    FROM orders
                    WHERE orders.order_status = 'Completed'
                    AND orders.product_id = %s;
                """, (product_id,))
                sold = cursor.fetchone()
                product['total_sold'] = sold['total_sold'] if sold and sold['total_sold'] else 0

                # Calculate average rating
                cursor.execute("""
                    SELECT ROUND(AVG(rate), 1) AS average_rate
                    FROM rating
                    WHERE product_id = %s;
                """, (product_id,))
                rate = cursor.fetchone()
                product['Rating'] = rate['average_rate'] if rate and rate['average_rate'] else 0


    return render_template('Home-page/product-search.html', products=products , username= username, profile_pic = profile_pic, search=search)


#====================================================================================================================================
###
@app.route('/category')
def category():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = buyerid()
    pagelimit = 30

    # Get the current page number from the query string (default to 1)
    page = request.args.get('page', default=1, type=int)
    offset = (page - 1) * pagelimit  # Calculate the offset

    # Get category from the query parameters
    category = request.args.get('category')
    if not category:
        return redirect(url_for('buyer_dashboard'))

    # Fetch total product count for pagination
    cursor.execute("SELECT COUNT(*) AS total FROM products WHERE category = %s", (category,))
    total_products = cursor.fetchone()['total']
    total_pages = (total_products + pagelimit - 1) // pagelimit

    # Fetch products for the current page
    cursor.execute("""
        SELECT * FROM products 
        WHERE category = %s
        LIMIT %s OFFSET %s
    """, (category, pagelimit, offset))
    products = cursor.fetchall()
    for product in products:
                product_id = product['Id']

                # Calculate total sold quantity
                cursor.execute("""
                    SELECT SUM(orders.quantity) AS total_sold
                    FROM orders
                    WHERE orders.order_status = 'Completed'
                    AND orders.product_id = %s;
                """, (product_id,))
                sold = cursor.fetchone()
                product['total_sold'] = sold['total_sold'] if sold and sold['total_sold'] else 0

                # Calculate average rating
                cursor.execute("""
                    SELECT ROUND(AVG(rate), 1) AS average_rate
                    FROM rating
                    WHERE product_id = %s;
                """, (product_id,))
                rate = cursor.fetchone()
                product['Rating'] = rate['average_rate'] if rate and rate['average_rate'] else 0

    cursor.close()
    connection.close()

    return render_template('Home-page/product-category.html', 
                           products=products, 
                           username=username, 
                           profile_pic=profile_pic, 
                           category=category, 
                           current_page=page, 
                           total_pages=total_pages)



@app.route('/buyer_dashboard/seller-profile/<int:seller_id>', methods=['GET'])
def buyersellerprofile(seller_id):
    username, profile_pic = buyerid()
    buyer_id = session['buyer_id']
    pagelimit = 30

    # Get the current page number from the query string (default to 1)
    page = request.args.get('page', default=1, type=int)
    offset = (page - 1) * pagelimit  # Calculate the offset

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total_products FROM products WHERE products.seller_id = %s;", (seller_id,))
        total_products = cursor.fetchone()['total_products']
        total_pages = (total_products + pagelimit - 1) // pagelimit  # Calculate total pages

        cursor.execute("""
            SELECT *, sellers.shop_name 
            FROM products
            JOIN addresses_seller ON addresses_seller.seller_id = products.seller_id
            JOIN sellers ON sellers.seller_id = products.seller_id
            WHERE products.seller_id = %s
            LIMIT %s OFFSET %s;
        """, (seller_id, pagelimit, offset))

        Shopinfo = cursor.fetchall()
        for product in Shopinfo:
            product_id = product['Id']

            # Calculate total sold quantity
            cursor.execute("""
                SELECT SUM(orders.quantity) AS total_sold
                FROM orders
                WHERE orders.order_status = 'Completed'
                AND orders.product_id = %s;
            """, (product_id,))
            sold = cursor.fetchone()
            product['total_sold'] = sold['total_sold'] if sold and sold['total_sold'] else 0

            # Calculate average rating
            cursor.execute("""
                SELECT ROUND(AVG(rate), 1) AS average_rate
                FROM rating
                WHERE product_id = %s;
            """, (product_id,))
            rate = cursor.fetchone()
            product['Rating'] = rate['average_rate'] if rate and rate['average_rate'] else 0

        # Ensure Shopinfo is not empty
        if Shopinfo:
            shoplocation = f"{Shopinfo[0]['houseNo']}, {Shopinfo[0]['street']}, {Shopinfo[0]['barangay']}, {Shopinfo[0]['city']}, {Shopinfo[0]['Province']}"
        else:
            shoplocation = "No location available"

    finally:
        cursor.close()
        connection.close()

    return render_template('Home-page/shop.html', username=username, profile_pic=profile_pic, Shopinfo=Shopinfo,
                           seller_id=seller_id, shoplocation=shoplocation, buyer_id=buyer_id, current_page=page, total_pages=total_pages)

#====================================================================================================================


@app.route('/buyer_dashboard/seller-profile-report/<int:seller_id>', methods=['GET'])
def buyersellerprofilereport(seller_id):
    username, profile_pic = buyerid()
    return render_template('Home-page/message-report.html', username=username, profile_pic=profile_pic, seller_id=seller_id)

@app.route('/buyer_dashboard/seller-profile-report-seller/<int:seller_id>', methods=['POST'])
def buyersellerprofilereport_form(seller_id):
    # #print debugging information
    #print(f"Seller ID: {seller_id}")
    buyer_id =session['buyer_id']
    
    username, profile_pic = buyerid()
    #print(f"Buyer Username: {username}, Profile Pic: {profile_pic}")

    violation_type = request.form.get('violation-type')
    description = request.form.get('description')
    #print(f"Violation Type: {violation_type}")
    #print(f"Description: {description}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    

    image = request.files.get('proof-image')
    image_data = None
    if image and allowed_file(image.filename):
        image_data = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_data))
    
    
    

    try:
        # Debugging: #print the query and values
        query = """
            INSERT INTO report_sellerproduct (seller_id, violation_type, description, report_image,buyer_id) 
            VALUES (%s, %s, %s, %s,%s)
        """
        values = (seller_id, violation_type, description, image_data,buyer_id)
        
        cursor.execute(query, values)
        connection.commit()
        #print("Report successfully inserted into the database.")

    except Exception as e:
        connection.rollback()
        #print(f"An error occurred: {e}")
        return redirect(url_for('buyersellerprofilereport', seller_id=seller_id, error=str(e)))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")
    
    return redirect(url_for('buyersellerprofile', seller_id=seller_id, error='Report submitted.'))


@app.route('/seller-profile-report-seller/<string:shop_name>/<int:buyer_id>', methods=['POST'])
def buyersellerprofilereport_formmobile(shop_name, buyer_id):
    if not buyer_id:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    violation_type = request.form.get('violation-type')
    description = request.form.get('description')

    if not violation_type or not description:
        return jsonify({'success': False, 'message': 'Violation type and description are required.'}), 400

    image = request.files.get('proof-image')
    image_data = None
    if image and allowed_file(image.filename):
        image_data = secure_filename(image.filename)
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        image.save(os.path.join(upload_folder, image_data))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT seller_id FROM sellers WHERE shop_name = %s", (shop_name,))
    seller = cursor.fetchone()
    if not seller:
        cursor.close()
        connection.close()
        return jsonify({'success': False, 'message': 'Seller not found.'}), 404

    sellerid = seller['seller_id']

    try:
        query = """
            INSERT INTO report_sellerproduct (seller_id, violation_type, description, report_image, buyer_id) 
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (sellerid, violation_type, description, image_data, buyer_id)
        cursor.execute(query, values)
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"An error occurred: {e}")
        cursor.close()
        connection.close()
        return jsonify({'success': False, 'message': f'Failed to submit report: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({'success': True, 'message': 'Report submitted successfully.'}), 200

 #===========================================================check out =============================================





@app.route('/buyer_dashboard/cart', methods=['GET'])
def cartget():
    username, profile_pic = buyerid()
    total_payment = 0
    buyer_id = session.get('buyer_id')
    
    if not buyer_id:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT p.Product_Name, c.quantity, p.Price, p.Image, s.Shop_Name, p.Id, v.color, v.size, c.id As cart_id, p.Price * c.quantity AS total
            FROM cart_items c
            JOIN products p ON c.Product_Id = p.Id
            JOIN sellers s ON p.Seller_Id = s.seller_id
            JOIN productvariations v ON c.variation_id = v.id
            WHERE c.Buyer_Id = %s
        """, (buyer_id,))

        cart_items = cursor.fetchall()

        cart_items_grouped = {}
        if cart_items:
            for item in cart_items:
                shop_name = item['Shop_Name']
                if shop_name not in cart_items_grouped:
                    cart_items_grouped[shop_name] = []
                cart_items_grouped[shop_name].append(item)

        # Calculate total payment
        total_payment = sum(item['total'] for item in cart_items)
        #print(total_payment )
    except Exception as e:
        total_payment = 0
    finally:
        cursor.close()
        connection.close()

    return render_template('Home-page/cartpage.html', cart_items_grouped=cart_items_grouped, total_payment=total_payment, username=username, profile_pic=profile_pic)

#========================================================================================================================

@app.route('/proceedCheckout', methods=['POST'])
def proceedCheckout():
    
    selected_item_ids = request.form.getlist('selected_items[]')
    #print("id",selected_item_ids)
    if not selected_item_ids:
        flash('Please select at least one item to checkout.', 'error')
        return redirect(url_for('cartget'))
    
    
    session['checkout_items'] = selected_item_ids
    return redirect(url_for('placeorderget'))



@app.route('/update_cart_quantity', methods=['POST'])
def update_cart_quantity():
    item_id = request.form.get('item_id')
    quantity_str = request.form.get('quantity')

    # Check for invalid item ID or quantity
    if not item_id or not quantity_str:
        return jsonify({'status': 'error', 'message': 'Invalid item or quantity'}), 400

    # Safely convert quantity to an integer and check validity
    try:
        new_quantity = int(quantity_str)
        if new_quantity < 1:
            return jsonify({'status': 'error', 'message': 'Quantity must be at least 1'}), 400
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Quantity must be a number'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
      
        cursor.execute("""
            UPDATE cart_items 
            SET quantity = %s 
            WHERE id = %s
        """, (new_quantity, item_id))



        connection.commit() 

    
        cursor.execute("""
            SELECT price, (price * quantity) AS total_price 
            FROM cart_items 
            WHERE id = %s
        """, (item_id,))
        item = cursor.fetchone()

        if item is None:
            return jsonify({'status': 'error', 'message': f"Item not found in the cart for item ID: {item_id}"}), 404

        # Assuming the price is at index 0 and total price is at index 1
        price, total_price = item

        return jsonify({'status': 'success', 'new_total_price': total_price})

    except Exception as e:
        connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cursor.close()
        connection.close()



@app.route('/delete_cart_item', methods=['POST'])
def delete_cart_item():
    item_id = request.form.get('item_id')  # Get the item ID from the request
    buyer_id = session.get('buyer_id') 
    print(item_id)
    print()# Get buyer ID from session
    if not buyer_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401  # Handle unauthorized access

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Delete the item from the cart
        cursor.execute("""
            DELETE FROM cart_items
            WHERE product_id = %s AND buyer_id = %s
        """, (item_id, buyer_id))

        connection.commit()  # Commit the transaction

        # Check if the deletion was successful
        if cursor.rowcount > 0:
            return jsonify({'status': 'success', 'message': 'Item deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Item not found in cart'}), 404

    except Exception as e:
        connection.rollback()  # Rollback on error
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cursor.close()
        connection.close()  


@app.route('/buyer_dashboard/productOverview/<int:product_id>') 
def productOverview(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = buyerid()
    
    # Call the product_description function with the product_id
    seller_logo, product_name, description, price, product_pic, sellerpic, sellershopname, product_id = product_description(product_id)
    #print(product_id)

   # Fetch the Seller_Id from the products table
    cursor.execute("SELECT Seller_Id FROM products WHERE Id = %s", (product_id,))
    rows = cursor.fetchone()  # Fetch one row

    if rows:
        seller_id = int(rows['Seller_Id'])  # Convert to integer if needed
    else:
        seller_id = None  # No seller_id found

    # SELECT Seller_Id FROM products WHERE products.Id = 33
    # Fetch product variations from the database
    variations = get_product_variations(product_id)  # This should return a list of variation dictionaries
    cursor.execute("""SELECT  SUM(orders.quantity) AS total_sold
                FROM orders
                WHERE orders.order_status = 'Completed' 
                AND orders.product_id = %s;""", (product_id,))
    sold = cursor.fetchone()
    solds = sold['total_sold']
    print(solds)
    cursor.execute("""
        SELECT ROUND(AVG(rate), 1) AS average_rate
        FROM rating
        WHERE product_id = %s;
    """, (product_id,))
    rate = cursor.fetchone()
    ratings = rate['average_rate']


    cursor.execute("""SELECT * ,CONCAT(buyers.Fname, " " ,buyers.Mname," ",buyers.Lname) AS Fullname
                        FROM rating 
                        JOIN buyers ON buyers.buyer_id = rating.buyer_id
                        WHERE product_id  = %s;""", (product_id,))
    reviews = cursor.fetchall()


    
    return render_template(
        'Home-page/product-overview.html',
        username=username,
        profile_pic=profile_pic,
        productName=product_name,
        description=description,
        price=price,
        productpic=product_pic,
        sellerpic=sellerpic,
        sellershopname=sellershopname,
        product_id=product_id,
        variations=variations,
        seller_id = seller_id,reviews =reviews,
        seller_logo = seller_logo,solds = solds, ratings=ratings
        
        # seller_id = seller_id # Pass variations to the template
    )

def get_product_variations(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    variations = []

    try:
        # Get unique colors (including NULL for no color)
        cursor.execute("""
            SELECT DISTINCT color 
            FROM ProductVariations 
            WHERE product_id = %s
        """, (product_id,))
        colors = cursor.fetchall()

       # Ensure that NULL values are replaced with a user-friendly message
        for color in colors:
            color_value = color['color'] if color['color'] is not None else 'No Color'  # Show 'No Color' if NULL

            # Then fetch the sizes, and use the same NULL handling logic for sizes
            if color_value == 'No Color':
                cursor.execute("""
                    SELECT size
                    FROM ProductVariations 
                    WHERE product_id = %s AND color IS NULL
                """, (product_id,))
            else:
                cursor.execute("""
                    SELECT size
                    FROM ProductVariations 
                    WHERE product_id = %s AND color = %s
                """, (product_id, color_value))

            
            size_rows = cursor.fetchall()
            sizes = [ row['size'] for row in size_rows]

            variations.append({'color': color_value, 'sizes': sizes})

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        connection.close()

    return variations


def variation_stocks(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    variations = []

    try:
        # Fetch all color, size, and stock combinations for the product
        cursor.execute("""
            SELECT color, size, stock 
            FROM ProductVariations 
            WHERE product_id = %s
            ORDER BY color, size
        """, (product_id,))
        rows = cursor.fetchall()
        
        # Group by color
        color_map = {}
        for row in rows:
            color = row['color']
            size = row['size']
            stock = row['stock']
            
            if color not in color_map:
                color_map[color] = []
            
            color_map[color].append({'size': size, 'stock': stock})
        
        # Prepare the variations list
        for color, size_list in color_map.items():
            variations.append({'color': color, 'sizes': size_list})
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        cursor.close()
        connection.close()
    
    return variations



#==================================================================================================
# direct buying
@app.route('/buyer_dashboard/directbuying/<int:product_id>', methods=["GET", "POST"])
def directbuying(product_id):

    if request.method == 'POST':
        #print(request.form)  # Debugging: View all form data
    # Retrieve form data
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity',1))  
        color = request.form.get('selected_color')
        size = request.form.get('selected_size')
        total_price = request.form.get('prize')
        buying = 1
        # selected_item =  request.form.getlist('selected_items[]')
        #print("quantity11:", quantity)
        #print("colo1r11:", color)
        #print("size11:", size)
        #print(buying)

    


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = buyerid()
    user_id = session['buyer_id']

    cursor.execute("SELECT COUNT(*) AS variation_count FROM productvariations WHERE product_id = %s", (product_id,))
    has_variations = cursor.fetchone()['variation_count'] > 0

    # Attempt to find the correct variation if variations exist
    variation_data = None
    if has_variations:
        if color and size:  # Both color and size provided
            cursor.execute("SELECT id FROM productvariations WHERE color = %s AND size = %s AND product_id = %s", (color, size, product_id))
        elif color:  # Only color provided
            cursor.execute("SELECT id FROM productvariations WHERE color = %s AND size IS NULL AND product_id = %s", (color, product_id))
        elif size:  # Only size provided
            cursor.execute("SELECT id FROM productvariations WHERE size = %s AND color IS NULL AND product_id = %s", (size, product_id))
        
        variation_data = cursor.fetchone()

    # Redirect with an error if variations are required but none selected
    if has_variations and variation_data is None:
        return redirect(url_for('productOverview', product_id=product_id, error="THE variety is not available"))
    
    variation_id = variation_data['id'] if variation_data else 0

    cursor.execute("""
                SELECT buyers.*, users.email, addresses_buyer.houseNo, addresses_buyer.street, 
                    addresses_buyer.barangay, addresses_buyer.city, addresses_buyer.Province
                FROM buyers 
                JOIN users ON users.user_id = buyers.user_id 
                JOIN addresses_buyer ON addresses_buyer.buyer_id = buyers.buyer_id
                WHERE buyers.buyer_id = %s
            """, (user_id,))
    user = cursor.fetchone()
    fullname = f"{user['Fname']}, {user['Mname']}, {user['Lname']}"

    location = f"{user['houseNo']}, {user['street']}, {user['barangay']}, {user['city']}, {user['Province']}"


  # Get the variation ID
    #print("variation",variation_id)
    
    
    # Fetching user information
    cursor.execute("""
        SELECT buyers.*, users.email 
        FROM buyers 
        JOIN users ON users.user_id = buyers.user_id 
        WHERE buyers.buyer_id = %s
    """, (user_id,))
    user = cursor.fetchone()

    # Fetching product and seller details
    query = """
        SELECT 
        p.Id AS product_id, 
        p.Product_Name, 
        p.Price, 
        p.Image, 
        s.seller_id, 
        b.buyer_id, 
        v.color,v.size, v.id
    FROM 
        products p 
    JOIN 
        productvariations v 
    JOIN 
        sellers s ON p.seller_id = s.seller_id 
    JOIN 
        buyers b ON b.buyer_id = %s 
    WHERE 
        p.Id = %s AND v.id = %s;

    """
    cursor.execute(query, (user_id, product_id,variation_id))
    cart_items = cursor.fetchall()
    cart_items_with_details = []
    for item in cart_items:
        item_dict = {
            'product_id': item['product_id'],
            'Product_Name': item['Product_Name'],
            'Price': item['Price'],
            'Image': item['Image'],
            'seller_id': item['seller_id'],
            'buyer_id': item['buyer_id'],
            'color': item['color'],
            'size': item['size'],
            'variation_id': item['id'],
            'quantity': quantity,  # Add the quantity
            'total_price': quantity * item['Price']  # Calculate total price
        }
        cart_items_with_details.append(item_dict)
    
    total_price = sum(item['total_price'] + 35 for item in cart_items_with_details)

    return render_template(
        'Home-page/placeorder.html',
        username=username,
        profile_pic=profile_pic,
        user=user,
        cart_items=cart_items_with_details,
        total_price =total_price, buying = buying,
        variation_id =variation_id,product_id = product_id,  quantity= quantity,
        fullname = fullname,location = location

        
    )


@app.route('/buyer_dashboard/placeorder', methods= ["GET"])
def placeorderget():
    username, profile_pic = buyerid()
    if 'checkout_items' not in session or not session['checkout_items']:
        flash('No items selected for checkout.', 'error')
        return redirect(url_for('cart'))
    
    else:
        if 'buyer_id' in session:
            user_id = session['buyer_id']
            
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            # Fetch user details
            cursor.execute("""
                SELECT buyers.*, users.email, addresses_buyer.houseNo, addresses_buyer.street, 
                    addresses_buyer.barangay, addresses_buyer.city, addresses_buyer.Province
                FROM buyers 
                JOIN users ON users.user_id = buyers.user_id 
                JOIN addresses_buyer ON addresses_buyer.buyer_id = buyers.buyer_id
                WHERE buyers.buyer_id = %s
            """, (user_id,))
            user = cursor.fetchone()
            fullname = f"{user['Fname']}, {user['Mname']}, {user['Lname']}"

            location = f"{user['houseNo']}, {user['street']}, {user['barangay']}, {user['city']}, {user['Province']}"


            # Empty Cart
            selected_item_ids = session['checkout_items']
            checkout_items = []
            total_price = 0
            #print(selected_item_ids)
            
            # Fetch cart items in a single query
            placeholders = ', '.join(['%s'] * len(selected_item_ids))
            query = f"""
            SELECT cart_items.*, (cart_items.quantity * products.Price) AS total_price, products.Product_Name, products.Price, productvariations.color, 			 			productvariations.size,	products.Image, products.Seller_Id
            FROM cart_items
            JOIN productvariations ON cart_items.variation_id  = productvariations.Id 
            JOIN products ON cart_items.product_id  = products.Id 
            JOIN sellers ON products.Seller_Id = sellers.seller_id
            WHERE cart_items.id IN ({placeholders}) AND cart_items.buyer_id = %s
            """

            cursor.execute(query, selected_item_ids + [user_id])
            checkout_items = cursor.fetchall()
            
            total_price = sum(item['total_price'] for item in checkout_items )
            
            cursor.close()

        return render_template('Home-page/placeorder.html', user=user, cart_items=checkout_items, total_price=total_price,username=username,profile_pic=profile_pic,
                               location = location,fullname =fullname)


@app.route('/checkoutPost', methods=['POST'])
def checkoutPost():
    if 'buyer_id' in session:
        quantity =  request.form.get('quantity')
        buying = request.form.get('buying')
        variation_id = request.form.get('variation_id')
        product_id = request.form.get('product_id')
        #print("product_id11",product_id)
        #print("id", buying)
        #print("quantity" ,quantity)
        # Check if buying is '1'
        if buying == '1':
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            user_id = session['buyer_id']
           
            query = """SELECT  *, productvariations.color , productvariations.size, productvariations.id AS variation_id , products.Price * %s AS total_price
                FROM products 
                JOIN productvariations ON productvariations.id = %s
                JOIN sellers ON products.Seller_Id = sellers.seller_id
                WHERE productvariations.id = %s
               AND products.Id = %s;
                    """
            cursor.execute(query, (quantity,variation_id, variation_id, product_id))
            checkout_items = cursor.fetchall()
            for item in checkout_items:
                cursor.execute('''
                            INSERT INTO orders (buyer_id, product_id, seller_id, order_status, 
                                                quantity, total_price, variation_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ''', (user_id, item['Id'], item['Seller_Id'], 'pending', 
                            quantity, item['total_price'], item['variation_id']))
                connection.commit()

            
            #print("id================================================")
            #print("id", buying) 
            #print("variation_id",variation_id)
            #print("product_id11",product_id)

            
            return redirect(url_for('completed'))
        else:
            #print(buying)
            user_id = session['buyer_id']
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cart_items = request.form.getlist('cart_ids[]')
            #print(cart_items)
            
            # Handle cart items only if it is not empty
            if cart_items:
                placeholders = ', '.join(['%s'] * len(cart_items))
                
                # Fetch cart items with details
                query = f"""
                SELECT cart_items.*, (cart_items.quantity * products.Price) AS total_price, 
                       products.Product_Name, products.Price, productvariations.color, 
                       productvariations.size, products.Image, products.Seller_Id
                FROM cart_items
                JOIN productvariations ON cart_items.variation_id = productvariations.Id 
                JOIN products ON cart_items.product_id = products.Id 
                JOIN sellers ON products.Seller_Id = sellers.seller_id
                WHERE cart_items.id IN ({placeholders}) AND cart_items.buyer_id = %s
                """
                cursor.execute(query, cart_items + [user_id])
                checkout_items = cursor.fetchall()

                # Insert each item into orders
                for item in checkout_items:
                    cursor.execute('''
                        INSERT INTO orders (buyer_id, product_id, seller_id, order_status, 
                                            quantity, total_price, variation_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (user_id, item['product_id'], item['Seller_Id'], 'pending', 
                          item['quantity'], item['total_price'], item['variation_id']))

                # Clear cart after placing order
                delete_query = f"""
                    DELETE FROM cart_items
                    WHERE id IN ({placeholders}) AND buyer_id = %s
                """
                cursor.execute(delete_query, cart_items + [user_id])

                # Commit the transaction
                connection.commit()
                cursor.close()

                flash('Your order has been placed successfully!', 'success')
                return redirect(url_for('completed',error= "Your order has been placed successfully!"))
            else:
                flash('No items in the cart.', 'warning')
                return redirect(url_for('cart'))
    else:
        return redirect(url_for('login'))


#============================================================ORDER================================================================

@app.route('/completed')
def completed():
    username, profile_pic = buyerid()
    return render_template ('Home-page/order-done.html',username = username,profile_pic =profile_pic)

@app.route('/user-orders')
def user_orders():
    username, profile_pic = buyerid()
    if 'buyer_id' in session:
        user_id = session['buyer_id']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch all orders with their creation time
        cursor.execute('''
            SELECT 
                orders.order_id,
                orders.created_at, 
                orders.product_id, 
                orders.quantity, 
                orders.total_price + 35 AS total_price,
                orders.order_status,
                products.product_name, 
                products.image, 
                products.Price,
                productvariations.color, productvariations.size
            FROM orders
            JOIN products ON orders.product_id = products.Id
            JOIN productvariations ON orders.variation_id = productvariations.id
            
            WHERE orders.buyer_id = %s
            ORDER BY orders.created_at DESC;
        ''', (user_id,))
        orders = cursor.fetchall()
        for order in orders:
            cursor.execute(
                '''
                SELECT COUNT(*) AS rate 
                FROM rating 
                WHERE product_id = %s AND buyer_id = %s;
                ''', (order['product_id'], user_id)
            )
            order['has_rating'] = cursor.fetchone()['rate'] > 0

        cursor.close()
        connection.close()

        order_group = {}
        if orders:
            for order in orders:
                # Extract the date part from the created_at timestamp
                date = order['created_at'].date()  # Assuming created_at is a datetime object
                
                if date not in order_group:
                    order_group[date] = []
                
                # Append the order to the corresponding date
                order_group[date].append(order)
        


        return render_template('Home-page/orders.html', orders=orders ,username=username ,profile_pic =profile_pic )
    else:
        return redirect(url_for('login'))
    



#=======================================================tracking=============================================================================
@app.route('/track_order/<int:order_id>', methods=['GET'])
def track_order(order_id):
    username, profile_pic = buyerid()
    if 'buyer_id' in session:
        user_id = session['buyer_id']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        #print(order_id)
        #print(user_id)

        cursor.execute("""
           SELECT 
                orders.order_id, 
                orders.created_at, 
                orders.total_price,
                orders.order_status,
                orders.quantity, 
                products.product_name, 
                products.image, 
                productvariations.color, 
                productvariations.size
             
            FROM orders
            JOIN products ON orders.product_id = products.Id
            JOIN productvariations ON orders.variation_id = productvariations.id
            
            WHERE orders.order_id = %s AND orders.buyer_id = %s;

        """, (order_id, user_id))
        
        order_details = cursor.fetchone()  # Change here: use order_details instead of order
        
        cursor.execute("""
            SELECT delivery_status
            FROM assignrider
            WHERE order_id = %s;
        """, (order_id,))
        results = cursor.fetchall()
        order_detail = results[0] if results else None

        print(order_detail)
        # # Check if the order exists
        # if order_details is None:
        #     cursor.close()
        #     connection.close()
        #     return render_template('Home-page/error.html', message="Order not found"), 404  # Custom error page
        
        cursor.close()
        connection.close()

    else:
        return redirect(url_for('login'))

    return render_template('Home-page/tracking.html', order_details=order_details , username=username, profile_pic=profile_pic,order_detail = order_detail )  # Pass order_details instead of order

#159
@app.route('/update-order-status', methods=['POST'])
def update_order_status():
    order_id = request.form.get('order_id')
    
    # Debug print statement
    print(f"Debug: Received order_id for update: {order_id}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Update the order status in the database
    if order_id:
        cursor.execute(
            "UPDATE orders SET order_status = 'Completed' WHERE order_id = %s",
            (order_id,)
        )
        connection.commit()

    cursor.close()
    connection.close()
    
    return redirect(url_for('user_orders'))




#========================================================user cancel=======================================================================
@app.route('/update_order_status_cancelled_user', methods=['POST'])
def update_order_status_cancelled_user():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Validate session and form data
        buyer_id = session.get('buyer_id')
        order_id = request.form.get('order_id')
        cancel_reason = request.form.get('reason')
        
        if not buyer_id or not order_id or not cancel_reason:
            print("Error: Missing required data (buyer_id, order_id, or cancel_reason).")
            return redirect(url_for('user_orders'))

        # Insert notification for the seller
        cursor.execute(
            """
            INSERT INTO notification_seller (buyer_id, cancel_reason, order_id)
            VALUES (%s, %s, %s)
            """,
            (buyer_id, cancel_reason, order_id)
        )
        
        # Update the order status to 'Cancelled'
        cursor.execute(
            "UPDATE orders SET order_status = 'Cancelled' WHERE order_id = %s",
            (order_id,)
        )
        
        # Commit changes
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    # Redirect to the user's orders page
    return redirect(url_for('user_orders'))


#==============================================================================================================================================
#username and pic
def buyerid():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM buyers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        
        username = user['Fname'] if user else ''
        profile_pic = user['profile_pic'] if user else ''

    finally:
        cursor.close()
        connection.close()


    return username, profile_pic


# @app.route('/createBuyerForm', methods=['GET'])
# def createBuyerForm():
#     provided_password = request.args.get('provided_password')
#     provided_email = request.args.get('provided_email')  # username 
#     #print(provided_email)
#     return render_template('Login-page/LoginPage-buyerForm.html', email1=provided_email, password1=provided_password)

@app.route('/createBuyerFormpost', methods=['POST'])
def createBuyerFormpost():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    provided_password = request.form.get('password')  
    provided_email = request.form.get('email')      

    # Check if email already exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (provided_email,))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        connection.close()
        # Correct syntax for redirect and url_for
        return redirect(url_for('createAccountBuyer', error="Email already registered."))

    # Close the cursor and connection after use
    cursor.close()
    connection.close()

    #print(provided_email)
    return render_template('Login-page/LoginPage-buyerForm.html', email1=provided_email, password1=provided_password)




# ===============================================================================
import requests
def get_location_name(code, location_type):
    # Build the URL based on the location type (province, municipality, barangay)
    base_url = "https://psgc.gitlab.io/api/"
    print(location_type)
    
    if location_type == 'province':
        url = f"{base_url}provinces/{code}"
    elif location_type == 'municipality':
        url = f"{base_url}municipalities/{code}"
    elif location_type == 'barangay':
        url = f"{base_url}barangays/{code}"
    else:
        return 'Unknown Location'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Return the name from the response
        return data.get('name', 'Unknown Location')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e}")
        return 'Unknown Location'
    
@app.route('/get-location/<location_type>/<code>', methods=['GET'])
def get_location(location_type, code):
    location_name = get_location_name(code, location_type)
    print(location_name)
    return jsonify({'location_name': location_name})

# ===============================================================================

@app.route('/registerbuyer', methods=['POST'])
def registerbuyer():
    # Set default profile pic path (or binary data depending on your approach)
    default_pic = get_default_profile_pic()
    
    # Fetch form data
    provided_email = request.form['email1']
    hashed_password = generate_password_hash(request.form['password'])
    
    Fname = request.form['fname']
    Mname = request.form['Mname']
    Lname = request.form['Lname']
    mobile_number = request.form['number']
    gender = request.form['gender']
    birthdate = f"{request.form['year']}-{request.form['month']}-{request.form['day']}"
    
    # Handle the valid ID image upload
    image = request.files.get('valid_id')
    valid_id_filename = None
    if image and allowed_file(image.filename):
        valid_id_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], valid_id_filename))
    
    # Handle profile picture upload or use default
    profile_image = "profile-icon-design-free-vector.jpg"
   
    
    # Address details
    houseNo = request.form['houseNo']
    street = request.form['street']
    barangay = request.form['barangay']
    city = request.form['city']
    Province = request.form['Province']
    postal = request.form['postal']

    barangay_name = get_location_name(barangay, 'barangay')
    city_name = get_location_name(city, 'municipality')
    province_name = get_location_name(Province, 'province')

    print(barangay_name)
    print(city_name)
    print(province_name)
    
    # Database connection
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Insert into users table
        query_user = "INSERT INTO users (email, password, role_id) VALUES (%s, %s, %s)"
        cursor.execute(query_user, (provided_email, hashed_password, 1))
        user_id = cursor.lastrowid
        
        # Insert into buyers table
        buyer_query = """
        INSERT INTO buyers (user_id, email, Fname, Mname, Lname, mobile_number, gender, birthdate, profile_pic, valid_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(buyer_query, (user_id, provided_email, Fname, Mname, Lname, mobile_number, gender, birthdate, profile_image, valid_id_filename))
        buyer_id = cursor.lastrowid
        
        # Insert into addresses_buyer table
        address_query = """
        INSERT INTO addresses_buyer (buyer_id, houseNo, street, barangay, city, Province, postal_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(address_query, (buyer_id, houseNo, street, barangay_name, city_name, province_name, postal))

        connection.commit()
        return redirect(url_for('login', error="Registered successfully, Waiting for Admin approval!"))

    except Exception as err:
        # Rollback if any error occurs
        connection.rollback()
        print(f"Error during registration: {err}")
        return redirect(url_for('registerbuyer', error="An error occurred during registration."))

    finally:
        cursor.close()
        connection.close()




    
###

@app.route('/buyer_dashboard')
def buyer_dashboard():
    username, profile_pic = buyerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    pagelimit = 30

    # Get the current page number from the query string (default to 1)
    page = request.args.get('page', default=1, type=int)
    offset = (page - 1) * pagelimit  # Calculate the offset

    # Get the current page number from the query string (default to 1)
    page = request.args.get('page', default=1, type=int)
    offset = (page - 1) * pagelimit  # Calculate the offset

    try:
        cursor.execute("SELECT * FROM buyers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()
        banner = "SELECT banner_filename FROM baner ORDER BY banner_id DESC LIMIT 1"
        cursor.execute(banner)
        result = cursor.fetchone()  # Fetch one result

        # Extract filename if result is not None
        banner_filename = result['banner_filename'] if result else None

        if user:
            session['buyer_id'] = user['buyer_id']
            cursor.execute("SELECT COUNT(*) AS total_products FROM products;")
            total_products = cursor.fetchone()['total_products']
            total_pages = (total_products + pagelimit - 1) // pagelimit  # Calculate total pages


            # Fetch products with pagination
            cursor.execute("""
                SELECT * 
                FROM products 
                ORDER BY RAND() 
                LIMIT %s OFFSET %s;
            """, (pagelimit, offset))
            products = cursor.fetchall()

            for product in products:
                product_id = product['Id']

                # Calculate total sold quantity
                cursor.execute("""
                    SELECT SUM(orders.quantity) AS total_sold
                    FROM orders
                    WHERE orders.order_status = 'Completed'
                    AND orders.product_id = %s;
                """, (product_id,))
                sold = cursor.fetchone()
                product['total_sold'] = sold['total_sold'] if sold and sold['total_sold'] else 0

                # Calculate average rating
                cursor.execute("""
                    SELECT ROUND(AVG(rate), 1) AS average_rate
                    FROM rating
                    WHERE product_id = %s;
                """, (product_id,))
                rate = cursor.fetchone()
                product['Rating'] = rate['average_rate'] if rate and rate['average_rate'] else 0

        else:
            products = []
            total_pages = 0
    finally:
        cursor.close()
        connection.close()

    return render_template('Home-page/homepage.html', 
                           username=username, 
                           profile_pic=profile_pic, 
                           products=products, banner_filename=banner_filename,
                           current_page=page,total_pages = total_pages)

@app.route('/buyer_dashboard/buyer_profile')
def Buyer_profile():
    username, profile_pic = buyerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT * 
            FROM addresses_buyer 
            JOIN buyers ON addresses_buyer.buyer_id = buyers.buyer_id 
            WHERE buyers.user_id = %s;
        """, (session['id'],))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['user_id']  
            Fname = user['Fname']
            Mname = user['Mname']
            Lname = user['Lname']
            gender = user['gender']

            houseNo = user['houseNo']
            street = user['street']
            barangay = user['barangay']
            city = user['city']
            Province = user['Province']
            postal_code = user['postal_code']
            email = user['email']
            contact_num = user['mobile_number']
            birthday = user['birthdate']

    except Exception as e:
        print(f"Error: {str(e)}")
        # Handle error as needed

    finally:
        cursor.close()
        connection.close()

    # Pass all the fetched variables to the template
    return render_template(
        'Home-page/profile.html',
        username=username, profile_pic=profile_pic,
        Fname=Fname, Mname=Mname, Lname=Lname,
        houseNo=houseNo, street=street, barangay=barangay, city=city, Province=Province, postal_code=postal_code, 
        email=email, contact_num=contact_num, gender = gender, birthday= birthday
    )






# ==========================================================================================================================
@app.route('/buyer_profile_form/update-profile', methods=['GET', 'POST'])
def buyer_update_profile():
    username, profile_pic = buyerid()
    Fname, Mname, Lname, email, contact_num, houseNo, street, barangay, city, Province, postal_code, description=buyerinfo()

    return render_template('Home-page/profile-form.html', username=username, profile_pic=profile_pic,
                           Fname = Fname, Mname = Mname, Lname = Lname,
                           email = email, contact_num = contact_num,
                           houseNo = houseNo, street = street, barangay = barangay,
                           city = city, Province = Province, postal_code = postal_code,
                           description = description 
                              )

@app.route('/update-profile-image', methods=['POST'])
def update_profile_image():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Fetch the buyer's current profile picture from the database
        cursor.execute("SELECT profile_pic FROM buyers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        if user:
            # Check if an image is part of the request
            if 'image' not in request.files:
                return redirect(url_for('buyer_update_profile'))

            image = request.files['image']

            # Ensure the image is not empty
            if image.filename == '':
                return redirect(url_for('buyer_update_profile'))

            # Check if the file extension is allowed
            if not allowed_file(image.filename):
                return redirect(url_for('buyer_update_profile'))

            # Secure the filename and save the file to the server
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Define UPLOAD_FOLDER in your config

            # Save the image to the server
            image.save(image_path)

            # Update the profile picture in the database with the image filename
            cursor.execute("""
                UPDATE buyers
                SET profile_pic = %s 
                WHERE user_id = %s
            """, (filename, session['id']))
            connection.commit()

    except Exception as e:
        connection.rollback()
        print(f"Error: {str(e)}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('buyer_update_profile'))




@app.route('/update-account-info', methods=['POST'])
def update_account_info():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    try:
        #print(f"Received email: {email}, password: {'<hidden>' if password else 'None'}")

        # Hash the password if it's provided
        if password:
            hashed_password = generate_password_hash(password)
            #print(f"Hashed password: {hashed_password}")

            # Update both email and password in `users` table
            cursor.execute("""
                UPDATE users 
                SET email = %s, password = %s
                WHERE user_id = %s
            """, (email, hashed_password, session['id']))
        else:
            # Update only email if no password provided
            cursor.execute("""
                UPDATE users 
                SET email = %s
                WHERE user_id = %s
            """, (email, session['id']))

        # Update email in the `buyers` table as well
        cursor.execute("""
            UPDATE buyers 
            SET email = %s
            WHERE user_id = %s
        """, (email, session['id']))

        connection.commit()
        #print("Database commit successful.")
        return redirect(url_for('buyer_update_profile', success="Account updated successfully"))

    except Exception as e:
        connection.rollback()
        #print(f"Error: {str(e)}")
        return redirect(url_for('buyer_update_profile', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")

@app.route('/update-account-personal-info', methods=['POST'])
def update_account_personal_info():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Retrieve form data (excluding email and password)
    fname = request.form.get('fname')
    mname = request.form.get('mname')
    lname = request.form.get('lname')
    contact_num = request.form.get('number')
    gender = request.form.get('gender')

    try:
        # Update the buyer's information (first name, middle name, last name, contact number, gender)
        cursor.execute("""
            UPDATE buyers
            SET Fname = %s, Mname = %s, Lname = %s, mobile_number = %s, gender = %s
            WHERE user_id = %s
        """, (fname, mname, lname, contact_num, gender, session['id']))

        connection.commit()
        #print(f"Account info updated for user_id: {session['id']}")

        # Success feedback (You can also handle this with a #print statement as feedback)
        #print("Account updated successfully.")
        return redirect(url_for('buyer_update_profile', success="Account updated successfully"))

    except Exception as e:
        connection.rollback()
        #print(f"Error: {str(e)}")
        return redirect(url_for('buyer_update_profile', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")



@app.route('/update-address-buyer', methods=['POST'])
def update_address_buyer():

    houseNo = request.form.get('houseNo')
    street = request.form.get('street')
    barangay = request.form.get('barangay')
    city = request.form.get('city')
    province = request.form.get('Province')
    postal_code = request.form.get('postal')

    try:
       
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Update the address in the database
        cursor.execute("""
            UPDATE addresses_buyer
            SET houseNo = %s, street = %s, barangay = %s, city = %s, Province = %s, postal_code = %s
            WHERE buyer_id = (SELECT buyer_id FROM buyers WHERE user_id = %s)
        """, (houseNo, street, barangay, city, province, postal_code, session['id']))

        connection.commit()
        #print("Address updated successfully.")

        # Success message
        return redirect(url_for('buyer_update_profile', success="Address updated successfully"))

    except Exception as e:
        connection.rollback()
        #print(f"Error: {str(e)}")
        return redirect(url_for('buyer_update_profile', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")


# ====================================================================================================================

#rider admin 

#rider registered #for blocking
@app.route('/account-management/requestAcc-rider')
def admin_management_requestAcc_rider():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT riders.profile_pic,
                CONCAT(riders.Fname, ' ', riders.Mname, ' ', riders.Lname) AS fullname, users.*
                FROM users
                JOIN riders ON riders.user_id = users.user_id
                WHERE users.approval = 1 AND users.active = 'ACTIVE';

        """)
        rider_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template ('admin-page-rider/account-management.html', rider_data=rider_data )


#rider register for approval
@app.route('/riderApproval')
def admin_management_requestAcc_rider_approval():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT *
            FROM users
            JOIN riders ON riders.user_id = users.user_id
            WHERE users.approval = 0 AND users.active = 'ACTIVE';
        """)
        rider_data = cursor.fetchall()  # Fetch all results
        
    finally:
        cursor.close()
        connection.close()

    return render_template ('admin-page-rider/rider-approval.html', rider_data=rider_data )


#rider details

@app.route('/riderDetailsAcc-buyer/<int:user_id>')
def admin_management_detailsAcc_rider(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
              SELECT *,
                CONCAT(riders.Fname, ' ', riders.Mname, ' ', riders.Lname) AS fullname
            FROM users
            JOIN riders ON riders.user_id = users.user_id
            JOIN addresses_rider ON addresses_rider.rider_id = riders.rider_id 
            WHERE users.approval = 0 
            AND users.user_id = %s;
        """, (user_id,))
        
        users_data = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching user details: {e}")
        users_data = []  # Return empty data on error

    finally:
        cursor.close()
        connection.close()

    return render_template('admin-page-rider/rider-approval-details.html', users_data=users_data)



#rider set to active account for rider
@app.route('/approve_rider/<int:user_id>', methods=['POST'])
def approve_user_rider(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch the user's full name
        cursor.execute(
            """
           SELECT 
                CASE 
                    WHEN b.user_id IS NOT NULL THEN CONCAT(b.Lname, ' ', b.Fname, ' ', COALESCE(b.Mname, ''))
                    WHEN s.user_id IS NOT NULL THEN CONCAT(s.Lname, ' ', s.Fname, ' ', COALESCE(s.Mname, ''))
                    WHEN r.user_id IS NOT NULL THEN CONCAT(r.Lname, ' ', r.Fname, ' ', COALESCE(r.Mname, ''))
                END AS FullName
            FROM users 
            LEFT JOIN buyers b ON b.user_id = users.user_id
            LEFT JOIN sellers s ON s.user_id = users.user_id
            LEFT JOIN riders r ON r.user_id = users.user_id
            WHERE users.user_id = %s
            """,
            (user_id,)
        )
        fullname_result = cursor.fetchone()
        fullname = fullname_result['FullName'] if fullname_result and fullname_result['FullName'] else None

        if not fullname:
            print("User not found.")
            print(user_id)
            return redirect(url_for('admin_management_requestAcc_rider_approval', error="User not found."))

        # Fetch recipient email from the form
        recipient_email = request.form.get('email')
        if not recipient_email:
            print("Recipient email not provided.")
            return redirect(url_for('admin_management_requestAcc_rider_approval', error="Recipient email not provided."))

        # Update user approval status
        cursor.execute("UPDATE users SET approval = 1 WHERE user_id = %s", (user_id,))
        connection.commit()

        # Prepare the email content
        message_content = f"""Dear {fullname},

We are delighted to inform you that your EcoHaven account has been successfully approved. 
You now have full access to our platform, where you can discover and enjoy a wide range of home and garden products.

If you have any questions or require assistance as you navigate the platform, please feel free to reach out to our support team.

Welcome to EcoHaven, and thank you for being part of our community.

Sincerely,
The EcoHaven Team"""

        # Send the approval email
        msg = Message(
            subject="Congratulations! Your EcoHaven Account Has Been Approved",
            sender=app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        msg.body = message_content
        mail.send(msg)
        print(f"Approval email sent to {recipient_email}")

    except Exception as e:
        connection.rollback()  # Rollback in case of any failure
        print(f"An error occurred: {e}")
        return redirect(url_for('admin_management_requestAcc_rider_approval', error="An error occurred during approval."))

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_management_requestAcc_rider_approval', success="User approved successfully."))








#rider homepage
# @rider_dashboard
#147
@app.route('/rider_dashboard' , methods=['GET'])
def rider_dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    print(session['id'])
    
    try:
        print(f"Session Data Before Fetch: {session}")  # Debugging

        # Get rider details from the database
        cursor.execute("SELECT * FROM riders WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        if user:
            session['rider_id'] = user['rider_id']  # Store in session
            print(f"Rider ID Set in Session: {session['rider_id']}") 
            Fname = user['Fname']
           
            profile_pic =user['profile_pic']

        cursor.execute("""
             SELECT 
                orders.order_id, 
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname, 
                CONCAT(addresses_buyer.houseNo, ' ', addresses_buyer.street, ' ', 
                    addresses_buyer.barangay, ' ', addresses_buyer.city, ' ', 
                    addresses_buyer.Province) AS Fulladdress
            FROM orders
            JOIN buyers ON orders.buyer_id = buyers.buyer_id
            JOIN addresses_buyer ON buyers.buyer_id = addresses_buyer.buyer_id
            JOIN assignrider ON assignrider.order_id = orders.order_id
            WHERE orders.order_status = 'Shipped' AND assignrider.rider_id = %s
        """, (session['rider_id'],))
        

        order_data = cursor.fetchall()
        order_count = len(order_data)

    except Exception as e:
        print(f"Error fetching user details: {e}")
        order_data = []  # Return empty data on error

    finally:
        cursor.close()
        connection.close()

    return render_template('Rider-page/dashboard.html', order_data=order_data, Fname = Fname, profile_pic = profile_pic, order_count=order_count)  

@app.route('/rider_dashboard-post', methods=['POST'])
def rider_dashboard_post():
    print(f"Session Data: {session}")  # Debugging print

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        order_id = request.form.get('order_id')  
        user_id = session.get('id')  # Get user_id from session

        print(f"Received Order ID: {order_id}")  # Debugging print
        print(f"Session User ID: {user_id}")  # Debugging print

        if not user_id:
            print("Error: No user_id in session")
            return redirect(url_for('rider_dashboard'))

        # Fetch rider_id based on session user_id
        cursor.execute("SELECT rider_id FROM riders WHERE user_id = %s", (user_id,))
        rider = cursor.fetchone()

        if not rider:
            print("Error: No rider found for this user")
            return redirect(url_for('rider_dashboard'))

        rider_id = rider['rider_id']
        session['rider_id'] = rider_id  # Store rider_id in session

        print(f"Fetched Rider ID: {rider_id}")  # Debugging print

        # Insert into assignrider table
        cursor.execute("""
            INSERT INTO assignrider (rider_id, order_id, delivery_status)
            VALUES (%s, %s, 'Assigned')
        """, (rider_id, order_id))

        # Update order status to "Out For Delivery"
        cursor.execute("""
            UPDATE orders SET order_status = 'Out For Delivery' WHERE order_id = %s
        """, (order_id,))

        connection.commit()
        print("Order successfully assigned and updated!")

    except Exception as e:
        print(f"Error inserting order assignment: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('rider_dashboard'))

#rider delivery
@app.route('/rider_dashboard/deliveries' , methods=['GET'])
def rider_deliveries():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    print(session['id'])
    
    try:
        print(f"Session Data Before Fetch: {session}")  # Debugging

        # Get rider details from the database
        cursor.execute("SELECT * FROM riders WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        if user:
            session['rider_id'] = user['rider_id']  # Store in session
            print(f"Rider ID Set in Session: {session['rider_id']}")
            Fname = user['Fname']
           
            profile_pic =user['profile_pic']

        cursor.execute("""
            SELECT DISTINCT
                o.order_id, 
                CONCAT(b.Fname, ' ', b.Mname, ' ', b.Lname) AS fullname, 
                CONCAT(ab.houseNo, ' ', ab.street, ' ', ab.barangay, ' ', ab.city, ' ', ab.Province) AS Fulladdress,
                o.total_price,
                b.mobile_number
            FROM orders o
            JOIN buyers b ON o.buyer_id = b.buyer_id
            JOIN addresses_buyer ab ON b.buyer_id = ab.buyer_id
            JOIN assignrider ar ON o.order_id = ar.order_id
            WHERE ar.delivery_status = 'Assigned' 
            AND ar.rider_id = %s
        """, (session['rider_id'],))  
        order_data = cursor.fetchall()
        order_count = len(order_data)

    except Exception as e:
        print(f"Error fetching user details: {e}")
        order_data = []  # Return empty data on error

    finally:
        cursor.close()
        connection.close()

    return render_template('Rider-page/my-deliveries.html', order_data=order_data,Fname = Fname, profile_pic= profile_pic,order_count =order_count ) 

    
@app.route('/rider-delivered', methods=['POST'])
def rider_delivered():
    print(f"Session Data: {session}")  # Debugging print

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        order_id = request.form.get('order_id')  
        user_id = session.get('id')  # Get user_id from session

        print(f"Received Order ID: {order_id}")  # Debugging print
        print(f"Session User ID: {user_id}")  # Debugging print

        if not user_id:
            print("Error: No user_id in session")
            return redirect(url_for('rider_dashboard'))

        # Fetch rider_id based on session user_id
        cursor.execute("SELECT rider_id FROM riders WHERE user_id = %s", (user_id,))
        rider = cursor.fetchone()

        if not rider:
            print("Error: No rider found for this user")
            return redirect(url_for('rider_dashboard'))

        rider_id = rider['rider_id']
        session['rider_id'] = rider_id  # Store rider_id in session

        print(f"Fetched Rider ID: {rider_id}")  # Debugging print

        # Insert into assignrider table
        cursor.execute("""
            UPDATE  assignrider  SET delivery_status = 'Completed' WHERE rider_id =%s AND order_id = %s
        """, (rider_id, order_id))     
           

        # Update order status to "Out For Delivery"
        # cursor.execute("""
        #     UPDATE orders SET order_status = 'Completed' WHERE order_id = %s
        # """, (order_id,))

        connection.commit()
        print("Order successfully assigned and updated!")

    except Exception as e:
        print(f"Error inserting order assignment: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('rider_dashboard')) 
@app.route('/rider_dashboard/deliveredCompleted' , methods=['GET'])
def rider_deliveredCompleted():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    print(session['id'])
    
    try:
        print(f"Session Data Before Fetch: {session}")  # Debugging

        # Get rider details from the database
        cursor.execute("SELECT * FROM riders WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        if user:
            session['rider_id'] = user['rider_id']  # Store in session
            print(f"Rider ID Set in Session: {session['rider_id']}")
            Fname = user['Fname']
           
            profile_pic =user['profile_pic']

        cursor.execute("""
            SELECT 
                orders.order_id, 
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname, 
                CONCAT(addresses_buyer.houseNo, ' ', addresses_buyer.street, ' ', 
                    addresses_buyer.barangay, ' ', addresses_buyer.city, ' ', 
                    addresses_buyer.Province) AS Fulladdress,
                orders.total_price,
                buyers.mobile_number,
                orders.updated_at
            FROM orders
            JOIN buyers ON orders.buyer_id = buyers.buyer_id
            JOIN addresses_buyer ON buyers.buyer_id = addresses_buyer.buyer_id
            JOIN assignrider ON orders.order_id = assignrider.order_id
            WHERE orders.order_status = 'Completed' 
            AND assignrider.rider_id = %s
        """, (session['rider_id'],))  
        order_data = cursor.fetchall()
        order_count = len(order_data)

    except Exception as e:
        print(f"Error fetching user details: {e}")
        order_data = []  # Return empty data on error

    finally:
        cursor.close()
        connection.close()

    return render_template('Rider-page/completed.html', order_data=order_data,Fname = Fname, profile_pic= profile_pic,order_count =order_count )
@app.route('/Rider/rider-filtered', methods=['GET'])
def rider_filtered():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Debug print session id
    print(f"Session ID: {session.get('id')}")

    # Get date range from query params or default to last 30 days
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date:
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.today().strftime('%Y-%m-%d')

    try:
        print(f"Session Data Before Fetch: {session}")  # Debugging

        # Get rider info based on user_id in session
        cursor.execute("SELECT * FROM riders WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        if not user:
            # Handle missing rider
            return "Rider not found", 404

        session['rider_id'] = user['rider_id']  # Store rider_id in session
        print(f"Rider ID Set in Session: {session['rider_id']}")

        Fname = user['Fname']
        profile_pic = user['profile_pic']

        # Fetch completed orders assigned to this rider within date range
        cursor.execute("""
            SELECT 
                orders.order_id, 
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname, 
                CONCAT(addresses_buyer.houseNo, ' ', addresses_buyer.street, ' ', 
                    addresses_buyer.barangay, ' ', addresses_buyer.city, ' ', 
                    addresses_buyer.Province) AS Fulladdress,
                orders.total_price,
                buyers.mobile_number,
                orders.updated_at
            FROM orders
            JOIN buyers ON orders.buyer_id = buyers.buyer_id
            JOIN addresses_buyer ON buyers.buyer_id = addresses_buyer.buyer_id
            JOIN assignrider ON orders.order_id = assignrider.order_id
            WHERE orders.order_status = 'Completed' 
              AND assignrider.rider_id = %s
              AND orders.updated_at BETWEEN %s AND %s
            ORDER BY orders.updated_at DESC
        """, (session['rider_id'], start_date, end_date))

        order_data = cursor.fetchall()
        order_count = len(order_data)

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'Rider-page/completed.html',
        order_data=order_data,
        Fname=Fname,
        profile_pic=profile_pic,
        order_count=order_count
    )




@app.route('/rider_dashboard/rider_profile')
def rider_profileWeb():
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT * 
            FROM addresses_rider 
            JOIN riders ON addresses_rider.rider_id = riders.rider_id 
            WHERE riders.user_id =  %s;
        """, (session['id'],))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['user_id']  
            Fname = user['Fname']
            Mname = user['Mname']
            Lname = user['Lname']
            gender = user['gender']
            profile_pic =user['profile_pic']
            houseNo = user['houseNo']
            street = user['street']
            barangay = user['barangay']
            city = user['city']
            Province = user['Province']
            postal_code = user['postal_code']
            email = user['email']
            contact_num = user['mobile_number']
            birthday = user['birthdate']

    except Exception as e:
        print(f"Error: {str(e)}")
        # Handle error as needed

    finally:
        cursor.close()
        connection.close()

    # Pass all the fetched variables to the template
    return render_template(
        'Rider-page/rider_profile.html',
       
        Fname=Fname, Mname=Mname, Lname=Lname,
        houseNo=houseNo, street=street, barangay=barangay, city=city, Province=Province, postal_code=postal_code, 
        email=email, contact_num=contact_num, gender = gender, birthday= birthday,profile_pic = profile_pic,username= Fname
    )

@app.route('/search-parcel')
def search_parcel():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    search = request.args.get('search', '').strip()
    if not search:  
        return redirect(url_for('rider_dashboard'))

    cursor.execute("SELECT * FROM riders WHERE user_id = %s", (session['id'],))
    user = cursor.fetchone()

    if user:
        session['rider_id'] = user['rider_id']
        print(f"Rider ID Set in Session: {session['rider_id']}")
        Fname = user['Fname']
        profile_pic = user['profile_pic']
    else:
        Fname = ''
        profile_pic = ''

    cursor.execute(
        """SELECT 
                orders.order_id, 
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname, 
                CONCAT(addresses_buyer.houseNo, ' ', addresses_buyer.street, ' ', 
                       addresses_buyer.barangay, ' ', addresses_buyer.city, ' ', 
                       addresses_buyer.Province) AS Fulladdress
           FROM orders
           JOIN buyers ON orders.buyer_id = buyers.buyer_id
           JOIN addresses_buyer ON buyers.buyer_id = addresses_buyer.buyer_id
           WHERE orders.order_status = 'Shipped' 
           AND (addresses_buyer.Province LIKE %s
                OR addresses_buyer.city LIKE %s
                );""", 
        ('%' + search + '%', '%' + search + '%')
    )

    order_data = cursor.fetchall()
    order_count = len(order_data)
    return render_template('Rider-page/dashboard.html', order_data=order_data, Fname=Fname, profile_pic=profile_pic,order_count = order_count)

@app.route('/search-parcel/ontheway')
def search_parcelOTW():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    search = request.args.get('search', '').strip()
    if not search:  
        return redirect(url_for('rider_dashboard'))

    cursor.execute("SELECT * FROM riders WHERE user_id = %s", (session['id'],))
    user = cursor.fetchone()

    if user:
        session['rider_id'] = user['rider_id']
        print(f"Rider ID Set in Session: {session['rider_id']}")
        Fname = user['Fname']
        profile_pic = user['profile_pic']
    else:
        Fname = ''
        profile_pic = ''

    cursor.execute(
        """ SELECT 
                orders.order_id, 
                CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname, 
                CONCAT(addresses_buyer.houseNo, ' ', addresses_buyer.street, ' ', 
                    addresses_buyer.barangay, ' ', addresses_buyer.city, ' ', 
                    addresses_buyer.Province) AS Fulladdress,
                orders.total_price,
                buyers.mobile_number
            FROM orders
            JOIN buyers ON orders.buyer_id = buyers.buyer_id
            JOIN addresses_buyer ON buyers.buyer_id = addresses_buyer.buyer_id
            JOIN assignrider ON orders.order_id = assignrider.order_id
            WHERE orders.order_status = 'Out For Delivery' 
            AND assignrider.rider_id = %s
           AND (addresses_buyer.Province LIKE %s
                OR addresses_buyer.city LIKE %s
                OR addresses_buyer.barangay LIKE %s);""", 
        (session['rider_id'],'%' + search + '%', '%' + search + '%', '%' + search + '%')
    )

    order_data = cursor.fetchall()
    order_count = len(order_data)
    return render_template('Rider-page/my-deliveries.html', order_data=order_data, Fname=Fname, profile_pic=profile_pic,order_count = order_count)




#==============================================================================
#create account rider
@app.route('/createRiderFormpost', methods=['POST'])
def createRiderFormpost():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    provided_password = request.form.get('password') 
    provided_email = request.form.get('email')        

    
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (provided_email,))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        connection.close()
       
        return redirect(url_for('createAccountRider', error="Email already registered."))
    cursor.close()
    connection.close()

    #print(provided_email)
    return render_template('Login-page/LoginPage-riderForm.html', email1=provided_email, password1=provided_password)

@app.route('/registerRider', methods=['POST'])
def registerRider():
    # Set default profile pic path (or binary data depending on your approach)
    default_pic = get_default_profile_pic()
    
    # Fetch form data
    provided_email = request.form['email1']
    hashed_password = generate_password_hash(request.form['password'])
    
    Fname = request.form['fname']
    Mname = request.form['Mname']
    Lname = request.form['Lname']
    mobile_number = request.form['number']
    gender = request.form['gender']
    birthdate = f"{request.form['year']}-{request.form['month']}-{request.form['day']}"
    
    # Handle the valid ID image upload
    image = request.files.get('valid_id')
    valid_id_filename = None
    if image and allowed_file(image.filename):
        valid_id_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], valid_id_filename))
    
    # Handle profile picture upload or use default
    profile_image = "profile-icon-design-free-vector.jpg"
   
    
    # Address details
    houseNo = request.form['houseNo']
    street = request.form['street']
    barangay = request.form['barangay']
    city = request.form['city']
    Province = request.form['Province']
    postal = request.form['postal']

    barangay_name = get_location_name(barangay, 'barangay')
    city_name = get_location_name(city, 'municipality')
    province_name = get_location_name(Province, 'province')

    print(barangay_name)
    print(city_name)
    print(province_name)
    
    # Database connection
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Insert into users table
        query_user = "INSERT INTO users (email, password, role_id) VALUES (%s, %s, %s)"
        cursor.execute(query_user, (provided_email, hashed_password, 4))
        user_id = cursor.lastrowid
        
        # Insert into buyers table
        buyer_query = """
        INSERT INTO riders (user_id, email, Fname, Mname, Lname, mobile_number, gender, birthdate, profile_pic, valid_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(buyer_query, (user_id, provided_email, Fname, Mname, Lname, mobile_number, gender, birthdate, profile_image, valid_id_filename))
        buyer_id = cursor.lastrowid
        
        # Insert into addresses_buyer table
        address_query = """
        INSERT INTO addresses_rider (rider_id, houseNo, street, barangay, city, Province, postal_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(address_query, (buyer_id, houseNo, street, barangay_name, city_name, province_name, postal))

        connection.commit()
        return redirect(url_for('login', error="Registered successfully, Waiting for Admin approval!"))

    except Exception as err:
        # Rollback if any error occurs
        connection.rollback()
        print(f"Error during registration: {err}")
        return redirect(url_for('registerRider', error="An error occurred during registration."))

    finally:
        cursor.close()
        connection.close()



#============================================================================================================================


# Seller

@app.route('/createsellerFormpost', methods=['POST'])
def createsellerFormpost():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    provided_password = request.form.get('password') 
    provided_email = request.form.get('email')        

    
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (provided_email,))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        connection.close()
       
        return redirect(url_for('createAccountSeller', error="Email already registered."))
    cursor.close()
    connection.close()

    #print(provided_email)
    return render_template('Login-page/LoginPage-sellerForm.html', email1=provided_email, password1=provided_password)


@app.route('/registerseller', methods=['POST'])
def registerseller():
    default_pic = get_default_profile_pic()
    
    # #print("Default profile picture set:", default_pic)

    provided_email = request.form['email1']
    hashed_password = generate_password_hash(request.form['password'])
    # provided_password = request.form['password']
    Fname = request.form['fname']
    Mname = request.form['Mname']
    Lname = request.form['Lname']
    mobile_number = request.form['number']
    gender = request.form['gender']
    shopname = request.form['shopname']
    description = request.form['description']
 
    profile_image = "profile-icon-design-free-vector.jpg"

    


    
    houseNo = request.form['houseNo']
    street = request.form['street']
    barangay = request.form['barangay']
    city = request.form['city']
    Province = request.form['Province']
    postal = request.form['postal']

    barangay_name = get_location_name(barangay, 'barangay')
    city_name = get_location_name(city, 'municipality')
    province_name = get_location_name(Province, 'province')

    print(barangay_name)
    print(city_name)
    print(province_name)

    image = request.files.get('valid_id')
    valid_id_filename = None
    if image and allowed_file(image.filename):
        valid_id_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], valid_id_filename))


    image2 = request.files.get('logo')
    logo = None
    if image2 and allowed_file(image2.filename):
        logo = secure_filename(image2.filename)
        image2.save(os.path.join(app.config['UPLOAD_FOLDER'], logo))
    
    image3 = request.files.get('permit')
    permit = None
    if image3 and allowed_file(image3.filename):
        permit = secure_filename(image3.filename)
        image3.save(os.path.join(app.config['UPLOAD_FOLDER'], permit))
    



    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Insert into users table
        query_user = "INSERT INTO users (email, password, role_id) VALUES (%s, %s, %s)"
        cursor.execute(query_user, (provided_email, hashed_password, 2))
        user_id = cursor.lastrowid
        #print("New user inserted with ID:", user_id)

        # Insert into buyers table
        buyer_query = """
        INSERT INTO sellers (user_id, email, Fname, Mname, Lname, shop_name, mobile_number, gender, profile_pic, shop_description, valid_id, shop_logo, business_permit)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s)
        """
        cursor.execute(buyer_query, (user_id, provided_email, Fname, Mname, Lname, shopname, mobile_number, gender, profile_image, description, valid_id_filename, logo, permit))
        seller_id = cursor.lastrowid
        #print("New buyer inserted with ID:", seller_id)

        # Insert into addresses table
        address_query = """
        INSERT INTO addresses_seller (seller_id, houseNo, street, barangay, city, Province, postal_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(address_query, (seller_id, houseNo, street, barangay_name, city_name, province_name, postal))
        #print("Address inserted for seller ID:", seller_id)

        connection.commit()
        #print("Transaction committed successfully.")
        return redirect(url_for('login', error="Registered successfully, Waiting for Admin approval!"))

    except Exception as err:
        connection.rollback()
        #print("Error occurred:", err)
        return redirect(url_for('registerseller', error="An error occurred during registration."))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")
 


    



#seller_dashboard
#username and pic
def sellerinfo():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""SELECT *
            FROM addresses_seller
            JOIN sellers ON addresses_seller.seller_id = sellers.seller_id
            WHERE sellers.user_id = %s;
        """, (session['id'],))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['user_id']  
            Fname = user['Fname'] 
            Mname = user['Mname'] 
            Lname = user['Lname']
            description =user['shop_description'] 
            houseNo = user['houseNo'] 
            street = user['street'] 
            barangay = user['barangay'] 
            city = user['city'] 
            Province = user['Province'] 
            postal_code = user['postal_code'] 
            email =  user['email']
            contact_num = user['mobile_number']
        else:  
            Fname = ''
            Mname =  ''
            Lname =  ''
            
            
            houseNo =  ''
            street =  ''
            barangay =  ''
            city =  ''
            Province =  ''
            postal_code =  ''
            email =   ''
           
            contact_num =  ''
           
            description = ''

    finally:
        cursor.close()
        connection.close()
    return Fname, Mname, Lname, email, contact_num, houseNo, street, barangay, city, Province, postal_code, description


def sellerid():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        
        if user:
            profile_pic = user['shop_logo']
            username = user['Fname']

    finally:
        cursor.close()
        connection.close()

   
    return username, profile_pic



@app.route('/seller_dashboard')
def seller_dashboard():
    username, profile_pic = sellerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT seller_id FROM sellers
                          JOIN users ON users.user_id = sellers.user_id
                          WHERE sellers.user_id = %s;""", (session['id'],))
        seller_data = cursor.fetchone()
        if seller_data:
            seller_id = seller_data['seller_id']
            session['seller_id'] = seller_data['seller_id']
        else:
            seller_id = None
            session['seller_id'] = None

        if seller_id:
            # Fetch all completed orders for the seller
            cursor.execute("""SELECT total_price FROM orders 
                              WHERE order_status = 'Completed' AND seller_id = %s""", (seller_id,))
            orders = cursor.fetchall()

            # Get the top 3 selling products for the seller
            cursor.execute("""
                SELECT products.ID, products.product_name, SUM(orders.quantity) AS total_sold, products.Image
                FROM orders
                JOIN products ON products.Id = orders.product_id
                WHERE orders.order_status = 'Completed' AND orders.seller_id = %s
                GROUP BY products.ID
                ORDER BY total_sold DESC
                LIMIT 3;
            """, (seller_id,))
            top_products = cursor.fetchall()
        else:
            orders = []
            top_products = []

    finally:
        cursor.close()
        connection.close()

    # Calculate total sales and order count
    sales = sum(order['total_price'] for order in orders)
    order_count = len(orders)
    #print(sales)
    #print(order_count)

    return render_template('Seller-page/dashboard.html', username=username, profile_pic=profile_pic,
                           sales=sales, order_count=order_count, top_products=top_products)


@app.route('/seller-page/products', methods=['GET'])
def sellerpage_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()

    try:
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        if user:
            session['seller_id'] = user['seller_id']

            # Pagination setup
            per_page = 30
            current_page = request.args.get('page', 1, type=int)
            offset = (current_page - 1) * per_page

            cursor.execute(
                "SELECT SQL_CALC_FOUND_ROWS * FROM products WHERE Seller_Id = %s LIMIT %s OFFSET %s",
                (session['seller_id'], per_page, offset),
            )
            products = cursor.fetchall()
            for product in products:
                product_id = product['Id']

                # Calculate total sold quantity
                cursor.execute("""
                    SELECT SUM(orders.quantity) AS total_sold
                    FROM orders
                    WHERE orders.order_status = 'Completed'
                    AND orders.product_id = %s;
                """, (product_id,))
                sold = cursor.fetchone()
                product['total_sold'] = sold['total_sold'] if sold and sold['total_sold'] else 0

                # Calculate average rating
                cursor.execute("""
                    SELECT ROUND(AVG(rate), 1) AS average_rate
                    FROM rating
                    WHERE product_id = %s;
                """, (product_id,))
                rate = cursor.fetchone()
                product['Rating'] = rate['average_rate'] if rate and rate['average_rate'] else 0

            # Get total number of rows for pagination
            cursor.execute("SELECT FOUND_ROWS() AS total;")
            total = cursor.fetchone()['total']

            total_pages = (total + per_page - 1) // per_page
        else:
            products = []
            total_pages = 0
            current_page = 1
    finally:
        cursor.close()
        connection.close()

    return render_template(
        'Seller-page/products.html',
        products=products,
        username=username,
        profile_pic=profile_pic,
        current_page=current_page,
        total_pages=total_pages,
    )
#search seller 
@app.route('/search-seller' )
def search_seller():
    username, profile_pic = sellerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = buyerid()
    search = request.args.get('search', '').strip()
    #print("ni search",search)

    if not search:  
        return redirect(url_for('buyer_dashboard'))  # Replace 'homepage' with your actual homepage route

    cursor.execute(
        "SELECT * FROM products WHERE Product_Name LIKE %s AND Seller_Id = %s", 
        ('%' + search + '%', session['seller_id'])
    )
    products = cursor.fetchall()


    return render_template('Seller-page/search.html', products=products , username= username, profile_pic = profile_pic, search=search)


@app.route('/seller-page-item/products/<int:product_id>', methods=['POST', 'GET'])
def sellerpage_products_item(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()
    seller_logo,product_name, description, price, product_pic, sellerpic, sellershopname, product_id = product_description(product_id)
    variations = get_product_variations(product_id)
    
    cursor.execute("SELECT Seller_Id FROM products WHERE Id = %s", (product_id,))
    row = cursor.fetchone()
    seller_id = int(row['Seller_Id']) if row else None

    error = request.args.get('error')  # Get error from URL parameters if any

    return render_template('Seller-page/product-edit.html', username=username,
                           profile_pic=profile_pic,
                           productName=product_name,
                           description=description,
                           price=price,
                           productpic=product_pic,
                           sellerpic=sellerpic,
                           sellershopname=sellershopname,
                           product_id=product_id,
                           variations=variations,
                           seller_id=seller_id,
                           error=error)


@app.route('/seller-page-item/products-delete', methods=['POST'])
def sellerpage_products_item_delete():
    
    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller_id')
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # First, delete from `cart_items` where `product_id` matches
    cursor.execute("DELETE FROM cart_items WHERE product_id = %s", (product_id,))
    connection.commit()
    
    # Then delete from `products` where `Id` and `Seller_Id` match
    cursor.execute("DELETE FROM products WHERE Seller_Id = %s AND Id = %s", (seller_id, product_id))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    #print(seller_id, product_id)
    return redirect(url_for('sellerpage_products', product_id=product_id, error="Product deleted"))

@app.route('/seller-page-item/products-update', methods=['POST','GET'])
def sellerpage_products_item_update():
    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller_id')

    username, profile_pic = sellerid()
    connection = get_db_connection()
    cursor = connection.cursor()
    seller_logo,product_name, description, price, product_pic, sellerpic, sellershopname, product_id = product_description(product_id)
    
   
   
    return render_template('Seller-page/update-form-product.html',username = username,profile_pic =profile_pic,
                           productName=product_name,
                           description=description,
                           price=price,
                           productpic=product_pic,
                           sellerpic=sellerpic,
                           sellershopname=sellershopname,
                           product_id=product_id,
                          
                           seller_id=seller_id,
                          )


@app.route('/seller-page-item/products-update-product', methods=['POST'])
def sellerpage_products_item_update_product_image():

    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller_id')
    connection = get_db_connection()
    cursor = connection.cursor()
    
    
    try:
            # Fetch the seller's current logo
            cursor.execute("SELECT Image FROM products WHERE Id = %s", (product_id,))
            user = cursor.fetchone()

            if user:
                #print("Files received:", request.files)
                # Check if an image was uploaded
                image3 = request.files.get('image')
                image = None
                if image3 and allowed_file(image3.filename):
                    image = secure_filename(image3.filename)
                    image3.save(os.path.join(app.config['UPLOAD_FOLDER'], image))

                # Update the logo in the database (storing binary data)
                cursor.execute("""
                    UPDATE products
                    SET Image = %s 
                    WHERE Id = %s
                """, (image, product_id))
                connection.commit()

                # Success message
                return redirect(url_for('sellerpage_products', error="Product pic updated successfully"))

    except Exception as e:
        connection.rollback()
        return redirect(url_for('sellerpage_products', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
    
@app.route('/seller-page-item/products-update-detais', methods=['POST'])
def sellerpage_products_item_update_product_detais():
    # Get product_id and seller_id from the form
    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller_id')
    #print(f"Received product_id: {product_id}, seller_id: {seller_id}")

    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Get the submitted form data
        product_name = request.form['product-name']
        price = request.form['price']
        description = request.form['description']
        category = request.form['category']
        #print(f"Received product data: Name: {product_name}, Price: {price}, Description: {description}, Category: {category}")

        # Update the product information in the database
        cursor.execute("""
            UPDATE products 
            SET Product_Name = %s, Price = %s, Description = %s, category = %s
            WHERE Id = %s
        """, (product_name, price, description, category, product_id))
        #print("SQL Update executed")

        # Commit the transaction
        connection.commit()
        #print("Transaction committed successfully")

        # Success message
        return redirect(url_for('sellerpage_products', success="Product information updated successfully"))

    except Exception as e:
        # Rollback if there's an error
        connection.rollback()
        #print(f"Error: {str(e)}")
        return redirect(url_for('sellerpage_products', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")





#===============addproduct===================================================================
@app.route('/seller/add-product', methods=['GET', 'POST'])
def upload_product():
    username, profile_pic = sellerid() 
    if request.method == 'POST':
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Fetch seller ID
            cursor.execute("SELECT seller_id FROM sellers WHERE user_id = %s", (session['id'],))
            user = cursor.fetchone()

            image3 = request.files.get('image')
            image = None
            if image3 and allowed_file(image3.filename):
                image = secure_filename(image3.filename)
                image3.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
    

            product_name = request.form['product-name']
            price = request.form['price']
            description = request.form['description']
            seller_id = session.get('seller_id')
            category = request.form['category']
            
            # Insert product information
            query = """INSERT INTO products (Product_Name, Description, Price, Stock_Quantity, Status, Seller_Id, Image, category)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(query, (product_name, description, price, 10, 'active', seller_id, image , category))
            connection.commit()
            product_id = cursor.lastrowid

            # Insert variations
            colors = request.form.getlist('variation_color[]')
            sizes = request.form.getlist('variation_size[]')
            variation_types = request.form.getlist('variation_type[]')
            
            for i in range(len(variation_types)):
                color = colors[i] if i < len(colors) else None
                size = sizes[i] if i < len(sizes) else None
                
                # Determine stock based on the inputs
                stock = 10  # Default stock quantity
                
                if variation_types[i] == 'color_size':
                    # Both color and size
                    query_variation = """INSERT INTO productvariations (product_id, color, size, stock, price)
                                         VALUES (%s, %s, %s, %s, %s)"""
                    cursor.execute(query_variation, (product_id, color, size, stock, price))
                elif variation_types[i] == 'color_only':
                    # Color only
                    query_variation = """INSERT INTO productvariations (product_id, color, size, stock, price)
                                         VALUES (%s, %s, NULL, %s, %s)"""
                    cursor.execute(query_variation, (product_id, color, stock, price))
                elif variation_types[i] == 'size_only':
                    # Size only
                    query_variation = """INSERT INTO productvariations (product_id, color, size, stock, price)
                                         VALUES (%s, NULL, %s, %s, %s)"""
                    cursor.execute(query_variation, (product_id, size, stock, price))

                    
            
            connection.commit()
            return redirect(url_for('sellerpage_products', error="Product added successfully"))
        
        except mysql.connector.Error as err:
            connection.rollback()
            return f"Database error: {err}"
        
        finally:
            cursor.close()
            connection.close()
    else:
        return render_template('Seller-page/add-product.html', username=username, profile_pic=profile_pic)

# =========================================================update stocks===============================================================
@app.route('/seller/update-stock', methods=['GET', 'POST'])
def update_stocks():
    username, profile_pic = sellerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    products = []
    total_pages = 0
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of products per page

    try:
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()
        if user:
            session['seller_id'] = user['seller_id']

            # Check for search query
            search_query = request.args.get('search', '')

            if search_query:
                # Filter products based on search query
                cursor.execute(
                    """SELECT COUNT(*) AS total FROM products 
                       WHERE Seller_Id = %s AND Product_Name LIKE %s""",
                    (session['seller_id'], f"%{search_query}%")
                )
            else:
                # Fetch total product count without filtering
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM products WHERE Seller_Id = %s",
                    (session['seller_id'],)
                )

            total_products = cursor.fetchone()['total']
            total_pages = (total_products + per_page - 1) // per_page

            if search_query:
                cursor.execute(
                    """SELECT * FROM products 
                       WHERE Seller_Id = %s AND Product_Name LIKE %s 
                       LIMIT %s OFFSET %s""",
                    (session['seller_id'], f"%{search_query}%", per_page, (page - 1) * per_page)
                )
            else:
                cursor.execute(
                    "SELECT * FROM products WHERE Seller_Id = %s LIMIT %s OFFSET %s",
                    (session['seller_id'], per_page, (page - 1) * per_page)
                )

            products = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    return render_template(
        'Seller-page/stocks.html',
        products=products,
        username=username,
        profile_pic=profile_pic,
        current_page=page,
        total_pages=total_pages
    )



@app.route('/seller-page-item/stocks/<int:product_id>', methods=['POST', 'GET'])
def sellerpage_products_stocks(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()
    seller_logo,product_name, description, price, product_pic, sellerpic, sellershopname, product_id = product_description(product_id)
    variations = variation_stocks(product_id)
    print("variation",variations)
    
    cursor.execute("SELECT Seller_Id FROM products WHERE Id = %s", (product_id,))
    row = cursor.fetchone()
    seller_id = int(row['Seller_Id']) if row else None

    error = request.args.get('error')  # Get error from URL parameters if any
    cursor.execute("SELECT Stock_Quantity FROM products WHERE Id = %s", (product_id,))
    quantity = cursor.fetchone()
    Stock_Quantity = int(quantity['Stock_Quantity'])


    return render_template('seller-page/stocks-view-all.html', username=username,
                           profile_pic=profile_pic,Stock_Quantity = Stock_Quantity,
                           productName=product_name,
                           description=description,
                           price=price,
                           productpic=product_pic,
                           sellerpic=sellerpic,
                           sellershopname=sellershopname,
                           product_id=product_id,
                           variations=variations,
                           seller_id=seller_id,
                           error=error)


@app.route('/seller/stock-management/<int:product_id>',methods=['POST'])
def seller_stock_management(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    stocks = request.form['quantity']
    try:
        cursor.execute("""
            UPDATE products
            SET stock_quantity = stock_quantity + %s
            WHERE id = %s
        """, (stocks, product_id))
        connection.commit()
        return redirect(url_for('sellerpage_products_stocks', product_id=product_id))
    except Exception as e:
        connection.rollback()
        return redirect(url_for('sellerpage_products_stocks', product_id=product_id))

    finally:
        cursor.close()
        connection.close()

@app.route('/seller/stock-variation-management/<int:product_id>', methods=['POST'])
def seller_stock_management_varation(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    stocks = request.form.get('quantity')
    size = request.form.get('size').strip()
    print("Stocks:", stocks)
    print("Size:", size)
    print("Product ID:", product_id)

    if not stocks or not size:
        print("Missing quantity or size.")
        return redirect(url_for('sellerpage_products_stocks', product_id=product_id))

    try:
        cursor.execute("""
            UPDATE ProductVariations
            SET stock = %s 
            WHERE product_id = %s AND size = %s;
        """, (stocks, product_id, size))
        connection.commit()

        if cursor.rowcount == 0:
            print(f"No rows updated. Check product_id={product_id} and size={size}.")
        else:
            print(f"Stock updated successfully for product ID {product_id}, size {size}, stocks {stocks}.")

    except Exception as e:
        connection.rollback()
        print(f"Error updating stock: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('sellerpage_products_stocks', product_id=product_id))

    



# ====================================================================================================================================
#seller ipdate profile
@app.route('/seller/update-profile', methods=['GET', 'POST'])
def update_profile():
    Fname, Mname, Lname, email, contact_num, houseNo, street, barangay, city, Province, postal_code, description =sellerinfo()

    username, profile_pic = sellerid()
    return render_template('Seller-page/seller-profile-form.html',username= username, profile_pic = profile_pic, Fname = Fname, Mname=Mname, Lname=Lname, houseNo=houseNo,
                            street=street, barangay = barangay, city=city, Province=Province, 
                            postal_code =postal_code, email= email,  contact_num = contact_num,
                             description = description
                               )

@app.route('/seller/update-logo', methods=['POST'])
def update_logo():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Fetch the seller's current logo
        cursor.execute("SELECT shop_logo FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()

        if user:
            #print("Files received:", request.files)
            # Check if an image was uploaded
            image = request.files.get('image')
            image_data = None
            if image and allowed_file(image.filename):
                image_data = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_data))
                    # Convert the image to binary format
                    

            # Update the logo in the database (storing binary data)
            cursor.execute("""
                UPDATE sellers
                SET shop_logo = %s 
                WHERE user_id = %s
            """, (image_data, session['id']))
            connection.commit()

            # Success message
            return redirect(url_for('update_profile', error="Logo updated successfully"))

    except Exception as e:
        connection.rollback()
        return redirect(url_for('update_profile', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()


@app.route('/seller/account-information', methods=['POST'])
def update_account_information_emailpass():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get the email and password from the form
        email = request.form['email']
        password = request.form['password']
        
        #print(f"Received email: {email}, password: {'<hidden>' if password else 'None'}")

        # Hash the password if it's not empty
        if password:
            hashed_password = generate_password_hash(password)
            #print(f"Hashed password: {hashed_password}")
            
            # Update the seller's email (if needed)
            cursor.execute("""
                UPDATE sellers 
                SET email = %s
                WHERE user_id = %s
            """, (email, session['id']))
            
            # Update the user's email and password
            cursor.execute("""
                UPDATE users 
                SET email = %s, password = %s
                WHERE user_id = %s
            """, (email, hashed_password, session['id']))
            #print(f"Update query executed for user_id: {session['id']}")
        else:
            # Update the seller's email (if needed)
            cursor.execute("""
                UPDATE sellers 
                SET email = %s
                WHERE user_id = %s
            """, (email, session['id']))
            
            # Update only the user's email if no password change
            cursor.execute("""
                UPDATE users 
                SET email = %s
                WHERE user_id = %s
            """, (email, session['id']))
            #print(f"Email updated for user_id: {session['id']}")

        connection.commit()
        return redirect(url_for('update_profile', success="Account updated successfully"))

    except Exception as e:
        connection.rollback()
        #print(f"Error: {str(e)}")
        return redirect(url_for('update_profile', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")


@app.route('/seller/update-account', methods=['POST'])
def update_account_information():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get the submitted form data (without email and password)
        fname = request.form['Fname']
        lname = request.form['Lname']
        mname = request.form['Mname']
        contact_num = request.form['number']
        gender = request.form['gender']

        # Update the user account information in the database (excluding email and password)
        cursor.execute("""
            UPDATE sellers 
            SET Fname = %s, Lname = %s, Mname = %s, mobile_number = %s, gender = %s
            WHERE user_id = %s
        """, (fname, lname, mname, contact_num, gender, session['id']))

        # Commit the transaction
        connection.commit()

        # Success message
        return redirect(url_for('update_profile', success="Account information updated successfully"))

    except Exception as e:
        # Rollback if there's an error
        connection.rollback()
        #print(f"Error: {str(e)}")
        return redirect(url_for('update_profile', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")


@app.route('/seller/update-address', methods=['POST'])
def update_address():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get the address data from the form
        house_no = request.form['houseNo']
        street = request.form['street']
        barangay = request.form['barangay']
        city = request.form['city']
        province = request.form['Province']
        postal_code = request.form['postal']
        #print(session['seller_id'])
        # Update the address in the database using seller_id
        cursor.execute("""
            UPDATE addresses_seller
            SET houseNo = %s, street = %s, barangay = %s, city = %s, Province = %s, postal_code = %s
            WHERE seller_id = %s
        """, (house_no, street, barangay, city, province, postal_code, session['seller_id']))

        # Commit the transaction
        connection.commit()

        # Success message
        return redirect(url_for('update_profile', success="Address updated successfully"))

    except Exception as e:
        # Rollback if there's an error
        connection.rollback()
        #print(f"Error: {str(e)}")
        return redirect(url_for('update_profile', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")
@app.route('/seller/update-description', methods=['POST'])
def update_shop_description():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get the new shop description from the form
        description = request.form['description']

        # Update the shop description in the database
        cursor.execute("""
            UPDATE sellers 
            SET shop_description = %s 
            WHERE seller_id = %s
        """, (description, session['seller_id']))

        # Commit the transaction
        connection.commit()

        # Success message
        return redirect(url_for('update_profile', success="Shop description updated successfully"))

    except Exception as e:
        # Rollback if there's an error
        connection.rollback()
        #print(f"Error: {str(e)}")
        return redirect(url_for('update_profile', error=f"Error: {str(e)}"))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")

    

# =======================================seller orders ======================================================================
@app.route('/seller/orders', methods=['GET', 'POST'])
def orders():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()
    
    try:
        # Get seller info based on user session ID
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()
        if user:
            session['seller_id'] = user['seller_id']
            
            # Dynamically filter based on seller_id from session
            cursor.execute("""
                SELECT orders.*, 
                       users.email,
                       buyers.profile_pic,
                       products.Image,
                       products.Product_Name
                    
                FROM orders
                JOIN products ON orders.product_id = products.Id
                JOIN buyers ON orders.buyer_id = buyers.buyer_id
                JOIN users ON buyers.user_id = users.user_id
                WHERE products.Seller_Id = %s;
            """, (session['seller_id'],))  # Using the seller_id from the session
            products = cursor.fetchall()
        else:
            products = []
    finally:
        cursor.close()
        connection.close()

    return render_template('Seller-page/orders/orders.html', products=products, username=username, profile_pic=profile_pic)

#===============================================================update approved=========================================
@app.route('/update_order_status_approved', methods=['POST'])
def update_order_status_approved():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for better readability
    
    order_id = request.form['order_id']

    try:

        # Fetch order details and associated product
        cursor.execute("""
            SELECT * ,products.Stock_Quantity
            FROM orders 
            JOIN products ON products.Id = orders.product_id
            WHERE orders.order_id = %s;
        """, (order_id,))
        result = cursor.fetchall()

        if result:  # Check if any rows are returned
            row = result[0]
            product_id = row.get('product_id')
            Stock_Quantity  = row.get('Stock_Quantity')
            quantity = row.get('quantity', 0)  # Default to 0 if the field is missing
            variation = row.get('variation_id', 'None')  # Default to 'None' if missing
            print(f"Quantity: {quantity}, Variation: {variation}")
        else:
            print(f"No order details found for order_id={order_id}")


        if variation is None or variation == 0:
            if Stock_Quantity is not None and quantity <= Stock_Quantity:
                # Update product stock
                cursor.execute("""
                    UPDATE products
                    SET Stock_Quantity = Stock_Quantity - %s
                    WHERE id = %s;
                """, (quantity, product_id))
                connection.commit()

                # Update the order status
                cursor.execute("""
                    UPDATE orders 
                    SET order_status = 'Approved' 
                    WHERE order_id = %s;
                """, (order_id,))
                connection.commit()
                print(f"Order {order_id} approved, stock decremented by {quantity}.")
            else:
                print(f"Insufficient stock for product ID {product_id}. Requested: {quantity}, Available: {Stock_Quantity}")
                return redirect(url_for('orders', error='Not enough stocks'))
        else:
            if Stock_Quantity is not None and quantity <= Stock_Quantity:
                # Update product stock
                cursor.execute("""
                    UPDATE productvariations
                    SET stock = stock - %s
                    WHERE id = %s;
                """, (quantity, variation))
                connection.commit()

                # Update the order status
                cursor.execute("""
                    UPDATE orders 
                    SET order_status = 'Approved' 
                    WHERE order_id = %s;
                """, (order_id,))
                connection.commit()
                print(f"Order {order_id} approved, stock decremented by {quantity}.")
            else:
                print(f"Insufficient stock for product ID {product_id}. Requested: {quantity}, Available: {Stock_Quantity}")
                return redirect(url_for('orders', error='Not enough stocks'))

    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('orders'))




#==========================================================================================================================
# render to ship
# @app.route('/seller/orders_toship', methods=['GET', 'POST'])
# def toship():
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     username, profile_pic = sellerid()
    
#     try:
#         # Get seller info based on user session ID
#         cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
#         user = cursor.fetchone()
#         if user:
#             session['seller_id'] = user['seller_id']
            
#             # Filter orders where the status is 'Approved'
#             cursor.execute("""
#                 SELECT orders.*, 
#                        users.email,
#                        buyers.profile_pic,
#                        products.Image,
#                        products.Product_Name
#                 FROM orders
#                 JOIN products ON orders.product_id = products.Id
#                 JOIN buyers ON orders.buyer_id = buyers.buyer_id
#                 JOIN users ON buyers.user_id = users.user_id
#                 WHERE products.Seller_Id = %s 
#                   AND orders.order_status = 'Approved';  -- Filtering for Approved orders
#             """, (session['seller_id'],))  # Using the seller_id from the session
#             products = cursor.fetchall()
            
#         else:
#             products = []
#     finally:
#         cursor.close()
#         connection.close()

#     return render_template('Seller-page/orders/toship.html', products=products, username=username, profile_pic=profile_pic)
@app.route('/seller/orders_toship', methods=['GET', 'POST'])
def toship():
    username, profile_pic = sellerid()  # Should not use the same cursor or connection

    connection = get_db_connection()
    try:
        # Get seller ID
        cursor1 = connection.cursor(dictionary=True)
        cursor1.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor1.fetchone()
        cursor1.close()

        if user:
            session['seller_id'] = user['seller_id']

            # Get Approved orders
            cursor2 = connection.cursor(dictionary=True)
            cursor2.execute("""
                SELECT orders.*, 
                       users.email,
                       buyers.profile_pic,
                       products.Image,
                       products.Product_Name
                FROM orders
                JOIN products ON orders.product_id = products.Id
                JOIN buyers ON orders.buyer_id = buyers.buyer_id
                JOIN users ON buyers.user_id = users.user_id
                WHERE products.Seller_Id = %s 
                  AND orders.order_status = 'Approved'
            """, (session['seller_id'],))
            products = cursor2.fetchall()
            cursor2.close()

            # Get riders
            cursor3 = connection.cursor(dictionary=True)
            cursor3.execute("""
                SELECT 
                    r.rider_id,
                    CONCAT(r.Fname, ' ', r.Lname) AS full_name,
                    r.mobile_number,
                    r.profile_pic
                FROM riders AS r
            """)
            rider_rows = cursor3.fetchall()
            cursor3.close()
        else:
            products = []
            rider_rows = []
    finally:
        connection.close()

    return render_template(
        'Seller-page/orders/toship.html',
        products=products,
        username=username,
        profile_pic=profile_pic,
        riders=rider_rows
    )
@app.route('/assign_rider', methods=['POST'])
def assign_rider():
    order_id = request.form.get('order_id')
    rider_id = request.form.get('rider_id')

    if not order_id or not rider_id:
        return jsonify({'error': 'Missing order_id or rider_id'}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)

        # Optional: Check if already assigned (prevent duplicate entry)
        cursor.execute("SELECT * FROM assignrider WHERE order_id = %s", (order_id,))
        existing = cursor.fetchone()

        if existing:
            return jsonify({'error': 'This order is already assigned to a rider.'}), 400

        # Insert the new assignment
        cursor.execute("""
            INSERT INTO assignrider (rider_id, order_id, delivery_status)
            VALUES (%s, %s, 'Assigned')
        """, (rider_id, order_id))
        connection.commit()
        cursor.execute("""
            UPDATE orders SET order_status = 'Shipped' WHERE order_id = %s
        """, (order_id,))
        connection.commit()


        return redirect(url_for('toship', error='Assign succesffuly'))
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

#=======================================================update shipping=============================================================
@app.route('/update_order_status_shipping', methods=['POST'])
def update_order_status_shipping():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    order_id = request.form['order_id']

    try:
        cursor.execute("""
            UPDATE orders 
            SET order_status = 'Shipped' 
            WHERE order_id = %s
        """, (order_id,))
        connection.commit()  
    except Exception as e:
        print(e)  
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('toship'))  
# ============================================================================================================================
# render shiping
@app.route('/seller/orders_shipping', methods=['GET', 'POST'])
def shipping():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()
    
    try:
        # Get seller info based on user session ID
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()
        if user:
            session['seller_id'] = user['seller_id']
            
            # Filter orders where the status is 'Approved'
            cursor.execute("""
                SELECT orders.*, 
                       users.email,
                       buyers.profile_pic,
                       products.Image,
                       products.Product_Name
                FROM orders
                JOIN products ON orders.product_id = products.Id
                JOIN buyers ON orders.buyer_id = buyers.buyer_id
                JOIN users ON buyers.user_id = users.user_id
                WHERE products.Seller_Id = %s 
                  AND orders.order_status = 'Shipped';  -- Filtering for Approved orders
            """, (session['seller_id'],))  # Using the seller_id from the session
            products = cursor.fetchall()
        else:
            products = []
    finally:
        cursor.close()
        connection.close()

    return render_template('Seller-page/orders/shipping.html', products=products, username=username, profile_pic=profile_pic)


# ==================================================================update cancelled========================================================================
@app.route('/update_order_status_cancelled', methods=['POST'])
def update_order_status_cancelled():
    order_id = request.form.get('order_id')
    
    connection = get_db_connection()
    cursor = connection.cursor()
    sellerid = session.get('seller_id')
    cancel_reason = request.form.get('cancel_reason')
    
    try:
        # Insert notification for the buyer
        cursor.execute(
            """
            INSERT INTO notification_buyer (seller_id, cancel_reason, order_id)
            VALUES (%s, %s, %s)
            """,
            (sellerid, cancel_reason, order_id)
        )

        # Update the order status to 'Cancelled'
        cursor.execute(
            "UPDATE orders SET order_status = 'Cancelled' WHERE order_id = %s",
            (order_id,)
        )

        connection.commit()
        cursor.execute("UPDATE orders SET order_status = 'Cancelled' WHERE order_id = %s", (order_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('orders'))  # Redirect back to the to ship orders page

#==================================================================================================================================
# render cancelled
@app.route('/seller/orders_cancelled', methods=['GET', 'POST'])
def cancelled():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()
    
    try:
        # Get seller info based on user session ID
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()
        if user:
            session['seller_id'] = user['seller_id']
            
            # Filter orders where the status is 'Approved'
            cursor.execute("""
                SELECT orders.*, 
                       users.email,
                       buyers.profile_pic,
                       products.Image,
                       products.Product_Name
                FROM orders
                JOIN products ON orders.product_id = products.Id
                JOIN buyers ON orders.buyer_id = buyers.buyer_id
                JOIN users ON buyers.user_id = users.user_id
                WHERE products.Seller_Id = %s 
                  AND orders.order_status = 'Cancelled';  
            """, (session['seller_id'],))  # Using the seller_id from the session
            products = cursor.fetchall()
        else:
            products = []
    finally:
        cursor.close()
        connection.close()

    return render_template('Seller-page/orders/cancellation.html', products=products, username=username, profile_pic=profile_pic)


@app.route('/seller/orders_completed', methods=['GET', 'POST'])
def selelr_completed_order():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()
    
    try:
        # Get seller info based on user session ID
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()
        if user:
            session['seller_id'] = user['seller_id']
            
            # Filter orders where the status is 'Approved'
            cursor.execute("""
                SELECT orders.*, 
                       users.email,
                       buyers.profile_pic,
                       products.Image,
                       products.Product_Name
                FROM orders
                JOIN products ON orders.product_id = products.Id
                JOIN buyers ON orders.buyer_id = buyers.buyer_id
                JOIN users ON buyers.user_id = users.user_id
                WHERE products.Seller_Id = %s 
                  AND orders.order_status = 'Completed';  -- Filtering for Approved orders
            """, (session['seller_id'],))  # Using the seller_id from the session
            products = cursor.fetchall()
        else:
            products = []
    finally:
        cursor.close()
        connection.close()

    return render_template('Seller-page/orders/completed.html', products=products, username=username, profile_pic=profile_pic)







@app.route('/seller/report/<int:buyer_id>', methods=['GET'])
def seller_report(buyer_id):
    username, profile_pic = sellerid()
    seller_id = session['seller_id']
    print(seller_id)
   
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT * ,CONCAT(buyers.Fname, ' ', buyers.Mname, ' ', buyers.Lname) AS fullname,
        CONCAT (addresses_buyer.houseNo,'',addresses_buyer.street,'',addresses_buyer.barangay,'',addresses_buyer.city,'',addresses_buyer.Province) AS address
        FROM buyers 
        JOIN addresses_buyer ON addresses_buyer.buyer_id = buyers.buyer_id
        WHERE buyers.buyer_id = %s""", (buyer_id,))
        buyers =  cursor.fetchone() 
    finally:
        cursor.close()
        connection.close()

    
    return render_template('Seller-page/buyer-profile.html', username=username, profile_pic=profile_pic, buyers=buyers,seller_id =seller_id)

@app.route('/seller/report-message/<int:buyer_id>', methods=['GET'])
def seller_report_message(buyer_id):
    username, profile_pic = sellerid()  # Assume buyerid() returns buyer information
    return render_template('Seller-page/report-message.html', username=username, profile_pic=profile_pic,buyer_id = buyer_id)

@app.route('/seller/report-message', methods=['POST'])
def seller_report_message_form():
    violation_type = request.form.get('violation-type')
    description = request.form.get('description')
    buyer_id = request.form.get('buyer_id')
    seller_id = session['seller_id']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
        
    # Check if an image is uploaded
    image = request.files.get('proof-image')
    proof_image = None
    if image and allowed_file(image.filename):
        proof_image = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], proof_image))


    try:
        # Debugging: #print the query and values
        query = """
            INSERT INTO buyers_reported (buyer_id, seller_id, report_type, description ,reported_image)  
            VALUES (%s, %s, %s, %s,%s)
        """
        values = (buyer_id, seller_id, violation_type, description,proof_image)
        
        cursor.execute(query, values)
        connection.commit()
        #print("Report successfully inserted into the database.")

    except Exception as e:
        connection.rollback()
        #print(f"An error occurred: {e}")
        return redirect(url_for('seller_report',buyer_id = buyer_id, error=str(e)))

    finally:
        cursor.close()
        connection.close()
        #print("Database connection closed.")

    return redirect(url_for('seller_report',buyer_id = buyer_id))


#===========================================================================================================================================

@app.route('/seller/sales', methods=['GET', 'POST'])
def selelr_sales():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()

    try:
        # Get seller info based on user session ID
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()
        if user:
            session['seller_id'] = user['seller_id']
            
            # Filter orders where the status is 'Approved'
            cursor.execute("""
               SELECT product_id, SUM(quantity) AS total_quantity,SUM(total_price) AS totalprice, 
                products.Product_Name, products.Image, products.Price,MAX(orders.updated_at) AS last_updated_at
            FROM orders
            JOIN products ON orders.product_id =products.Id

            WHERE  orders.seller_id =%s  AND orders.order_status="Completed"
            GROUP BY products.Id;
                    """, (session['seller_id'],))  # Using the seller_id from the session
            products = cursor.fetchall()

            cursor.execute("""SELECT total_price FROM orders 
                              WHERE order_status = 'Completed' AND seller_id = %s""", (session['seller_id'],))
            orders = cursor.fetchall()

        


        else:
            products = []
    finally:
        cursor.close()
        connection.close()
    total_sales = sum(product['totalprice'] for product in products)
    order_count = len(orders)


    return render_template('Seller-page/sales.html', profile_pic=profile_pic, username=username ,products = products,
                           total_sales =total_sales, order_count= order_count)




@app.route('/seller/sales-filtered', methods=['GET'])
def seller_sales_filtered():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid()
    
    # Get start_date and end_date from the query string
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to the last 30 days if no dates are provided
    if not start_date:
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')  # 30 days ago
    if not end_date:
        end_date = datetime.today().strftime('%Y-%m-%d')

    try:
        # Get seller info based on user session ID
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['id'],))
        user = cursor.fetchone()
        
        if user:
            session['seller_id'] = user['seller_id']
            
            # Filter orders where the status is 'Completed' within the date range
            cursor.execute("""
                SELECT product_id, SUM(quantity) AS total_quantity, SUM(total_price) AS totalprice, 
                products.Product_Name, products.Image, products.Price, MAX(orders.updated_at) AS last_updated_at
                FROM orders
                JOIN products ON orders.product_id = products.Id
                WHERE orders.seller_id = %s 
                  AND orders.order_status = "Completed"
                  AND orders.updated_at BETWEEN %s AND %s
                GROUP BY products.Id;
            """, (session['seller_id'], start_date, end_date))
            products = cursor.fetchall()

            # Fetch the total sales amount for the specified date range
            cursor.execute("""
                SELECT total_price 
                FROM orders 
                WHERE order_status = 'Completed' 
                  AND seller_id = %s 
                  AND orders.updated_at BETWEEN %s AND %s
            """, (session['seller_id'], start_date, end_date))
            orders = cursor.fetchall()

        else:
            products = []
            orders = []

    finally:
        cursor.close()
        connection.close()

    # Calculate total sales and order count
    total_sales = sum(order['total_price'] for order in orders)
    order_count = len(orders)

    return render_template('Seller-page/sales.html', 
                           profile_pic=profile_pic, username=username,products=products, total_sales=total_sales, 
                           order_count=order_count)



#===========================================================================================================================================
@app.route('/seller/profile')
def profile():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    username, profile_pic = sellerid() 
    try:
        cursor.execute("""SELECT *
            FROM addresses_seller
            JOIN sellers ON addresses_seller.seller_id = sellers.seller_id
            WHERE sellers.user_id = %s;
        """, (session['id'],))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['user_id']  
            Fname = user['Fname'] 
            Mname = user['Mname'] 
            Lname = user['Lname']
            shop_name = user['shop_name']
            description =user['shop_description'] 
            
            houseNo = user['houseNo'] 
            street = user['street'] 
            barangay = user['barangay'] 
            city = user['city'] 
            Province = user['Province'] 
            postal_code = user['postal_code'] 
            email =  user['email']
            shopname = user['shop_name']
            contact_num = user['mobile_number']
            profile_pic1 = user['profile_pic']
             
        else:  
            Fname = ''
            Mname =  ''
            Lname =  ''
            shop_name = ''
            
            houseNo =  ''
            street =  ''
            barangay =  ''
            city =  ''
            Province =  ''
            postal_code =  ''
            email =   ''
            shopname =  ''
            contact_num =  ''
            profile_pic1 = ''
            description = ''

    finally:
        cursor.close()
        connection.close()

    return render_template('Seller-page/seller-profile.html',
                            Fname = Fname, Mname=Mname, Lname=Lname, houseNo=houseNo,
                            street=street, barangay = barangay, city=city, Province=Province, 
                            postal_code =postal_code, email= email, shopname=shopname, contact_num = contact_num,
                            profile_pic = profile_pic, shop_name =shop_name, description = description )



#==========================================================================Chat========================================================
@app.route('/chat/<int:seller_id>/<int:buyer_id>', methods=['GET', 'POST'])
def chat(seller_id, buyer_id):
    username, profile_pic = buyerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    print(f"Chat route accessed with seller_id={seller_id}, buyer_id={buyer_id}")

    # Example user_id from session (replace with actual user ID logic)
    user_id = session.get('id')
    print(f"Logged-in user_id: {user_id}")

    # Check if the logged-in user is a buyer
    cursor.execute("SELECT buyer_id FROM buyers WHERE user_id = %s", (user_id,))
    is_buyer = cursor.fetchone() is not None
    print(f"Buyer check: is_buyer={is_buyer}")

    # Determine sender and receiver based on user type
    if is_buyer:
        print("User is a buyer.")
        sender_id = buyer_id  # The logged-in user (buyer) is the sender
        receiver_id =seller_id # The seller is the receiver
    else:
        print("User is a seller.")
        sender_id = seller_id  # The logged-in user (seller) is the sender
        receiver_id = buyer_id  # The buyer is the receiver

    if request.method == 'POST':
        message = request.form['message']
        timestamp = datetime.now()
        print(f"Message: {message}, Timestamp: {timestamp}, Sender ID: {sender_id}, Receiver ID: {receiver_id}")

        # Insert the message into the database
        cursor.execute(
            "INSERT INTO messages (sender_id, receiver_id, message, timestamp) VALUES (%s, %s, %s, %s)",
            (sender_id, receiver_id, message, timestamp)
        )
        connection.commit()
        print("Message inserted into the database.")

    # Fetch chat messages between the buyer and seller
    cursor.execute(
        """
        SELECT sender_id, receiver_id, message, timestamp 
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
       
        """, (buyer_id, seller_id, seller_id, buyer_id)
    )
    messages = cursor.fetchall()

    cursor.execute(
        """
        SELECT seller_id,   shop_name,shop_logo
        FROM sellers
        WHERE seller_id = %s
        """, (seller_id,)
        )
    seller = cursor.fetchone()


    cursor.execute("""
            SELECT 
                s.shop_name, 
                s.shop_logo, 
                m.message AS last_message, 
                m.timestamp AS last_message_time,
                m.sender_id, 
                m.receiver_id
            FROM sellers s
            JOIN messages m ON s.seller_id = m.receiver_id
            WHERE 
                m.sender_id = %s
                AND m.timestamp = (
                    SELECT MAX(timestamp) 
                    FROM messages 
                    WHERE sender_id = m.sender_id AND receiver_id = m.receiver_id
                );
        """, (buyer_id,))

    
    chats = cursor.fetchall()

    cursor.close()
    connection.close()

    print("Database connection closed.")
    print("sender_id",sender_id)
    print("buyer_id",buyer_id)
    print("seller_id",seller_id)

    return render_template('Home-page/chat.html', username = username , profile_pic = profile_pic,
                       sender_id=sender_id, chats =chats,
                       seller_id=seller_id, 
                       buyer_id=buyer_id, 
                       messages=messages,
                       seller = seller)

@app.route('/chat', methods=['GET'])
def allchat():
    username, profile_pic = buyerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    buyer_id =session['buyer_id']
    print(buyer_id)
    
    
    messages = None
    

    cursor.execute("""
            SELECT 
                s.shop_name, 
                s.shop_logo, 
                m.message AS last_message, 
                m.timestamp AS last_message_time,
                m.sender_id, 
                m.receiver_id
            FROM sellers s
            JOIN messages m ON s.seller_id = m.receiver_id
            WHERE 
                m.sender_id = %s
                AND m.timestamp = (
                    SELECT MAX(timestamp) 
                    FROM messages 
                    WHERE sender_id = m.sender_id AND receiver_id = m.receiver_id
                );
        """, (session['buyer_id'],))

    
    chats = cursor.fetchall()
    

    seller = None


    cursor.close()
    connection.close()
     
    return render_template('Home-page/chat.html', username = username , profile_pic = profile_pic,
                       messages=messages, chats = chats, seller = seller , is_get=True  
                       )

    
#==============================================================================================================================================

@app.route('/chat-seller/<int:buyer_id>/<int:seller_id>', methods=['GET', 'POST'])
def chat_seller(seller_id, buyer_id):
    username, profile_pic = sellerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    


    print(f"Chat route accessed with seller_id={seller_id}, buyer_id={buyer_id}")

    # Example user_id from session (replace with actual user ID logic)
    user_id = session.get('id')
    print(f"Logged-in user_id: {user_id}")

    # Check if the logged-in user is a buyer
    cursor.execute("SELECT buyer_id FROM buyers WHERE user_id = %s", (user_id,))
    is_buyer = cursor.fetchone() is not None
    print(f"Buyer check: is_buyer={is_buyer}")

    # Determine sender and receiver based on user type
    if is_buyer:
        print("User is a buyer.")
        sender_id = buyer_id  # The logged-in user (buyer) is the sender
        receiver_id =seller_id # The seller is the receiver
    else:
        print("User is a seller.")
        sender_id = seller_id  # The logged-in user (seller) is the sender
        receiver_id = buyer_id  # The buyer is the receiver

    if request.method == 'POST':
        message = request.form['message']
        timestamp = datetime.now()
        print(f"Message: {message}, Timestamp: {timestamp}, Sender ID: {sender_id}, Receiver ID: {receiver_id}")

        # Insert the message into the database
        cursor.execute(
            "INSERT INTO messages (sender_id, receiver_id, message, timestamp) VALUES (%s, %s, %s, %s)",
            (sender_id, receiver_id, message, timestamp)
        )
        connection.commit()
        

    # Fetch chat messages between the buyer and seller
    cursor.execute(
        """
        SELECT sender_id, receiver_id, message, timestamp 
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
       
        """, (buyer_id, seller_id, seller_id, buyer_id)
    )
    messages = cursor.fetchall()
    #babagohin
    cursor.execute(
        """
        SELECT buyer_id,   Fname,profile_pic
        FROM buyers
        WHERE buyer_id = %s
        """, (buyer_id,)
        )
    seller = cursor.fetchone()
    #babagohin
    cursor.execute("""
            SELECT
                b.Fname, 
                b.profile_pic, 
                m.message AS last_message, 
                m.timestamp AS last_message_time,
                m.sender_id, 
                m.receiver_id
            FROM buyers b
            JOIN messages m 
                ON b.buyer_id = m.sender_id
            WHERE 
                m.receiver_id = %s 
                AND m.timestamp = (
                    SELECT MAX(m2.timestamp) 
                    FROM messages m2
                    WHERE m2.sender_id = m.sender_id 
                    AND m2.receiver_id = m.receiver_id
                );
        """, (seller_id,))

    
    chats = cursor.fetchall()

    cursor.close()
    connection.close()

    print("Database connection closed.")
    print("sender_id",sender_id)
    print("buyer_id",buyer_id)
    print("seller_id",seller_id)

    return render_template('seller-page/chat.html', username = username , profile_pic = profile_pic,
                       sender_id=sender_id, chats =chats,
                       seller_id=seller_id, 
                       buyer_id=buyer_id, 
                       messages=messages,
                       seller = seller)

@app.route('/chat-seller', methods=['GET'])
def allchat_seller():
    username, profile_pic = sellerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    seller_id =session['seller_id']
    print(seller_id)
    
    messages = None
    

    cursor.execute("""
           SELECT
                b.Fname, 
                b.profile_pic, 
                m.message AS last_message, 
                m.timestamp AS last_message_time,
                m.sender_id, 
                m.receiver_id
            FROM buyers b
            JOIN messages m 
                ON b.buyer_id = m.sender_id
            WHERE 
                m.receiver_id =%s
                AND m.timestamp = (
                    SELECT MAX(m2.timestamp) 
                    FROM messages m2
                    WHERE m2.sender_id = m.sender_id 
                    AND m2.receiver_id = m.receiver_id
                );
        """, (seller_id,))

    
    chats = cursor.fetchall()
    

    seller = None


    cursor.close()
    connection.close()
     
    return render_template('Seller-page/chat.html', username = username , profile_pic = profile_pic,
                       messages=messages, chats = chats, seller = seller)



#=========================================================================================================================================================
@app.route('/notification')
def notification():
    username, profile_pic = buyerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    buyer_id = session.get('buyer_id')
    try:
        # Get seller info based on user session ID
        cursor.execute("""SELECT *
                        FROM buyers_reported 
                        JOIN sellers ON sellers.seller_id = buyers_reported.seller_id
                        WHERE buyer_id = %s""", (buyer_id,))
        reports = cursor.fetchall()
        cursor.execute("""SELECT b.buyer_id, s.shop_name, n.cancel_reason
FROM notification_buyer n
JOIN orders o ON o.buyer_id = %s
JOIN sellers s ON s.seller_id = n.seller_id
JOIN buyers b ON b.buyer_id = o.buyer_id
WHERE b.buyer_id = %s AND o.order_id =b.buyer_id;   ;""", (buyer_id,buyer_id,))
        cancelled = cursor.fetchall()

        cursor.execute("""SELECT * 
                            FROM orders
                            JOIN products ON products.Id = orders.product_id
                            WHERE buyer_id = %s""", (buyer_id,))
        orders = cursor.fetchall()
        
    finally:
        cursor.close()
        connection.close()
    return render_template('Home-page/notif.html', username = username , profile_pic = profile_pic,
                           reports = reports,orders=orders,cancelled = cancelled)



@app.route('/seller-notification')
def notification_seller():
    username, profile_pic = sellerid()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if not session.get('seller_id'):
        print("Seller ID is missing from the session.")
        return redirect(url_for('login'))  # Redirect to login if no seller_id

    try:
        # Get cancelled orders
        cursor.execute(
            """
            SELECT 
                n.buyer_id, 
                n.order_id, 
                n.cancel_reason, 
                o.seller_id, 
                o.product_id, 
                p.Product_Name, 
                b.Fname
            FROM 
                notification_seller n
            JOIN 
                buyers b ON n.buyer_id = b.buyer_id
            JOIN 
                orders o ON n.order_id = o.order_id
            JOIN 
                products p ON o.product_id = p.Id
            WHERE 
                o.seller_id = %s AND o.order_status = 'Cancelled'
            """,
            (session['seller_id'],)
        )
        cancelled = cursor.fetchall()

        # Get pending orders
        cursor.execute(
            """
            SELECT 
                b.buyer_id, 
                o.seller_id, 
                o.product_id, 
                p.Product_Name, 
                b.Fname
            FROM 
                orders o
            JOIN 
                buyers b ON o.buyer_id = b.buyer_id
            JOIN 
                products p ON o.product_id = p.Id
            WHERE 
                o.seller_id = %s AND o.order_status = 'Pending'
            """,
            (session['seller_id'],)
        )
        pendings = cursor.fetchall()

        # Get reports
        cursor.execute(
            """
            SELECT *
            FROM report_sellerproduct 
            JOIN buyers ON buyers.buyer_id = report_sellerproduct.buyer_id
            WHERE seller_id = %s
            """,
            (session['seller_id'],)
        )
        reports = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
        cancelled = []
        pendings = []
        reports = []
    finally:
        cursor.close()
        connection.close()

    return render_template(
        'Seller-page/notif.html',
        username=username,
        profile_pic=profile_pic,
        pendings=pendings,
        cancelled=cancelled,
        reports=reports
    )



#==================================================================================================================================================================


@app.route('/submit-rating', methods=['POST'])
def submit_rating():
    order_id = request.form.get('order_id')
    rating = request.form.get('rating')
    description = request.form.get('description')
    print(order_id)
    print(rating)
    print(description)
    
    # Database connection
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch product ID based on order ID
        cursor.execute("SELECT product_id FROM orders WHERE order_id = %s", (order_id,))
        product = cursor.fetchone()
        if not product:
            raise ValueError("Order ID not found.")
        product_id = product['product_id']

        # Handle image upload
        image3 = request.files.get('picture')
        image = None
        if image3 and allowed_file(image3.filename):
            image = secure_filename(image3.filename)
            image3.save(os.path.join(app.config['UPLOAD_FOLDER'], image))

        # Insert rating into the database
        query = """INSERT INTO rating (product_id, rate, description, product_pic,buyer_id)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (product_id, rating, description, image, session['buyer_id']))
        connection.commit()

        # Redirect after successful operation
        print("Rating successfully submitted.")
        return redirect(url_for('user_orders',error = 'Rating successfully submitted.'))
    
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Database error: {err}")
        return redirect(url_for('user_orders'))
    
    except ValueError as ve:
        print(f"Error: {ve}")
        return redirect(url_for('user_orders'))
    
    finally:
        cursor.close()
        connection.close()

    
#====================================================================================================
import logging
from flask_mail import Message

# Set logging level to debug
app.logger.setLevel(logging.DEBUG)

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Retrieve user based on email
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        # Create a token for password reset link
        token = s.dumps(email, salt='reset-password')
        reset_link = url_for('reset_password_page', token=token, _external=True)

        msg = Message("Password Reset Request", 
                      recipients=[email], 
                      sender='ecohaven28@gmail.com')
        msg.body = f"To reset your password, click the link below:\n\n{reset_link}"

        try:
            mail.send(msg)
            return redirect(url_for('login', error='Email sent successfully. Please check your inbox.'))
        except Exception as e:
            app.logger.error(f"Error sending email: {e}")
            return redirect(url_for('login', error='There was an error sending the reset email. Please try again later.'))
    else:
        return redirect(url_for('login', error='Your email is not registered. Please check and try again.'))

#forget__pass
@app.route('/reset-password-page/<token>', methods=['GET', 'POST'])
def reset_password_page(token):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    email = None

    # Debug: Print received token
    print(f"Received token: {token}")

    # Try to decode the token
    try:
        email = s.loads(token, salt='reset-password', max_age=3600)  # Token expires in 1 hour
        # Debug: Print decoded email
        print(f"Decoded email: {email}")
    except Exception as e:
        print(f"Error decoding token: {e}")  # Debug: Log decoding error
        return 'The reset link is invalid or has expired.'

    
    return render_template('Login-page/NewpassForm.html', email=email)


@app.route('/reset-password-new', methods=['GET', 'POST'])
def reset_password_new():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    password = request.form.get('password')
    email = request.form.get('email')
    print('email!!!',email)
    print(f"Password received: {password}")  # Debug: Print submitted password

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)
    print(f"Hashed password: {hashed_password}")  # Debug: Print hashed password

    # Update the user's password in the database
    try:
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        connection.commit()
        print("Password updated successfully.")  # Debug: Confirm password update
    except Exception as db_error:
        print(f"Database error: {db_error}")  # Debug: Log database errors
    finally:
        # Close the connection
        cursor.close()
        connection.close()

    return redirect(url_for('login', error='Your password has been updated successfully.'))

#====================================================================================================


@app.route('/download-sales-report')
def download_sales_report():
    # Retrieve the start and end date from the query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to the last 30 days if no dates are provided
    if not start_date:
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')  # 30 days ago
    if not end_date:
        end_date = datetime.today().strftime('%Y-%m-%d')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    print(start_date)
    print(end_date)

    seller_id = session.get('seller_id')
    if not seller_id:
        return "Unauthorized", 401

    # Fetch sales data
    cursor.execute('''
        SELECT product_id, SUM(quantity) AS total_quantity, SUM(total_price) AS totalprice,
               products.Product_Name, products.Image, products.Price, MAX(orders.updated_at) AS last_updated_at
        FROM orders
        JOIN products ON orders.product_id = products.Id
        WHERE orders.seller_id = %s 
                   AND orders.order_status = "Completed"
                    AND orders.updated_at BETWEEN %s AND %s
        GROUP BY products.Id;
    ''', (seller_id, start_date, end_date))
    sales_data = cursor.fetchall()

    # Fetch total price
    cursor.execute('''
        SELECT 
            SUM(orders.total_price) AS total_price,
            SUM(orders.total_price * 0.95) AS total_price_sum,
            SUM(orders.total_price) * 0.05 AS total_price_5_percent
        FROM orders
        WHERE orders.seller_id = %s 
        AND orders.order_status = "Completed"
        AND orders.updated_at BETWEEN %s AND %s;
    ''', (seller_id,start_date, end_date))

    # Fetch the result
    result = cursor.fetchone()
    total_price = result['total_price'] or 0
    total_price_sum = result['total_price_sum'] or 0
    total_price_5_percent = result['total_price_5_percent'] or 0


    # Fetch seller info
    cursor.execute('''
        SELECT 
            CONCAT(sellers.Fname, ' ', sellers.Mname, ' ', sellers.Lname) AS full_name,
            sellers.shop_name,
            CONCAT(A.houseNo, ' , ', A.street, ' , ', A.barangay, ' ,  ', A.city, ' , ', A.Province) AS addresses
        FROM sellers
        JOIN addresses_seller A ON A.seller_id = sellers.seller_id 
        WHERE sellers.seller_id =%s;
    ''', (seller_id,))
    sellers = cursor.fetchall()

    connection.close()

    # Generate PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add Title
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Sales Report", ln=True, align='C')

    # Add Header
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Seller ID: {seller_id}", ln=True, align='L')

    # Seller info
    # Seller info
    for seller in sellers:
        pdf.set_font("Arial", size=12)
        
        # Access the seller's full name from the dictionary
        full_name = seller['full_name']
        shop_name = seller['shop_name']
        address = seller['addresses']
        
        pdf.cell(0, 10, txt=f"Name: {full_name}", ln=True, align='L')
        pdf.cell(0, 10, txt=f"Shop_name: {shop_name}", ln=True, align='L')

        # Add Address
        pdf.cell(0, 10, txt=f"Address: {address}", ln=True, align='L')

        # Separator line
        pdf.cell(0, 10, txt="--------------------------------------------", ln=True, align='L')


    # Add Sales Data
    for sale in sales_data:
        product_name = sale['Product_Name']
        price = sale['totalprice']
        total_quantity = sale['total_quantity']
        pdf.cell(0, 10, txt=f"Product: {product_name} -  {price:.2f} php - {total_quantity}X", ln=True)

    # Add Total Sales (bold)
   
    pdf.cell(0, 10, txt="--------------------------------------------", ln=True)
    pdf.cell(0, 10, txt=f"Total Sales: {total_price:.2f} php", ln=True, align='R')
    pdf.cell(0, 10, txt=f"Platform Commission: (5%) -{total_price_5_percent:.2f} php ", ln=True, align='R')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=f"Total Sales: {total_price_sum:.2f} php", ln=True, align='R')

    # Save PDF to BytesIO
    pdf.set_font("Arial", '', 12)
    pdf_buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')  # Generate PDF as a string
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)

    # Send PDF as response
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=sales_report.pdf'

    return response






#=======================================================================================================$$$$$$
@app.route('/admin_sales', methods=["GET"])
def admin_sales():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get the shop_name from query parameters
    shop_name = request.args.get('shop_name', '').strip()  # Default to an empty string

    # Base SQL query
    base_query = """
        SELECT s.seller_id, s.shop_name, s.shop_logo, COUNT(o.order_id) AS completed_orders,
               SUM(o.total_price) AS totalprice,
               SUM(o.total_price) * 0.05 AS total_price_5_percent
        FROM orders o
        JOIN sellers s ON s.seller_id = o.seller_id
        WHERE o.order_status = 'Completed'
    """

    # Add a search condition if shop_name is provided
    if shop_name:
        base_query += " AND s.shop_name LIKE %s"

    base_query += " GROUP BY s.seller_id, s.shop_name;"

    try:
        if shop_name:
            cursor.execute(base_query, (f"%{shop_name}%",))
        else:
            cursor.execute(base_query)

        commissions = cursor.fetchall()
        for commission in commissions:
            commission['totalprice'] = round(commission['totalprice'] or 0, 2)
            commission['total_price_5_percent'] = round(commission['total_price_5_percent'] or 0, 2)

        # Calculate the sum of total_price_5_percent with 2 decimal places
        commissions_sum = round(sum(commission['total_price_5_percent'] for commission in commissions), 2)

    finally:
        cursor.close()
        connection.close()

    return render_template('admin-page/sales.html', commissions=commissions, commissions_sum=commissions_sum, shop_name=shop_name)

@app.route('/admin/admin-filtered', methods=['GET'])
def admin_sales_filtered():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    
    # Get start_date and end_date from the query string
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to the last 30 days if no dates are provided
    if not start_date:
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')  # 30 days ago
    if not end_date:
        end_date = datetime.today().strftime('%Y-%m-%d')

    try:
       
        cursor.execute("""
          SELECT s.seller_id, s.shop_name, s.shop_logo, COUNT(o.order_id) AS completed_orders, o.updated_at, o.created_at,
            SUM(o.total_price) AS totalprice,
            SUM(o.total_price) * 0.05 AS total_price_5_percent
        FROM orders o
        JOIN sellers s ON s.seller_id = o.seller_id
        WHERE o.order_status = "Completed"
        AND o.updated_at BETWEEN %s AND %s
        GROUP BY s.seller_id
       
    """, (start_date, end_date))
        commissions = cursor.fetchall()
        for commission in commissions:
            commission['totalprice'] = round(commission['totalprice'] or 0, 2)
            commission['total_price_5_percent'] = round(commission['total_price_5_percent'] or 0, 2)

        # Calculate the sum of total_price_5_percent with 2 decimal places
        commissions_sum = round(sum(commission['total_price_5_percent'] for commission in commissions), 2)

    finally:
        cursor.close()
        connection.close()



    return render_template('admin-page/sales.html',commissions = commissions ,commissions_sum =commissions_sum)





@app.route('/download-sales-report-admin')
def download_sales_report_admin():
    # Retrieve the start and end date from the query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to the last 30 days if no dates are provided
    if not start_date:
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')  # 30 days ago
    if not end_date:
        end_date = datetime.today().strftime('%Y-%m-%d')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    print(start_date)
    print(end_date)

   

    # Fetch sales data
    cursor.execute("""
        SELECT s.seller_id, s.shop_name, s.shop_logo, COUNT(o.order_id) AS completed_orders, o.updated_at, o.created_at,
            SUM(o.total_price) AS totalprice,
            SUM(o.total_price) * 0.05 AS total_price_5_percent
        FROM orders o
        JOIN sellers s ON s.seller_id = o.seller_id
        WHERE o.order_status = "Completed"
        AND o.updated_at BETWEEN %s AND %s
        GROUP BY s.seller_id
                   LIMIT 10;
       
    """, (start_date, end_date))

    commissions = cursor.fetchall()
    for commission in commissions:
        commission['totalprice'] = round(commission['totalprice'] or 0, 2)
        commission['total_price_5_percent'] = round(commission['total_price_5_percent'] or 0, 2)

    # Calculate the sum of total_price_5_percent with 2 decimal places
    commissions_sum = round(sum(commission['total_price_5_percent'] for commission in commissions), 2)

    # Fetch total price
    

    # Fetch the result



    # Fetch seller info
    

    connection.close()

    # Generate PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add Title
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Sales Report", ln=True, align='C')

    # Add Header
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Admin Commissions", ln=True, align='L')

        # Separator line
    pdf.cell(0, 10, txt="--------------------------------------------", ln=True, align='L')


    # Add Sales Data
    for commission in commissions:
        shopname = commission['shop_name']
        totalprice = commission['totalprice']
        total_price_5_percent = commission['total_price_5_percent']
       
        pdf.cell(0, 10, txt=f"Shopname: {shopname} -  {total_price_5_percent:.2f} php ", ln=True)

    # Add Total Sales (bold)
   
    pdf.cell(0, 10, txt="--------------------------------------------", ln=True)
    
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=f"Total Commissions: {commissions_sum:.2f} php", ln=True, align='R')

    # Save PDF to BytesIO
    pdf.set_font("Arial", '', 12)
    pdf_buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')  # Generate PDF as a string
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)

    # Send PDF as response
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=sales_report-admin.pdf'

    return response





#=======================================================================================================
@app.route('/signup')
def signup():
    return render_template('Login-page/LoginPage-signup.html')

@app.route('/forgotPassword')
def forgotPassword():
    return render_template('Login-page/LoginPage-forgotPassword.html')

@app.route('/createAccountBuyer')
def createAccountBuyer():
    return render_template('Login-page/LoginPage-createAccountBuyer.html')

@app.route('/createAccountSeller')
def createAccountSeller():
    return render_template('Login-page/LoginPage-createAccountSeller.html')

@app.route('/createAccountRider')
def createAccountRider():
    return render_template('Login-page/LoginPage-createAccountRider.html')


@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))  

if __name__ == '__main__':
    app.run(host='192.168.126.154', port=3306, debug=True)
    