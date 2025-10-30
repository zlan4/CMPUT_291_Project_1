from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from GUI import UI
import checkFormats
from functools import partial
import popupFile
import sys
import sqlite3
import dbManager

def start():
    """Starts the application."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.loginPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    UI_OBJECT.usernameLineEdit.setFocus()
    UI_OBJECT.loginErrorLabel.setText("")
    refresh_page()
    UI_OBJECT.saveChangesButton.setVisible(True)
    UI_OBJECT.addToCartButton.setVisible(True)
    UI_OBJECT.itemCount.setVisible(True)
    UI_OBJECT.addItemCount.setVisible(True)
    UI_OBJECT.subtractItemCount.setVisible(True)
    UI_OBJECT.productDescComboBox.setVisible(True)
    UI_OBJECT.salesComboBox.setVisible(True)
    return

def signup_page():
    """Opens the signup page."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.signupPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    UI_OBJECT.signupErrorLabel.setText("")
    UI_OBJECT.signupUsernameLineEdit.setFocus()
    UI_OBJECT.signupUsernameLineEdit.returnPressed.connect(UI_OBJECT.signupEmailLineEdit.setFocus)
    UI_OBJECT.signupEmailLineEdit.returnPressed.connect(UI_OBJECT.signupPasswordLineEdit.setFocus)
    UI_OBJECT.signupPasswordLineEdit.returnPressed.connect(UI_OBJECT.signupConfirmPasswordLineEdit.setFocus)
    UI_OBJECT.signupConfirmPasswordLineEdit.returnPressed.connect(signup_button_clicked)
    refresh_page()
    return

def signup_button_clicked():
    """Checks if the signup info provided is valid."""
    username = UI_OBJECT.signupUsernameLineEdit.text()
    email = UI_OBJECT.signupEmailLineEdit.text().lower()
    password = UI_OBJECT.signupPasswordLineEdit.text()
    confirm_password = UI_OBJECT.signupConfirmPasswordLineEdit.text()
    if len(username) == 0 or len(password) == 0 or len(confirm_password) == 0 or len(email) == 0:
        UI_OBJECT.signupErrorLabel.setText("Please fill in all fields.")
        return
    if not checkFormats.is_valid_email(email):
        UI_OBJECT.signupErrorLabel.setText("Invalid email format.")
        return
    if password != confirm_password:
        UI_OBJECT.signupErrorLabel.setText("Passwords do not match.")
        return
    UI_OBJECT.signupErrorLabel.setText("")
    check, user_id = dbManager.register_user(UI_OBJECT.cursor, username, email, password)
    UI_OBJECT.conn.commit()
    if not check:
        UI_OBJECT.signupErrorLabel.setText("An account with the email already exists")
        return
    UI_OBJECT.user_id = user_id
    UI_OBJECT.user_mode = 'customer'
    open_customer_interface()
    return

def check_login_info():
    """Verifies if the user exists and opens the respective interface."""
    username = UI_OBJECT.usernameLineEdit.text()
    password = UI_OBJECT.passwordLineEdit.text()
    if len(username) == 0 or len(password) == 0:
        UI_OBJECT.loginErrorLabel.setText("Please fill in all fields.")
        return
    check, user_details = dbManager.check_login(UI_OBJECT.cursor, username, password)
    if not check:
        UI_OBJECT.loginErrorLabel.setText("Invalid username or password.")
        return
    UI_OBJECT.loginErrorLabel.setText("")
    user_type = user_details[-1]
    UI_OBJECT.user_id = user_details[0]
    if user_type == "customer": 
        open_customer_interface()
        UI_OBJECT.user_mode = 'customer'
    elif user_type == "sales":
        open_salesperson_interface()
        UI_OBJECT.user_mode = 'salesperson'
    else:
        print("Error: Unknown user type")
    return

