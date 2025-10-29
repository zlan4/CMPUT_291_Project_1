import sqlite3
import random


"""Add all the database functions here."""

"""Login + Registration Functions"""
def check_login(cursor, userid, password):
    """
    Check if the login credentials exists in the database.
    
    @param userid: user id
    @param password: user password
    
    @return:
    - true and user role if credentials are valid
    - false and empty string if credentials are invalid
    """
    cursor.execute('''
        SELECT *
        FROM users
        WHERE uid = ? AND pwd = ?
        ''', (userid, password))
    
    row = cursor.fetchone()

    if row:
        return True, row
    else:
        return False, ''


def register_user(cursor, name, email, password):
    """
    Register a new user in the database.
    
    @param name: user's name
    @param email: user's email
    @param password: user's password
    
    @return:
    - true if registration is successful
    - false if email already exists
    """

    cursor.execute('''
        SELECT *
        FROM customers
        WHERE email = ?
        ''', (email,))
    row = cursor.fetchone()

    if row:
        print("Email already registered.")
        return False, ''
    
    # Generate user ID - if the id already exists, generate a new one
    while True:
        id = random.randint(10000, 99999)
        cursor.execute('''
            SELECT *
            FROM users
            WHERE uid = ?
            ''', (id,))
        row = cursor.fetchone()
        if not row:
            break 
    
    # Insert into users and customers table
    cursor.execute('''
        INSERT INTO users (uid, pwd, role)
        VALUES (?, ?, 'customer')
        ''', (id, password))
    
    cursor.execute('''
        INSERT INTO customers (cid, name, email)
        VALUES (?, ?, ?)
        ''', (id, name, email))
    return True


"""Customer Functions"""
def search_product(cursor, keyword):
    """
    Search for products by keyword.
    
    @param keyword: search keyword

    @return:
    - true and list of products if found
    - false and empty string if no products found
    """
    # Add search to table

    # Return products
    cursor.execute('''
        SELECT *
        FROM products
        WHERE name LIKE %?% 
        OR descr LIKE %?%
        ''', (f"%{keyword}%", f"%{keyword}%"))

    products = cursor.fetchall()

    if products:
        return True, products
    else:
        return False, ''
    

def product_details(cursor, product_id):
    """
    Get the details of a specific product.
    
    @param product_id: product id

    @return:
    - true and product details if product exists
    - false and empty string if product does not exist
    """
    cursor.execute('''
        SELECT *
        FROM products
        WHERE pid = ?
        ''', (product_id,))

    product = cursor.fetchone()

    if product:
        return True, product
    else:
        return False, ''


def add_to_cart(cursor, cid, sessionNo, pid, qty):
    """
    Add a product to the customer's cart.

    @param cid: customer id
    @param sessionNo: session number
    @param pid: product id
    @param qty: quantity to add 

    @return:
    - true if addition is successful
    - false if not enough stock available
    """
    cursor.execute('''
        SELECT stock_count
        FROM products
        WHERE pid = ?
        ''', (pid,))

    count = cursor.fetchone()[0]

    if qty > count:
        print("Not enough stock available.")
        return False, ''
    else:
        cursor.execute('''
            INSERT INTO cart (cid, sessionNo, pid, qty)
            VALUES (?, ?, ?, ?)
            ''', (cid, sessionNo, pid, qty))
        return True # run the commit outside


def update_product_cart_quantity(cursor, cid, sessionNo, pid, qty):
    """
    Update the quantity of a specific product.
    
    @param cid: customer id
    @param sessionNo: session number
    @param pid: product id
    @param qty: new quantity

    @return:
    - true if update is successful
    - false if not enough stock available
    """
    cursor.execute('''
        SELECT stock_count
        FROM products
        WHERE pid = ?
        ''', (pid,))

    count = cursor.fetchone()[0]

    if qty > count:
        print("Not enough stock available.")
        return False, ''
    else:
        cursor.execute('''
            UPDATE cart
            SET qty = ?
            WHERE cid = ? AND sessionNo = ? AND pid = ?
            ''', (qty, cid, sessionNo, pid))
        return True # run the commit outside


