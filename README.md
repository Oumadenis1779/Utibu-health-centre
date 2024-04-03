# Utibu Health Project
Overview
Utibu Health is a Flask-based web application designed to facilitate the management of a health-related business. The application provides functionalities for managing customers, medications, orders, payments, statements, and shopping cart items.

# Features
# Customer Management
1.Registration: Customers can register by providing their details including first name, last name, email, phone number, address, username, and password.
  Login: Registered customers can log in using their username and password.
  Update and Delete: Customers can update and delete their profile information.
2.Medication Management
  Create, Read, Update, Delete (CRUD): Users can perform CRUD operations on medications, including creating, reading, updating, and deleting medication information.
  View Medication Stock: Users can view the current stock level of each medication.
3.Order Management
  Place Order: Customers can place orders for medications, specifying the quantity they require.
  View Orders: Users can view their order history, including details such as order date, status, and total amount.
  Update and Delete Orders: Users can update and delete their orders.
4.Payment Management
 Record Payments: Users can record payments for their orders, specifying the payment date, amount paid, and payment method.
 View Payments: Users can view their payment history, including details such as payment date, amount paid, and payment method.
 Update and Delete Payments: Users can update and delete their payment records.
5.Statement Management
 Generate Statements: The system generates statements for customers, indicating the amount due and payment status.
 View Statements: Customers can view their statement history, including details such as statement date, amount due, and payment status.
 Update and Delete Statements: Users can update and delete their statement records.
6.Shopping Cart
 Add to Cart: Users can add medications to their shopping cart, specifying the quantity required.
 View Cart: Users can view the items in their shopping cart, including details such as medication name, quantity, and subtotal.
 Update and Remove from Cart: Users can update the quantity of items in the cart or remove them altogether.

# Technologies Used
Flask: Flask is used as the web framework for developing the application.
SQLAlchemy: SQLAlchemy is utilized as the ORM (Object-Relational Mapping) tool for database operations.
JWT (JSON Web Tokens): JWT is employed for user authentication and authorization.
SQLite: SQLite is the database management system used for storing application data.
Flask-Migrate: Flask-Migrate is used for handling database migrations.
Installation
To run the application locally, follow these steps:

Clone the repository: git clone <repository_url>
Install the required dependencies: pip install -r requirements.txt
Set up the database by running migrations: flask db upgrade
Run the Flask application: python app.py
Access the application in a web browser at http://localhost:5000