def open_customer_interface(refresh=True, type = "default"):
    """Opens the customer page."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.customerSearchPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    if refresh:
        refresh_page()
        UI_OBJECT.nextButton.setEnabled(False)
        UI_OBJECT.previousButton.setEnabled(False)
        for row in range(UI_OBJECT.customerSearchFormDisplay.rowCount()):
            UI_OBJECT.customerSearchFormDisplay.removeRow(0)
    UI_OBJECT.accountBox.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
    if type == "My Orders":
        UI_OBJECT.customerSearchLineEdit.setVisible(False)
        UI_OBJECT.myOrdersLabel.setVisible(True)
        UI_OBJECT.myOrdersBackButton.setVisible(True)
        check, products = dbManager.view_past_orders(UI_OBJECT.cursor, UI_OBJECT.user_id)
        if not check:
            print("Error retrieving orders")
            return
        totalPages = len(products) // 5 + (1 if len(products) % 5 != 1 else 1)
        UI_OBJECT.totalPageLabel.setText(str(totalPages))
        UI_OBJECT.of.setText("of")
        UI_OBJECT.PRODUCTS_LIST = []
        UI_OBJECT.current_page_num = 0
        separate_to_pages(products, mode= "Orders")
        display_next_page(False)
    else:
        UI_OBJECT.customerSearchLineEdit.setVisible(True)
        UI_OBJECT.myOrdersLabel.setVisible(False)
        UI_OBJECT.myOrdersBackButton.setVisible(False)
    return

def customer_search_for_products(products = False):
    """Displays products based on search."""
    searchString = UI_OBJECT.customerSearchLineEdit.text().lower()
    if not products:
        check, products = dbManager.search_product(UI_OBJECT.cursor, searchString)
        if not check:
            for row in range(UI_OBJECT.customerSearchFormDisplay.rowCount()):
                UI_OBJECT.customerSearchFormDisplay.removeRow(0)
            popupFile.info_popup("No products found")
    totalPages = len(products) // 5 + (1 if len(products) % 5 != 1 else 1)
    UI_OBJECT.totalPageLabel.setText(str(totalPages))
    UI_OBJECT.of.setText("of")
    UI_OBJECT.PRODUCTS_LIST = []
    UI_OBJECT.current_page_num = 0
    separate_to_pages(products)
    display_next_page()
    return

def display_next_page(productMode = True):
    """Displays the next page of products."""
    if UI_OBJECT.current_page_num+1 > len(UI_OBJECT.PRODUCTS_LIST):
        return
    UI_OBJECT.current_page_num += 1
    if UI_OBJECT.current_page_num in [0,1] :
        UI_OBJECT.previousButton.setEnabled(False)
    else:
        UI_OBJECT.previousButton.setEnabled(True)
    if UI_OBJECT.current_page_num == len(UI_OBJECT.PRODUCTS_LIST):
        UI_OBJECT.nextButton.setEnabled(False)
    else:
        UI_OBJECT.nextButton.setEnabled(True)
    for row in range(UI_OBJECT.customerSearchFormDisplay.rowCount()):
        UI_OBJECT.customerSearchFormDisplay.removeRow(0)
    UI_OBJECT.currentPageLabel.setText(str(UI_OBJECT.current_page_num))
    add_product_buttons(productMode)
    return

def display_previous_page(productMode = True):
    """Displays the previous page of products."""
    if UI_OBJECT.current_page_num-1 < 1:
        return
    UI_OBJECT.current_page_num -= 1
    if UI_OBJECT.current_page_num in [0,1] :
        UI_OBJECT.previousButton.setEnabled(False)
    else:
        UI_OBJECT.previousButton.setEnabled(True)
    if UI_OBJECT.current_page_num == len(UI_OBJECT.PRODUCTS_LIST):
        UI_OBJECT.nextButton.setEnabled(False)
    else:
        UI_OBJECT.nextButton.setEnabled(True)
    for row in range(UI_OBJECT.customerSearchFormDisplay.rowCount()):
        UI_OBJECT.customerSearchFormDisplay.removeRow(0)
    UI_OBJECT.currentPageLabel.setText(str(UI_OBJECT.current_page_num))
    add_product_buttons(productMode)
    return

def add_product_buttons(productMode):
    """Adds product buttons to the form layout."""
    products = UI_OBJECT.PRODUCTS_LIST[UI_OBJECT.current_page_num - 1]
    for product in products:
        productButton = QPushButton(products[product])
        productButton.setMinimumSize(100, 75)
        if productMode:
            productButton.clicked.connect(partial(view_product_details, product))
        else:
            productButton.clicked.connect(partial(view_order_lines, productButton.text()))
        UI_OBJECT.customerSearchFormDisplay.addRow(productButton)

def separate_to_pages(products, productsPerPage=5, mode = "default"):
    """Separates products into dicts of 5 products each."""
    paginated_products = {}
    count = 0
    if mode == "default":
        for i in products:
            paginated_products[i[0]] = str(i[0]) + ": " + i[1]
            count += 1
            if count == productsPerPage:
                count = 0
                UI_OBJECT.PRODUCTS_LIST.append(paginated_products)
                paginated_products = {}
    else:
        check, totalAmount = dbManager.grand_total(UI_OBJECT.cursor, products[0][0])
        if not check:
            print("Error retrieving total amount")
            return
        for i in products:
            paginated_products[i[0]] = str(i[0]) + ": " + i[3] + ", "+i[4]+", "+str(totalAmount)
            count += 1
            if count == productsPerPage:
                count = 0
                UI_OBJECT.PRODUCTS_LIST.append(paginated_products)
                paginated_products = {}
    if paginated_products is not None:
        UI_OBJECT.PRODUCTS_LIST.append(paginated_products)
    return

def view_product_details(product_id):
    """Views the details of a selected product."""
    # get product details from database using product_id                                                            <------------------------------------ Database calls
    # Update viewedProduct table in database to add a record of this view                                            <------------------------------------ Database calls
    check, product = dbManager.product_details(UI_OBJECT.cursor, product_id)
    if not check:
        return
    UI_OBJECT.saveChangesButton.setVisible(False)
    UI_OBJECT.salesComboBox.setVisible(False)
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.productDetailsPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    UI_OBJECT.productDescComboBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.productDescComboBox))
    UI_OBJECT.productNameLabel.setText(str(product[1]))
    UI_OBJECT.productDescriptionLabel.setText(product[5])
    UI_OBJECT.idLineEdit.setText(str(product[0]))
    UI_OBJECT.idLineEdit.setEnabled(False)
    UI_OBJECT.categoryLineEdit.setText(product[2])
    UI_OBJECT.categoryLineEdit.setEnabled(False)
    UI_OBJECT.priceLineEdit.setText(str(product[3]))
    UI_OBJECT.priceLineEdit.setEnabled(False)
    UI_OBJECT.stockLineEdit.setText(str(product[4]))
    UI_OBJECT.stockLineEdit.setEnabled(False)
    UI_OBJECT.itemCount.setText("1")
    if str(product[4]) == "0":
        UI_OBJECT.itemCount.setText("0")
        UI_OBJECT.addItemCount.setEnabled(False)
        UI_OBJECT.subtractItemCount.setEnabled(False)
        UI_OBJECT.itemCount.setEnabled(False)
        UI_OBJECT.addToCartButton.setEnabled(False)
    return

def back_from_details_page():
    """Returns to the customer or salesperson interface from product details page."""
    if UI_OBJECT.user_mode == "salesperson":
        look_up_products_salesperson()
    else:
        open_customer_interface(False)
    return

def add_item_to_cart():
    """Adds the selected item to the cart."""
    product_id = UI_OBJECT.idLineEdit.text()
    quantity = UI_OBJECT.itemCount.text()
    # Add item to cart in database                                                                                     <------------------------------------ Database calls
    # Arguments: product_id, quantity
    dbManager.add_to_cart(UI_OBJECT.cursor, UI_OBJECT.user_id, 1, )
    return

def view_cart():
    """Views the customer's cart."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.cartPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    # Fetch cart items from database as a dictionary                                            <------------------------------------ Database calls
    # Arguments: UI_OBJECT.customer_id
    for i in range(UI_OBJECT.cartViewGridLayout.rowCount()):
        for j in  range(UI_OBJECT.cartViewGridLayout.columnCount()):
            item = UI_OBJECT.cartViewGridLayout.itemAtPosition(i, j)
            if item:
                widget = item.widget()
                if widget:
                    UI_OBJECT.cartViewGridLayout.removeWidget(widget)
                    widget.deleteLater()
    cart_items = {1: ["Product A", 2, 19.98], 2: ["Product B", 1, 9.99], 3: ["Product C", 3, 29.97], 4: ["Product D", 1, 14.99], 5: ["Product E", 2, 39.98], 6: ["Product F", 1, 24.99], 7: ["Product G", 4, 79.96], 8: ["Product H", 2, 49.98], 9: ["Product I", 1, 59.99], 10: ["Product J", 3, 89.97], 11: ["Product K", 2, 69.98]}
    row = 0
    for key, value in cart_items.items():
        name, quantity, price = value[0], value[1], value[2]
        price = float(price)
        itemNameLabel = QLabel(name)
        itemNameLabel.setMinimumHeight(50)
        itemNameLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        UI_OBJECT.cartViewGridLayout.addWidget(itemNameLabel, row, 0)

        qtySpinBox = QSpinBox()
        # get product details from database using product_id                                                            <------------------------------------ Database calls
        # Same as the one in view_product_details function
        product = {
            "id": "12345",
            "name": "Sample Product",
            "category": "Sample Category",
            "description": "This is a sample product description.",
            "price": "19.99",
            "stock": "10"}
        maxValue = int(product["stock"])
        qtySpinBox.setRange(1, maxValue)
        qtySpinBox.setValue(quantity)
        UI_OBJECT.cartViewGridLayout.addWidget(qtySpinBox, row, 1)

        totalLabel = QLabel(f"${price*quantity:.2f}")
        UI_OBJECT.cartViewGridLayout.addWidget(totalLabel, row, 2)
        qtySpinBox.valueChanged.connect(partial(on_quantity_change, qtySpinBox, price=price, totalLabel=totalLabel))

        deleteBtn = QPushButton("Delete")
        UI_OBJECT.cartViewGridLayout.addWidget(deleteBtn, row, 3)
        deleteBtn.clicked.connect(partial(on_delete_clicked, row, layout = UI_OBJECT.cartViewGridLayout))
        update_total_quantity()
        row += 1
    return

