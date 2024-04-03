from flask import Flask, request, jsonify, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from models import db, Customer, Medication, Orders, OrderItems, Payments,Statements,CartItem
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash
from datetime import datetime
# from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utibu_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = os.environ.get('secret_key')

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.json

# Check if a customer with the same username or email already exists
    existing_customer = Customer.query.filter(
        (Customer.Username == data['Username']) |
        (Customer.Email == data['Email'])
    ).first()
    
    if existing_customer:
        return jsonify({'error': 'Customer with the same username or email already exists'}), 400

 # Add the new customer to the database
    new_customer = Customer(
        FirstName=data['FirstName'],
        LastName=data['LastName'],
        Email=data['Email'],
        Phone=data['Phone'],
        Address=data.get('Address'),
        Username=data['Username']
    )
    new_customer.set_password(data['Password'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer added successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Query the database for the user with the provided username
    user = Customer.query.filter_by(Username=username).first()

    # Check if the user exists and the provided password is correct
    if user and user.check_password(password):
        # Generate JWT token
        access_token = create_access_token(identity=user.Username)
        return jsonify({'message': 'Login successful',  'access_token': access_token, 'email': user.Email, 'customer_id': user.CustomerID }), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    result = []
    for customer in customers:
        result.append({
            'CustomerID': customer.CustomerID,
            'FirstName': customer.FirstName,
            'LastName': customer.LastName,
            'Email': customer.Email,
            'Phone': customer.Phone,
            'Address': customer.Address,
            'Username': customer.Username
        })
    return jsonify(result)

@app.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify({
        'CustomerID': customer.CustomerID,
        'FirstName': customer.FirstName,
        'LastName': customer.LastName,
        'Email': customer.Email,
        'Phone': customer.Phone,
        'Address': customer.Address,
        'Username': customer.Username
    })

@app.route('/customer/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'}), 200

@app.route('/customer/<int:customer_id>', methods=['PATCH'])
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.json
    if 'FirstName' in data:
        customer.FirstName = data['FirstName']
    if 'LastName' in data:
        customer.LastName = data['LastName']
    if 'Email' in data:
        customer.Email = data['Email']
    if 'Phone' in data:
        customer.Phone = data['Phone']
    if 'Address' in data:
        customer.Address = data['Address']
    if 'Username' in data:
        customer.Username = data['Username']
    if 'Password' in data:
        customer.set_password(data['Password'])

    db.session.commit()
    return jsonify({'message': 'Customer updated successfully'}), 200

# @app.route('/')
# def hello():
#     return 'Hello, Utibu Health!'

# Route to create a new medication
@app.route('/medications', methods=['POST'])
def create_medication():
    data = request.get_json()
    existing_medication = Medication.query.filter_by(Name=data['Name']).first()
    if existing_medication:
        return jsonify({'error': 'Medication already exists'}), 400

    new_medication = Medication(Name=data['Name'], Description=data['Description'], StockLevel=data['StockLevel'], PricePerUnit=data['PricePerUnit'])
    db.session.add(new_medication)
    db.session.commit()
    return jsonify({'message': 'Medication created successfully'}), 201

# Route to retrieve all medications
@app.route('/medications', methods=['GET'])
def get_medications():
    medications = Medication.query.all()
    output = []
    for medication in medications:
        medication_data = {
            'MedicationID': medication.MedicationID,
            'Name': medication.Name,
            'Description': medication.Description,
            'StockLevel': medication.StockLevel,
            'PricePerUnit': medication.PricePerUnit
        }
        output.append(medication_data)
    return jsonify({'medications': output})

# Route to retrieve a specific medication by its ID
@app.route('/medications/<int:medication_id>', methods=['GET'])
def get_medication(medication_id):
    medication = Medication.query.get_or_404(medication_id)
    medication_data = {
        'MedicationID': medication.MedicationID,
        'Name': medication.Name,
        'Description': medication.Description,
        'StockLevel': medication.StockLevel,
        'PricePerUnit': medication.PricePerUnit
    }
    return jsonify(medication_data)

# Route to update a medication
@app.route('/medications/<int:medication_id>', methods=['PUT'])
def update_medication(medication_id):
    medication = Medication.query.get_or_404(medication_id)
    data = request.get_json()
    medication.Name = data['Name']
    medication.Description = data['Description']
    medication.StockLevel = data['StockLevel']
    medication.PricePerUnit = data['PricePerUnit']
    db.session.commit()
    return jsonify({'message': 'Medication updated successfully'})

# Route to delete a medication
@app.route('/medications/<int:medication_id>', methods=['DELETE'])
def delete_medication(medication_id):
    medication = Medication.query.get_or_404(medication_id)
    db.session.delete(medication)
    db.session.commit()
    return jsonify({'message': 'Medication deleted successfully'})


# @app.route('/order', methods=['POST'])
# def order_medication():
#     data = request.json
#     medication_name = data.get('medication_name')
#     quantity = data.get('quantity')
#     customer_id = data.get('customer_id')

#     if not medication_name or not quantity or not customer_id:
#         return jsonify({'error': 'Medication name, quantity, and customer ID are required'}), 400

#     # Check if medication is available in stock
#     medication = Medication.query.filter_by(Name=medication_name).first()
#     if not medication:
#         return jsonify({'error': f'Medication {medication_name} not found'}), 404

#     if medication.StockLevel < quantity:
#         return jsonify({'error': f'Insufficient quantity of {medication_name} in stock'}), 400

#     # Retrieve customer details
#     customer = Customer.query.get(customer_id)
#     if not customer:
#         return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404

#     # Create a new order
#     order = Orders(CustomerID=customer_id, OrderDate=datetime.now(), Status='Pending', TotalAmount=0.0)
#     db.session.add(order)
#     db.session.commit()

#     # Create order item
#     order_item = OrderItems(OrderID=order.OrderID, MedicationID=medication.MedicationID, Quantity=quantity, Subtotal=quantity * medication.PricePerUnit)
#     db.session.add(order_item)
#     db.session.commit()

#     # Update total amount in order
#     order.TotalAmount = order_item.Subtotal
#     db.session.commit()

#     # Update stock level
#     medication.StockLevel -= quantity
#     db.session.commit()

#     return jsonify({'message': 'Order successful'}), 200

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Orders.query.all()
    return jsonify([order.__dict__ for order in orders])

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    customer_id = data.get('CustomerID')
    total_amount = data.get('TotalAmount')
    order_date_str = data.get('OrderDate')
    
    # Parse order_date_str into a datetime object
    order_date = datetime.strptime(order_date_str, '%Y-%m-%dT%H:%M:%S')
    
    existing_order = Orders.query.filter_by(CustomerID=customer_id, TotalAmount=total_amount).first()
    if existing_order:
        return jsonify({'message': 'Order already exists for this customer.'}), 409
    
    new_order = Orders(CustomerID=customer_id, OrderDate=order_date, Status=data.get('Status'), TotalAmount=total_amount)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Order placed successfully'}), 201

@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    order = Orders.query.get_or_404(id)
    data = request.json
    for key, value in data.items():
        setattr(order, key, value)
    db.session.commit()
    return jsonify({'message': 'Order updated successfully'})

@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Orders.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'})


# Create operation
@app.route('/order_items', methods=['POST'])
def create_order_item():
    data = request.json
    order_id = data['OrderID']
    medication_id = data['MedicationID']
    
    existing_order_item = OrderItems.query.filter_by(OrderID=order_id, MedicationID=medication_id).first()
    if existing_order_item:
        return jsonify({'message': 'Order item already exists'}), 409  # 409 Conflict status code
    else:
        new_order_item = OrderItems(
            OrderID=order_id,
            MedicationID=medication_id,
            Quantity=data['Quantity'],
            Subtotal=data['Subtotal']
        )
        db.session.add(new_order_item)
        db.session.commit()
        return jsonify({'message': 'Order item created successfully'}), 201

# Read operation (get all order items)
@app.route('/order_items', methods=['GET'])
def get_order_items():
    order_items = OrderItems.query.all()
    output = []
    for order_item in order_items:
        output.append({
            'OrderItemID': order_item.OrderItemID,
            'OrderID': order_item.OrderID,
            'MedicationID': order_item.MedicationID,
            'Quantity': order_item.Quantity,
            'Subtotal': order_item.Subtotal
        })
    return jsonify({'order_items': output})

# Update operation
@app.route('/order_items/<int:id>', methods=['PUT'])
def update_order_item(id):
    order_item = OrderItems.query.get(id)
    if order_item:
        data = request.json
        order_item.OrderID = data['OrderID']
        order_item.MedicationID = data['MedicationID']
        order_item.Quantity = data['Quantity']
        order_item.Subtotal = data['Subtotal']
        db.session.commit()
        return jsonify({'message': 'Order item updated successfully'})
    else:
        return jsonify({'message': 'Order item not found'}), 404

# Delete operation
@app.route('/order_items/<int:id>', methods=['DELETE'])
def delete_order_item(id):
    order_item = OrderItems.query.get(id)
    if order_item:
        db.session.delete(order_item)
        db.session.commit()
        return jsonify({'message': 'Order item deleted successfully'})
    else:
        return jsonify({'message': 'Order item not found'}), 404


# Create operation
@app.route('/payments', methods=['POST'])
def create_payment():
    data = request.json
    order_id = data['OrderID']
    payment_date = datetime.strptime(data['PaymentDate'], '%Y-%m-%dT%H:%M:%S')
    amount_paid = data['AmountPaid']
    payment_method = data['PaymentMethod']
    
    # Check if a payment with the same details already exists
    existing_payment = Payments.query.filter_by(OrderID=order_id, PaymentDate=payment_date, AmountPaid=amount_paid, PaymentMethod=payment_method).first()
    if existing_payment:
        return jsonify({'message': 'Payment already exists'}), 409  # 409 Conflict status code
    
    # If payment does not exist, create a new payment
    new_payment = Payments(
        OrderID=order_id,
        PaymentDate=payment_date,
        AmountPaid=amount_paid,
        PaymentMethod=payment_method
    )
    db.session.add(new_payment)
    db.session.commit()
    return jsonify({'message': 'Payment created successfully'}), 201

# Read operation (get all payments)
@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payments.query.all()
    output = []
    for payment in payments:
        output.append({
            'PaymentID': payment.PaymentID,
            'OrderID': payment.OrderID,
            'PaymentDate': payment.PaymentDate.strftime('%Y-%m-%d %H:%M:%S'),  # Format date for JSON
            'AmountPaid': payment.AmountPaid,
            'PaymentMethod': payment.PaymentMethod
        })
    return jsonify({'payments': output})

# Update operation
@app.route('/payments/<int:id>', methods=['PUT'])
def update_payment(id):
    payment = Payments.query.get(id)
    if payment:
        data = request.json
        payment.OrderID = data['OrderID']
        payment.PaymentDate = datetime.strptime(data['PaymentDate'], '%Y-%m-%d %H:%M:%S')
        payment.AmountPaid = data['AmountPaid']
        payment.PaymentMethod = data['PaymentMethod']
        db.session.commit()
        return jsonify({'message': 'Payment updated successfully'})
    else:
        return jsonify({'message': 'Payment not found'}), 404

# Delete operation
@app.route('/payments/<int:id>', methods=['DELETE'])
def delete_payment(id):
    payment = Payments.query.get(id)
    if payment:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'message': 'Payment deleted successfully'})
    else:
        return jsonify({'message': 'Payment not found'}), 404  


