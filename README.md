# CMPUT 291 Group Project 1 - Fall 2025  
This application is similar to an online shopping system with two end-users, customers and salespeople. Users have the ability to browse different products available for purchase, create a secure account, search for items, manage their shopping cart, check out, and view past orders. Salespeople are able to update product information, generate weekly sales reports, and view the best-selling items. To facilitate these user and application interactions, the graphical user interface (GUI) was built using PyQt6. The system functionalities were implemented using Python code integrated with SQLite3. Important information such as product and user details was stored in a database, which was accessed at various times throughout the program to check for things like username and password validity, fetch product details based on searched keywords, record new user signups or other updates, and ensure that those data remain persistent and accessible even after the application has finished running or has been rebooted.

# Accessing Virtual Environment
1) Create the virtual environment using Python >=3.11
- MacOS + Linux
`python3 -m venv <envname>`
- Windows
`python -m venv <envname>`

2) Activate the virtual environment
- MacOS + Linux
`source <envname>/bin/activate`
- Windows Command Prompt
`<envname>/Scripts/activate.bat`
- Windows PowerShell
`./<envname>/Scripts/activate.ps1`

3) Make sure to add your virtual environment to the .gitignore file

4) Install dependencies
`pip install -r requirements.txt`