def on_quantity_change(currentSpinBox, price, totalLabel):
    # Update quantity in cart in database                                                            <------------------------------------ Database calls
    # Arguments: itemid, value
    new_quantity = currentSpinBox.value()
    totalLabel.setText(f"${price*new_quantity:.2f}")
    update_total_quantity()

def update_total_quantity():
    total = 0
    for i in range(UI_OBJECT.cartViewGridLayout.rowCount()):
        if UI_OBJECT.cartViewGridLayout.itemAtPosition(i, 2):
            label = UI_OBJECT.cartViewGridLayout.itemAtPosition(i, 2).widget()
            total += float(label.text()[1:])
    UI_OBJECT.totalPriceLabel.setText("$"+str(round(total, 2)))
    if float(UI_OBJECT.totalPriceLabel.text()[1:]) == float(0):
        UI_OBJECT.checkoutButton.setEnabled(False)
    else:
        UI_OBJECT.checkoutButton.setEnabled(True)

def on_delete_clicked(rowNum, layout):
    for j in  range(4):
        item = layout.itemAtPosition(rowNum, j)
        if item:
            widget = item.widget()
            if widget:
                widget.deleteLater()
                widget.setParent(None)
    # Delete item from cart in database                                                            <------------------------------------ Database calls
        # Arguments: itemid
    update_total_quantity()