@app.route('/statements', methods=['POST'])
def create_statement():
    data = request.json
    customer_id = data['CustomerID']
    statement_date = datetime.strptime(data['StatementDate'], '%Y-%m-%dT%H:%M:%S')
    amount_due = data['AmountDue']
    payment_status = data['PaymentStatus']
    
    # Check if a statement with the same details already exists
    existing_statement = Statements.query.filter_by(CustomerID=customer_id, StatementDate=statement_date, AmountDue=amount_due, PaymentStatus=payment_status).first()
    if existing_statement:
        return jsonify({'message': 'Statement already exists'}), 409  # 409 Conflict status code
    
    # If statement does not exist, create a new statement
    new_statement = Statements(
        CustomerID=customer_id,
        StatementDate=statement_date,
        AmountDue=amount_due,
        PaymentStatus=payment_status
    )
    db.session.add(new_statement)
    db.session.commit()
    return jsonify({'message': 'Statement created successfully'}), 201

# Read operation (get all statements)
@app.route('/statements', methods=['GET'])
def get_statements():
    statements = Statements.query.all()
    output = []
    for statement in statements:
        output.append({
            'StatementID': statement.StatementID,
            'CustomerID': statement.CustomerID,
            'StatementDate': statement.StatementDate.strftime('%Y-%m-%d %H:%M:%S'),  # Format date for JSON
            'AmountDue': statement.AmountDue,
            'PaymentStatus': statement.PaymentStatus
        })
    return jsonify({'statements': output})

