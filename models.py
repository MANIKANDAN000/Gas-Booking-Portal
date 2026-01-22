from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db, login_manager

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    connections = db.relationship('Connection', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, delivered, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime, nullable=True)
    delivery_address = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'

class Connection(db.Model):
    __tablename__ = 'connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    connection_type = db.Column(db.String(20), default='domestic')  # domestic, commercial
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    id_proof = db.Column(db.String(50), nullable=True)
    address_proof = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Connection {self.id} - {self.status}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, success, warning, payment
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