def checkout_button_clicked():
    check, address = popupFile.input_popup("Please enter shipping address")
    if not check:
        return
    confirm = popupFile.confirm_popup(f"Confirm placing order to {address}")
    if not confirm:
        return
    # create a new order                                                    <------------------------------------ Database calls
    for i in range(UI_OBJECT.cartViewGridLayout.rowCount()):
        for j in  range(UI_OBJECT.cartViewGridLayout.columnCount()):
            item = UI_OBJECT.cartViewGridLayout.itemAtPosition(i, j)
            if item:
                widget = item.widget()
                if widget:
                    UI_OBJECT.cartViewGridLayout.removeWidget(widget)
                    widget.deleteLater()
    update_total_quantity()
    popupFile.info_popup("Order has been placed")

def view_order_lines(buttonText):
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.orderDetailsPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    ono = int(buttonText.split(":")[0])
    otherDetails = buttonText.split(":")[1]
    odate, oaddress, ototalAmount = otherDetails.split(",")
    UI_OBJECT.orderNoDisplay.setText(str(ono))
    UI_OBJECT.orderDateDisplay.setText(str(odate))
    UI_OBJECT.shippingAddressDisplay.setText(str(oaddress))
    UI_OBJECT.totalAmountDisplay.setText("Total: $"+str(ototalAmount))
    check, order_lines = dbManager.view_order_details(UI_OBJECT.cursor, ono)
    if not check:
        popupFile.info_popup("Error retrieving order lines")
        return
    add_order_lines_to_layout(order_lines)