def remove_from_cart(cursor, cid, sessionNo, pid):
    """
    Remove a product from the customer's cart.
    
    @param cid: customer id
    @param sessionNo: session number
    @param pid: product id

    @return:
    - true if removal is successful
    """
    cursor.execute('''
        DELETE FROM cart
        WHERE cid = ? AND sessionNo = ? AND pid = ?
        ''', (cid, sessionNo, pid))
    return True  # run the commit outside


def checkout(cursor, cid, sessionNo, shipping_address):
    """
    Creates a new order with a unique order number.
    Creates entries in the order_items table for each item in the cart.
    Updates the stock count in the products table.
    Empties the cart after the order is created.
    
    @param cid: customer id
    @param sessionNo: session number
    @param shipping_address: shipping address for the order
    
    @return:
    - true if checkout is successful
    """
    # Generate unique order number
    while True:
        ono = random.randint(10000, 99999)
        cursor.execute('''
            SELECT *
            FROM orders
            WHERE ono = ?
            ''', (ono,))
        row = cursor.fetchone()
        if not row:
            break 

    # Get current date
    odate = sqlite3.datetime.date.today().isoformat()

    # Insert into orders table
    cursor.execute('''
        INSERT INTO orders (ono, cid, sessionNo, odate, shipping_address)
        VALUES (?, ?, ?, ?, ?)
        ''', (ono, cid, sessionNo, odate, shipping_address))

    # Get cart items
    cursor.execute('''
        SELECT pid, qty, price
        FROM cart
        JOIN products ON cart.pid = products.pid
        WHERE cid = ? AND sessionNo = ?
        ''', (cid, sessionNo))

    cart_items = cursor.fetchall()

    # Insert into order_items table and update product stock
    lineNo = 0
    for item in cart_items:
        pid, qty, price = item
        cursor.execute('''
            INSERT INTO orderlines (ono, lineNo, pid, qty, uprice)
            VALUES (?, ?, ?, ?, ?)
            ''', (ono, lineNo, pid, qty, price))
        
        # Update product stock
        cursor.execute('''
            UPDATE products
            SET stock_count = stock_count - ?
            WHERE pid = ?
            ''', (qty, pid))
        
        # Empty the cart
        cursor.execute('''
            DELETE FROM cart
            WHERE cid = ? AND sessionNo = ? AND pid = ?
            ''', (cid, sessionNo, pid))

        lineNo += 1

    return True # run the commit outside


def view_past_orders(cursor, cid):
    """
    View past orders of the customer.
   
    @param cid: customer id
    
    @return:
    - true and list of past orders if orders exist
    - false and empty string if no orders exist
    """
    cursor.execute('''
        SELECT *
        FROM orders
        WHERE cid = ?
        ORDER BY odate DESC
        ''', (cid,))

    orders = cursor.fetchall()

    if orders:
        return True, orders
    else:
        return False, ''


def view_order_details(cursor, ono):
    """
    View the details of a specific past order.
    
    @param ono: order number
    
    @return:
    - true and order details if order exists
    - false and empty string if order does not exist
    """
    cursor.execute('''
        SELECT *
        FROM orderlines
        WHERE ono = ?
        ''', (ono,))

    order_details = cursor.fetchall()

    if order_details:
        return True, order_details
    else:
        return False, ''


def grand_total(cursor, ono):
    """
    Calculate the grand total of a specific order.
    
    @param ono: order number
    
    @return:
    - true and total amount if order exists
    - false and empty string if order does not exist
    """
    cursor.execute('''
        SELECT SUM(qty * uprice) as total
        FROM orderlines
        WHERE ono = ?
        ''', (ono,))

    total = cursor.fetchone()[0]

    if total is not None:
        return True, total
    else:
        return False, ''