from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Booking, Connection, User, Notification
from extensions import db
from config import Config
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Helper function to create notification
def create_notification(user_id, title, message, type='info', link=None):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        link=link
    )
    db.session.add(notification)
    db.session.commit()
    return notification

# Helper to notify all admins
def notify_admins(title, message, type='info', link=None):
    admins = User.query.filter_by(is_admin=True).all()
    for admin in admins:
        create_notification(admin.id, title, message, type, link)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Get user statistics
    total_bookings = Booking.query.filter_by(user_id=current_user.id).count()
    pending_bookings = Booking.query.filter_by(user_id=current_user.id, status='pending').count()
    delivered_bookings = Booking.query.filter_by(user_id=current_user.id, status='delivered').count()
    
    # Get unread notifications count
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Recent bookings
    recent_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).limit(5).all()
    
    # Recent notifications
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('user/dashboard.html',
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         delivered_bookings=delivered_bookings,
                         recent_bookings=recent_bookings,
                         notifications=notifications,
                         unread_notifications=unread_notifications)

@user_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 1))
        delivery_address = request.form.get('delivery_address')
        notes = request.form.get('notes', '')
        
        # Calculate amount
        amount = (Config.CYLINDER_PRICE * quantity) + Config.DELIVERY_CHARGE
        
        # Create booking with pending status
        booking = Booking(
            user_id=current_user.id,
            quantity=quantity,
            amount=amount,
            delivery_address=delivery_address,
            notes=notes,
            status='pending',  # Waiting for admin approval
            payment_status='pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Notify admins about new booking
        notify_admins(
            title='New Booking Request',
            message=f'{current_user.name} has requested {quantity} cylinder(s). Amount: ₹{amount}',
            type='info',
            link=f'/admin/bookings'
        )
        
        flash(f'Booking submitted! Waiting for admin approval. Booking ID: #{booking.id}', 'success')
        return redirect(url_for('user.track_order', booking_id=booking.id))
    
    return render_template('user/book.html', 
                         cylinder_price=Config.CYLINDER_PRICE,
                         delivery_charge=Config.DELIVERY_CHARGE)

@user_bp.route('/orders')
@login_required
def orders():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('user/orders.html', bookings=bookings)

@user_bp.route('/track-orders')
@login_required
def track_orders():
    # Get all active (non-cancelled, non-delivered) orders for tracking
    active_bookings = Booking.query.filter_by(user_id=current_user.id).filter(
        Booking.status.in_(['pending', 'confirmed', 'paid'])
    ).order_by(Booking.booking_date.desc()).all()
    
    # Get recently delivered (last 5)
    delivered_bookings = Booking.query.filter_by(user_id=current_user.id, status='delivered').order_by(Booking.delivery_date.desc()).limit(5).all()
    
    return render_template('user/track_orders.html', active_bookings=active_bookings, delivered_bookings=delivered_bookings)

@user_bp.route('/track/<int:booking_id>')
@login_required
def track_order(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('user.orders'))
    
    return render_template('user/track_order.html', booking=booking)

@user_bp.route('/pay/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def pay_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('user.orders'))
    
    if booking.status != 'confirmed':
        flash('This booking is not ready for payment', 'error')
        return redirect(url_for('user.track_order', booking_id=booking_id))
    
    if request.method == 'POST':
        # Process payment (simulated)
        booking.payment_status = 'paid'
        booking.status = 'paid'
        db.session.commit()
        
        # Notify user
        create_notification(
            current_user.id,
            'Payment Successful',
            f'Your payment of ₹{booking.amount} for Order #{booking.id} was successful!',
            'success',
            f'/user/track/{booking.id}'
        )
        
        # Notify admins about payment
        notify_admins(
            title='💰 Payment Received',
            message=f'{current_user.name} has paid ₹{booking.amount} for Order #{booking.id}. Ready for delivery!',
            type='payment',
            link=f'/admin/bookings?status=paid'
        )
        
        flash('Payment successful! Your receipt has been generated.', 'success')
        return redirect(url_for('user.receipt', booking_id=booking.id))
    
    return render_template('user/pay.html', booking=booking)

@user_bp.route('/receipt/<int:booking_id>')
@login_required
def receipt(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('user.orders'))
    
    if booking.payment_status != 'paid':
        flash('No receipt available - payment not completed', 'error')
        return redirect(url_for('user.orders'))
    
    from datetime import datetime
    return render_template('user/receipt.html', booking=booking, now=datetime.now())

@user_bp.route('/cancel/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('user.orders'))
    
    if booking.status in ['delivered', 'cancelled', 'paid']:
        flash('Cannot cancel this booking', 'error')
        return redirect(url_for('user.orders'))
    
    booking.status = 'cancelled'
    db.session.commit()
    
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('user.orders'))

@user_bp.route('/notifications')
@login_required
def notifications():
    all_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return render_template('user/notifications.html', notifications=all_notifications)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        current_user.city = request.form.get('city')
        current_user.pincode = request.form.get('pincode')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
    
    return render_template('user/profile.html')

@user_bp.route('/new-connection', methods=['GET', 'POST'])
@login_required
def new_connection():
    if request.method == 'POST':
        connection_type = request.form.get('connection_type')
        id_proof = request.form.get('id_proof')
        address_proof = request.form.get('address_proof')
        
        connection = Connection(
            user_id=current_user.id,
            connection_type=connection_type,
            id_proof=id_proof,
            address_proof=address_proof
        )
        
        db.session.add(connection)
        db.session.commit()
        
        flash('Connection request submitted successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/new_connection.html')