def add_order_lines_to_layout(order_lines):
    for row in range(UI_OBJECT.orderLinesDisplay.rowCount()):
        UI_OBJECT.orderLinesDisplay.removeRow(0)
    count = 0
    for item in order_lines:
        count += 1
        check, itemDetails = dbManager.product_details(UI_OBJECT.cursor, item[2])
        if not check:
            popupFile.info_popup("Error retrieving product details")
            return
        title = QLabel("Product "+ str(count))
        title.setStyleSheet("font-weight: bold; font-size: 11px;")
        UI_OBJECT.orderLinesDisplay.addRow(title)
        UI_OBJECT.orderLinesDisplay.addRow(QLabel("Product Name: "), QLabel(itemDetails[1]))
        UI_OBJECT.orderLinesDisplay.addRow(QLabel("Category: "), QLabel(itemDetails[2]))
        UI_OBJECT.orderLinesDisplay.addRow(QLabel("Quantity: "), QLabel(str(item[3])))
        UI_OBJECT.orderLinesDisplay.addRow(QLabel("Unit Price: "), QLabel(str(item[4])))
        UI_OBJECT.orderLinesDisplay.addRow(QLabel("Total: "), QLabel(str(round(item[3]*item[4], 2))))

def customer_account_options(comboBox):
    """Handles customer account options."""
    option = comboBox.currentText()
    comboBox.setCurrentIndex(-1)
    if option == "Logout":
        start()
    elif option == "Exit":
        QApplication.quit()
    elif option == "Cart":
        view_cart()
    elif option == "My Orders":
        open_customer_interface(type = "My Orders")

## Salesperson Functions ##--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def open_salesperson_interface():
    """Opens the salesperson interface."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.salesHomePage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    return

def look_up_products_salesperson():
    """Allows salesperson to look up products."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.salesProductLookupPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    UI_OBJECT.productSearchLineEdit.setFocus()
    refresh_page()
    return

def view_product_details_salesperson():
    """Shows the product data from the product_id entered by the salesperson."""
    UI_OBJECT.productDescComboBox.setVisible(False)
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.productDetailsPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    product_id = UI_OBJECT.productSearchLineEdit.text()
    # get product details from database using product_id.                           <------------------------------------ Database calls
    # same as the one in view_product_details function, don't have to create again
    product = {
        "id": "12345",
        "name": "Sample Product",
        "category": "Sample Category",
        "description": "This is a sample product description.",
        "price": "19.99",
        "stock": "10"}
    UI_OBJECT.productNameLabel.setText(product["name"])
    UI_OBJECT.productDescriptionLabel.setText(product["description"])
    UI_OBJECT.idLineEdit.setText(product["id"])
    UI_OBJECT.idLineEdit.setEnabled(False)
    UI_OBJECT.categoryLineEdit.setText(product["category"])
    UI_OBJECT.categoryLineEdit.setEnabled(False)
    UI_OBJECT.priceLineEdit.setText(product["price"])
    UI_OBJECT.priceLineEdit.returnPressed.connect(UI_OBJECT.stockLineEdit.setFocus)
    UI_OBJECT.stockLineEdit.setText(product["stock"])
    UI_OBJECT.stockLineEdit.returnPressed.connect(save_product_changes)

    # Hide cart related UI elements for salesperson view
    UI_OBJECT.addItemCount.setVisible(False)
    UI_OBJECT.subtractItemCount.setVisible(False)
    UI_OBJECT.itemCount.setVisible(False)
    UI_OBJECT.addToCartButton.setVisible(False)
    return

