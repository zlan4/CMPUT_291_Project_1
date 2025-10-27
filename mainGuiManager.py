from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from GUI import UI
import checkFormats
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

def open_customer_interface():
    """Opens the customer page."""
    pageNo = UI_OBJECT.stackedWidget.indexOf(UI_OBJECT.customerSearchPage)
    UI_OBJECT.stackedWidget.setCurrentIndex(pageNo)
    refresh_page()
    items = ...  # Fetch items from database to populate search filters                                         <------------------------------------ Database calls
    UI_OBJECT.accountBox.addItems(["Logout", "Exit"])
    UI_OBJECT.accountBox.currentIndexChanged.connect(customer_account_options)
    return

def customer_search_for_products():
    """Displays products based on search."""
    searchString = UI_OBJECT.customerSearchLineEdit.text().lower()
    products = ...# Fetch products from database based on searchString (returns list or Dictionary?)            <------------------------------------ Database calls
    products = ["Product 1", "Product 2", "Product 3"]  # Placeholder for fetched products
    for product in products:
        UI_OBJECT.customerSearchFormDisplay.addRow(QLabel(product))
        # UI_OBJECT.customerSearchFormDisplay.addRow(QLabel("---------------------"))
    return

def next_button_clicked():
    """Displays the next page of products."""


def customer_account_options():
    """Handles customer account options."""
    option = UI_OBJECT.accountBox.currentText()
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
        if isinstance(item, QComboBox):
            item.clear()
        if isinstance(item, QFormLayout):
            for row in range(item.rowCount()):
                item.removeRow(row)

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    UI_OBJECT = UI() 
    UI_OBJECT.show()
    establish_connections()
    start()
    app.exec() 