import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gas-booking-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/gas_booking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gas cylinder pricing
    CYLINDER_PRICE = 900  # Price per cylinder in INR
    DELIVERY_CHARGE = 50  # Delivery charge