def save_product_changes():
    """Saves changes made to the product details by the salesperson."""
    product_id = UI_OBJECT.idLineEdit.text()
    new_price = UI_OBJECT.priceLineEdit.text()
    new_stock = UI_OBJECT.stockLineEdit.text()
    product = ...# get product details from database using product_id                                                            <------------------------------------ Database calls
    # Same as the one in view_product_details function, don't have to create again
    if product["price"] == new_price and product["stock"] == new_stock:
        return
    confirmation = popupFile.confirm_popup(f'Are you sure you want to save changes product: {product_id}?')
    if not confirmation:
        return
    print(new_price, new_stock)
    # Update product details in database                                                                         <------------------------------------ Database calls
    # Arguments: product_id, new_price, new_stock
    return

def view_sales_report_clicked():
    """Displays the sales report fo the last week."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.weeklySalesReportPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    for row in range(UI_OBJECT.salesReportFormLayout.rowCount()):
        UI_OBJECT.salesReportFormLayout.removeRow(0)
    # Fetch sales report data from database as a dictionary                                        <------------------------------------ Database calls
    weekly_sales = {
        "distinct_orders": 150,
        "distint_products_sold": 300,
        "distinct_customers_with_purchases": 120,
        "average_amount_per_customer": 250.75,
        "total_sales_amount": 30150.00
    }
    for key, value in weekly_sales.items():
        label = QLabel(key.replace("_", " ").title() + ":")
        label.setMinimumHeight(50)
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        UI_OBJECT.salesReportFormLayout.addRow(label, QLabel(str(value)))
    return

def display_top_products():
    """Displays the top selling products."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.topProductsPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    for row in range(UI_OBJECT.topProductsFormLayout.rowCount()):
        UI_OBJECT.topProductsFormLayout.removeRow(0)

def check_box_toggled(checkbox):
    """Handles checkbox toggles for top products display."""
    if checkbox == UI_OBJECT.distinctOrdersCheckBox:
        UI_OBJECT.totalViewsCheckBox.blockSignals(True)
        UI_OBJECT.totalViewsCheckBox.setChecked(False)
        UI_OBJECT.totalViewsCheckBox.blockSignals(False)
        add_top_products_by_distinct_orders()
    elif checkbox == UI_OBJECT.totalViewsCheckBox:
        print("Total Views Checked")
        UI_OBJECT.distinctOrdersCheckBox.blockSignals(True)
        UI_OBJECT.distinctOrdersCheckBox.setChecked(False)
        UI_OBJECT.distinctOrdersCheckBox.blockSignals(False)
        add_top_products_by_total_views()

def add_top_products_by_distinct_orders():
    """Adds top products by distinct orders to the UI."""
    for row in range(UI_OBJECT.topProductsFormLayout.rowCount()):
        UI_OBJECT.topProductsFormLayout.removeRow(0)
    # Fetch top 3 products by distinct orders from database as a dictionary                   <------------------------------------ Database calls
    top_products = {
        1: ["Product A", 120],
        2: ["Product B", 110],
        3: ["Product C", 100],
    }
    for key, value in top_products.items():
        name, orders = value[0], value[1]
        label = QLabel(f"{key}. {name} - {orders} distinct orders")
        label.setMinimumHeight(50)
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        UI_OBJECT.topProductsFormLayout.addRow(label)
    return

def add_top_products_by_total_views():
    """Adds top 3 products by total views to the UI."""
    for row in range(UI_OBJECT.topProductsFormLayout.rowCount()):
        UI_OBJECT.topProductsFormLayout.removeRow(0)
    # Fetch top 3 products by total views from database as a dictionary                        <------------------------------------ Database calls
    top_products = {
        1: ["Product X", 500],
        2: ["Product Y", 450],
        3: ["Product Z", 400],
    }
    for key, value in top_products.items():
        name, views = value[0], value[1]
        label = QLabel(f"{key}. {name} - {views} total views")
        label.setMinimumHeight(50)
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        UI_OBJECT.topProductsFormLayout.addRow(label)
    return

def refresh_page():
    """Refreshes the current page."""
    current_index = UI_OBJECT.stackedWidget.currentIndex()
    answer = UI_OBJECT.stackedWidget.widget(current_index).findChildren(QWidget)
    for item in answer:
        if isinstance(item, QLineEdit):
            item.setText("")