# Update operation
@app.route('/statements/<int:id>', methods=['PUT'])
def update_statement(id):
    statement = Statements.query.get(id)
    if statement:
        data = request.json
        statement.CustomerID = data['CustomerID']
        statement.StatementDate = datetime.strptime(data['StatementDate'], '%Y-%m-%dT%H:%M:%S')
        statement.AmountDue = data['AmountDue']
        statement.PaymentStatus = data['PaymentStatus']
        db.session.commit()
        return jsonify({'message': 'Statement updated successfully'})
    else:
        return jsonify({'message': 'Statement not found'}), 404

# Delete operation
@app.route('/statements/<int:id>', methods=['DELETE'])
def delete_statement(id):
    statement = Statements.query.get(id)
    if statement:
        db.session.delete(statement)
        db.session.commit()
        return jsonify({'message': 'Statement deleted successfully'})
    else:
        return jsonify({'message': 'Statement not found'}), 404


@app.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.json
    customer_id = data.get('customer_id')
    medication_id = data.get('medication_id')
    quantity = data.get('quantity')

    if not customer_id or not medication_id or not quantity:
        return jsonify({'error': 'Customer ID, Medication ID, and quantity are required'}), 400

    # Check if the item already exists in the cart
    existing_item = CartItem.query.filter_by(CustomerID=customer_id, MedicationID=medication_id).first()
    if existing_item:
        return jsonify({'error': 'Item already exists in the cart'}), 409

    # Create a new cart item
    new_cart_item = CartItem(CustomerID=customer_id, MedicationID=medication_id, Quantity=quantity)
    db.session.add(new_cart_item)
    db.session.commit()
    return jsonify({'message': 'Item added to cart successfully'}), 201


@app.route('/cartitems/<int:user_id>', methods=['GET'])
def get_cart_items(user_id):
    user = Customer.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Retrieve the items in the user's cart
    cart_items = CartItem.query.filter_by(CustomerID=user_id).all()

    # Prepare the response data
    items_data = []
    for item in cart_items:
        medication = Medication.query.get(item.MedicationID)
        items_data.append({
            "CartItemID": item.CartItemID,
            "MedicationID": medication.MedicationID,
            "MedicationName": medication.Name,
            "Quantity": item.Quantity,
            "Subtotal": item.Quantity * medication.PricePerUnit,
            # Add other details as needed
        })

    return jsonify({'cart_items': items_data}), 200


@app.route('/cart/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    data = request.json
    cart_item.Quantity = data.get('quantity')
    db.session.commit()
    return jsonify({'message': 'Cart item updated successfully'})

@app.route('/cart/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart successfully'})







if __name__ == '__main__':
    app.run(debug=True)
