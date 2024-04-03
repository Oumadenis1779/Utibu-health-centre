from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Customer(db.Model):
    CustomerID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(100), nullable=False)
    LastName = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.String(20), nullable=False)
    Address = db.Column(db.String(255))
    Username = db.Column(db.String(100), nullable=False)
    PasswordHash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.PasswordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.PasswordHash, password)

class Medication(db.Model):
    MedicationID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    StockLevel = db.Column(db.Integer, nullable=False)
    PricePerUnit = db.Column(db.Float, nullable=False)

class Orders(db.Model):
    OrderID = db.Column(db.Integer, primary_key=True)
    CustomerID = db.Column(db.Integer, db.ForeignKey('customer.CustomerID'), nullable=False)
    OrderDate = db.Column(db.DateTime, nullable=False)
    Status = db.Column(db.String(20), nullable=False)
    TotalAmount = db.Column(db.Float, nullable=False)

    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

class OrderItems(db.Model):
    OrderItemID = db.Column(db.Integer, primary_key=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('orders.OrderID'), nullable=False)
    MedicationID = db.Column(db.Integer, db.ForeignKey('medication.MedicationID'), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Subtotal = db.Column(db.Float, nullable=False)

    order = db.relationship('Orders', backref=db.backref('order_items', lazy=True))
    medication = db.relationship('Medication')

class Payments(db.Model):
    PaymentID = db.Column(db.Integer, primary_key=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('orders.OrderID'), nullable=False)
    PaymentDate = db.Column(db.DateTime, nullable=False)
    AmountPaid = db.Column(db.Float, nullable=False)
    PaymentMethod = db.Column(db.String(50), nullable=False)

    order = db.relationship('Orders', backref=db.backref('payments', lazy=True))


class Statements(db.Model):
    StatementID = db.Column(db.Integer, primary_key=True)
    CustomerID = db.Column(db.Integer, db.ForeignKey('customer.CustomerID'), nullable=False)
    StatementDate = db.Column(db.DateTime, nullable=False)
    AmountDue = db.Column(db.Float, nullable=False)
    PaymentStatus = db.Column(db.String(20), nullable=False)

    customer = db.relationship('Customer', backref=db.backref('statements', lazy=True))

