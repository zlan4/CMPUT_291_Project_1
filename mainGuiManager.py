from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from GUI import UI
import checkFormats
from functools import partial
import sys

def start():
    """Starts the application."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.loginPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    UI_OBJECT.loginErrorLabel.setText("")
    refresh_page()
    return

def signup_page():
    """Opens the signup page."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.signupPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    UI_OBJECT.signupErrorLabel.setText("")
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
    # Check if email already exists, if it exists, print error                                                  <------------------------------------ Database calls
    # Argumensts: email
    # If email doesn't exist, create new user in database                                                       <------------------------------------ Database calls
    # Arguments: username, email, password
    open_customer_interface()
    return

def check_login_info():
    """Verifies if the user exists and opens the respective interface."""
    username = UI_OBJECT.usernameLineEdit.text()
    password = UI_OBJECT.passwordLineEdit.text()
    if len(username) == 0 or len(password) == 0:
        UI_OBJECT.loginErrorLabel.setText("Please fill in all fields.")
        return
    valid_user = True   # Verify user credentials                                                               <------------------------------------ Database calls   
    # Arguments: username, password
    if not valid_user:
        UI_OBJECT.loginErrorLabel.setText("Invalid username or password.")
        return
    UI_OBJECT.loginErrorLabel.setText("")
    user_type = "customer"  # or "salesperson"  # This should be determined by actual login info                <------------------------------------ Database calls
    # Arguments: username, password
    if user_type == "customer":
        open_customer_interface()
    elif user_type == "salesperson":
        open_salesperson_interface()
    else:
        print("Error: Unknown user type")
    return

def open_customer_interface(refresh=True):
    """Opens the customer page."""
    print("Refresh:",refresh)
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.customerSearchPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    UI_OBJECT.accountBox.setCurrentIndex(-1)
    if refresh:
        refresh_page()
        UI_OBJECT.nextButton.setEnabled(False)
        UI_OBJECT.previousButton.setEnabled(False)
        for row in range(UI_OBJECT.customerSearchFormDisplay.rowCount()):
            UI_OBJECT.customerSearchFormDisplay.removeRow(0)
    items = ...  # Fetch items from database to populate search filters                                         <------------------------------------ Database calls
    # UI_OBJECT.accountBox.addItems(["Logout", "Exit"])
    UI_OBJECT.accountBox.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
    UI_OBJECT.accountBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.accountBox))
    return

def customer_search_for_products():
    """Displays products based on search."""
    searchString = UI_OBJECT.customerSearchLineEdit.text().lower()
    products = ...# Fetch products from database based on searchString (returns a Dictionary with productid as key)<------------------------------------ Database calls
    products = {1: "Product A", 2: "Product B", 3: "Product C", 4: "Product D", 5: "Product E", 6: "Product F", 7: "Product G", 8: "Product H", 9: "Product I", 10: "Product J", 11: "Product K"}
    totalPages = len(products) // 5 + (1 if len(products) % 5 != 0 else 0)
    UI_OBJECT.totalPageLabel.setText(str(totalPages))
    UI_OBJECT.of.setText("of")
    UI_OBJECT.PRODUCTS_LIST = []
    UI_OBJECT.current_page_num = 0
    separate_to_pages(products)
    display_next_page()
    return

def display_next_page():
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
    add_product_buttons()
    return

def display_previous_page():
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
    add_product_buttons()
    return

def add_product_buttons():
    """Adds product buttons to the form layout."""
    products = UI_OBJECT.PRODUCTS_LIST[UI_OBJECT.current_page_num - 1]
    for product in products:
        productButton = QPushButton(products[product])
        productButton.setMinimumSize(100, 75)
        productButton.clicked.connect(partial(view_product_details, product))
        UI_OBJECT.customerSearchFormDisplay.addRow(productButton)

def separate_to_pages(products, productsPerPage=5):
    """Separates products into dicts of 5 products each."""
    paginated_products = {}
    count = 0
    for i in products:
        paginated_products[i] = products[i]
        count += 1
        if count == productsPerPage:
            count = 0
            UI_OBJECT.PRODUCTS_LIST.append(paginated_products)
            paginated_products = {}
    if paginated_products is not None:
        UI_OBJECT.PRODUCTS_LIST.append(paginated_products)
    print(UI_OBJECT.PRODUCTS_LIST)
    return

def view_product_details(product_id):
    """Views the details of a selected product."""
    print("Product:",product_id)
    # get product details from database using product_id                                                            <------------------------------------ Database calls
    # Update viewedProduct table in database to add a record of this view                                            <------------------------------------ Database calls
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.productDetailsPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    UI_OBJECT.productDescComboBox.setCurrentIndex(-1)
    UI_OBJECT.productDescComboBox.currentIndexChanged.connect(lambda: customer_account_options(UI_OBJECT.productDescComboBox))
    print("Yay")
    product = {
        "id": "12345",
        "name": "Sample Product",
        "category": "Sample Category",
        "description": "This is a sample product description.",
        "price": "$19.99",
        "stock": "0"}
    UI_OBJECT.productNameLabel.setText(product["name"])
    UI_OBJECT.productDescriptionLabel.setText(product["description"])
    UI_OBJECT.idLineEdit.setText(product["id"])
    UI_OBJECT.categoryLineEdit.setText(product["category"])
    UI_OBJECT.priceLineEdit.setText(product["price"])
    UI_OBJECT.stockLineEdit.setText(product["stock"])
    if product["stock"] == "0":
        UI_OBJECT.itemCount.setText("0")
        UI_OBJECT.addItemCount.setEnabled(False)
        UI_OBJECT.subtractItemCount.setEnabled(False)
        UI_OBJECT.itemCount.setEnabled(False)
        UI_OBJECT.addToCartButton.setEnabled(False)
    return

def customer_account_options(comboBox):
    """Handles customer account options."""
    option = comboBox.currentText()
    if option == "Logout":
        start()
    elif option == "Exit":
        QApplication.quit()

def open_salesperson_interface():
    """Opens the salesperson interface."""
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

    # Product Details Page Connections
    UI_OBJECT.productDetailsBackButton.clicked.connect(lambda: open_customer_interface(False))
    UI_OBJECT.addItemCount.clicked.connect(lambda: UI_OBJECT.itemCount.setText(str(min(int(UI_OBJECT.itemCount.text())+1, int(UI_OBJECT.stockLineEdit.text())))))
    UI_OBJECT.subtractItemCount.clicked.connect(lambda: UI_OBJECT.itemCount.setText(str(max(1,int(UI_OBJECT.itemCount.text())-1))))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    UI_OBJECT = UI() 
    UI_OBJECT.show()
    establish_connections()
    start()
    app.exec() 