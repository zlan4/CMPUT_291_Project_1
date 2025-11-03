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
    return True, id


"""Customer Functions"""
def new_session(cursor, cid):
    """
    Create a new session for the customer.
    @param cid: customer id
    
    @return:
    - session number
    """
    # Get the max sessionNo and add one to it to get the next sessionNo
    cursor.execute('''
        SELECT MAX(sessionNo)
        FROM sessions
        WHERE cid = ?
        ''', (cid,))
    
    row = cursor.fetchone()
    if row[0] is None:
        sessionNo = 1
    else:
        sessionNo = row[0] + 1

    start_time = sqlite3.datetime.datetime.today().isoformat()

    cursor.execute('''
        INSERT INTO sessions (cid, sessionNo, start_time, end_time)
        VALUES (?, ?, ?, NULL)
        ''', (cid, sessionNo, start_time))
    
    return sessionNo


def search_product(cursor, cid, sessionNo, keyword):
    """
    Search for products by keyword.
    
    @param keyword: search keyword
 
    @return:
    - true and list of products if found
    - false and empty string if no products found
    """
    # Add search to table
    ts = sqlite3.datetime.datetime.today().isoformat()
    
    cursor.execute('''
        INSERT INTO search (cid, sessionNo, ts, query)
        VALUES (?, ?, ?, ?)
        ''', (cid, sessionNo, ts, keyword))

    # Return products
    cursor.execute('''
        SELECT *
        FROM products
        WHERE name LIKE ?
        OR descr LIKE ?
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

def viewed_product(cursor, cid, sessionNo, product_id):
    ts = sqlite3.datetime.datetime.today().isoformat()
    cursor.execute('''
        INSERT INTO viewedProduct (cid, sessionNo, ts, pid)
        VALUES (?, ?, ?, ?)
        ''', (cid, sessionNo, ts, product_id))


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
        return True, "" # run the commit outside

## View Cart Items
def view_cart_items(cursor, cid, sessionNo):
    cursor.execute('''
            SELECT *
            FROM cart
            WHERE cid = ? AND sessionNo = ?
            ''', (cid, sessionNo))
    return cursor.fetchall()

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
    # Generate unique order number, loop until a unique one is created
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
        SELECT cart.pid, qty, price
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

        lineNo += 1 # increment the lineNo for other products

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

"""Salesperson Functionalities"""
def update_product(cursor, product_id, new_price, new_stock):
    """
    Allows a salesperson to update a product's price and stock count
    
    @param product_id: product id
    @param new_price: new price entered by the salesperson
    @param new_stock: new stock count entered by the salesperson
    """

    cursor.execute('''
        UPDATE products
        SET price = ?, stock_count = ?
        WHERE pid = ?
    ''', (new_price, new_stock, product_id))

def generate_sales_report(cursor):
    """
    Generate weekly sales report
    
    @return:
    - Dictionary containing the sales statistics for the past 7 days (excluding the current day)
    """

    cursor.execute('''
        SELECT 
        COUNT(DISTINCT o.ono) AS distinct_orders,
        COUNT(DISTINCT ol.pid) AS distinct_products_sold,
        COUNT(DISTINCT o.cid) AS distinct_customers_with_purchases,
        ROUND(SUM(ol.qty * ol.uprice) / COUNT(DISTINCT o.cid), 2) AS average_amount_per_customer,
        ROUND(SUM(ol.qty * ol.uprice), 2) AS total_sales_amount
        FROM orders o
        JOIN orderlines ol ON o.ono = ol.ono
        WHERE date(o.odate) >= date('now', '-7 days') AND date(o.odate) <= date('now', '-1 day');
    ''')
    result = cursor.fetchone()
    weekly_sales = {
        'distinct_orders': result[0],
        'distinct_products_sold': result[1],
        'distinct_customers_with_purchases': result[2],
        'average_amount_per_customer': result[3],
        'total_sales_amount': result[4]
    }
    return weekly_sales

def top_three_products_based_on_order(cursor):
    """
    List the top three products based on the number of distinct orders they were in (includes ties)
    
    @return:
    - Dictionary containing product name, id, and order count for the top three products
    """

    cursor.execute("""
    WITH product_counts AS (
    SELECT p.pid, p.name, COUNT(DISTINCT ol.ono) as order_count
    FROM products p JOIN orderlines ol ON p.pid = ol.pid
    GROUP BY p.pid, p.name)
    SELECT name, pid, order_count
    FROM product_counts pc1
    WHERE (
    SELECT COUNT(DISTINCT order_count)
    FROM product_counts pc2
    WHERE pc2.order_count > pc1.order_count
    ) < 3
    ORDER BY order_count DESC, name
    """)
    results = cursor.fetchall()
    top_products = {}
    for i, (name, pid, order_count) in enumerate(results, 1):
        top_products[i] = [name, pid, order_count]
    return top_products

def top_three_products_based_on_views(cursor):
    """
    List the top three products based on the number of views (includes ties)
    
    @return:
    - Dictionary containing product name, id, and view count for the top three products
    """

    cursor.execute("""
    WITH product_views AS (
    SELECT p.pid, p.name, COUNT(vp.pid) as view_count
    FROM products p JOIN viewedProduct vp ON p.pid = vp.pid
    GROUP BY p.pid, p.name)
    SELECT name, pid, view_count
    FROM product_views pv1
    WHERE (
    SELECT COUNT(DISTINCT view_count)
    FROM product_views pv2
    WHERE pv2.view_count > pv1.view_count
    ) < 3
    ORDER BY view_count DESC, name
    """)
    results = cursor.fetchall()
    top_products = {}
    for i, (name, pid, view_count) in enumerate(results, 1):
        top_products[i] = [name, pid, view_count]
    return top_products