def establish_connections():
    """Creates connections between buttons. Add all connections here."""
    #Login Page Connections
    UI_OBJECT.loginButton.clicked.connect(check_login_info)
    UI_OBJECT.exitButton.clicked.connect(QApplication.quit)
    UI_OBJECT.goToSignupPage.clicked.connect(signup_page)
    UI_OBJECT.usernameLineEdit.returnPressed.connect(UI_OBJECT.passwordLineEdit.setFocus)
    UI_OBJECT.passwordLineEdit.returnPressed.connect(check_login_info)

    #Signup Page Connections
    UI_OBJECT.goToLoginPage.clicked.connect(start)
    UI_OBJECT.signupButton.clicked.connect(signup_button_clicked)
    UI_OBJECT.signupExitButton.clicked.connect(QApplication.quit)

    #Customer Page Connections
    UI_OBJECT.customerSearchLineEdit.returnPressed.connect(customer_search_for_products)
    UI_OBJECT.nextButton.clicked.connect(display_next_page)
    UI_OBJECT.previousButton.clicked.connect(display_previous_page)
    UI_OBJECT.accountBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.accountBox))
    UI_OBJECT.myOrdersBackButton.clicked.connect(lambda: open_customer_interface(refresh = True))

    # Product Details Page Connections
    UI_OBJECT.productDetailsBackButton.clicked.connect(lambda: back_from_details_page())
    UI_OBJECT.addItemCount.clicked.connect(lambda: UI_OBJECT.itemCount.setText(str(min(int(UI_OBJECT.itemCount.text())+1, int(UI_OBJECT.stockLineEdit.text())))))
    UI_OBJECT.subtractItemCount.clicked.connect(lambda: UI_OBJECT.itemCount.setText(str(max(1,int(UI_OBJECT.itemCount.text())-1))))
    UI_OBJECT.addToCartButton.clicked.connect(add_item_to_cart)
    UI_OBJECT.salesComboBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.salesComboBox))

    # Cart Page Connections
    UI_OBJECT.cartPageHomeButton.clicked.connect(lambda: open_customer_interface(True))
    UI_OBJECT.cartPageComboBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.cartPageComboBox))
    UI_OBJECT.checkoutButton.clicked.connect(checkout_button_clicked)

    # Salesperson Page Connections
    UI_OBJECT.salesLogoutButton.clicked.connect(start)
    UI_OBJECT.salesExitButton.clicked.connect(QApplication.quit)
    UI_OBJECT.salesViewProductsButton.clicked.connect(look_up_products_salesperson)
    UI_OBJECT.salesReportViewButton.clicked.connect(view_sales_report_clicked)
    UI_OBJECT.salesTopProductsButton.clicked.connect(display_top_products)

    # Salesperson Product Lookup Page Connections
    UI_OBJECT.salesProductLookupBackButton.clicked.connect(open_salesperson_interface)
    UI_OBJECT.salesLookupComboBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.salesLookupComboBox))
    UI_OBJECT.productSearchEnterButton.clicked.connect(view_product_details_salesperson)
    UI_OBJECT.productSearchLineEdit.returnPressed.connect(view_product_details_salesperson)
    UI_OBJECT.saveChangesButton.clicked.connect(save_product_changes)

    # Sales Report Page Connections
    UI_OBJECT.weeklySalesReportBackButton.clicked.connect(open_salesperson_interface)
    UI_OBJECT.weeklySalesReportComboBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.weeklySalesReportComboBox))

    # Top Products Page Connections
    UI_OBJECT.topProductsBackButton.clicked.connect(open_salesperson_interface)
    UI_OBJECT.topProductsComboBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.topProductsComboBox))
    UI_OBJECT.distinctOrdersCheckBox.stateChanged.connect(lambda: check_box_toggled(UI_OBJECT.distinctOrdersCheckBox))
    UI_OBJECT.totalViewsCheckBox.stateChanged.connect(lambda: check_box_toggled(UI_OBJECT.totalViewsCheckBox))

    # Order Details Page Connections
    UI_OBJECT.orderDetailsHomeButton.clicked.connect(lambda: open_customer_interface(True))
    UI_OBJECT.orderDetailsComboBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.orderDetailsComboBox))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    UI_OBJECT = UI()
    UI_OBJECT.show()
    UI_OBJECT.conn = sqlite3.connect(sys.argv[1])
    UI_OBJECT.cursor = UI_OBJECT.conn.cursor() 
    establish_connections()
    start()
    app.exec() 