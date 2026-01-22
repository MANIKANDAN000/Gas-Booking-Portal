from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, Booking, Connection, Notification
from extensions import db
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    delivered_bookings = Booking.query.filter_by(status='delivered').count()
    pending_connections = Connection.query.filter_by(status='pending').count()
    paid_bookings = Booking.query.filter_by(status='paid').count()
    
    # Get admin notifications
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Recent bookings
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
    
    # Calculate revenue
    total_revenue = db.session.query(db.func.sum(Booking.amount)).filter(
        Booking.status.in_(['paid', 'delivered'])
    ).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         delivered_bookings=delivered_bookings,
                         pending_connections=pending_connections,
                         paid_bookings=paid_bookings,
                         recent_bookings=recent_bookings,
                         total_revenue=total_revenue,
                         notifications=notifications,
                         unread_notifications=unread_notifications)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    else:
        all_bookings = Booking.query.filter_by(status=status_filter).order_by(Booking.booking_date.desc()).all()
    
    return render_template('admin/bookings.html', bookings=all_bookings, current_filter=status_filter)

@admin_bp.route('/booking/<int:booking_id>/update', methods=['POST'])
@login_required
@admin_required
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    old_status = booking.status
    
    valid_statuses = ['pending', 'confirmed', 'paid', 'delivered', 'cancelled']
    
    if new_status in valid_statuses:
        booking.status = new_status
        
        # When admin CONFIRMS booking -> Notify user to pay
        if new_status == 'confirmed' and old_status == 'pending':
            create_notification(
                booking.user_id,
                'Booking Approved! Please Pay',
                f'Your booking #{booking.id} has been approved. Please complete payment of ₹{booking.amount} to proceed.',
                'payment',
                f'/user/pay/{booking.id}'
            )
            flash(f'Booking #{booking_id} confirmed. User notified to pay.', 'success')
        
        # When admin marks as DELIVERED (only allowed after payment)
        elif new_status == 'delivered':
            if old_status != 'paid':
                flash('Cannot deliver - payment not received yet!', 'error')
                return redirect(url_for('admin.bookings'))
            
            booking.delivery_date = datetime.utcnow()
            
            # Notify customer
            create_notification(
                booking.user_id,
                'Order Delivered! 🎉',
                f'Your order #{booking.id} has been delivered successfully. Thank you for using GasBook!',
                'success',
                f'/user/track/{booking.id}'
            )
            
            # Notify all admins about successful delivery
            admins = User.query.filter_by(is_admin=True).all()
            for admin in admins:
                create_notification(
                    admin.id,
                    '✅ Delivery Completed',
                    f'Order #{booking.id} ({booking.quantity} cylinder) delivered to {booking.user.name}. Amount: ₹{booking.amount}',
                    'success',
                    f'/admin/bookings?status=delivered'
                )
            
            flash(f'Booking #{booking_id} marked as delivered. Customer notified.', 'success')
        
        # Cancelled
        elif new_status == 'cancelled':
            create_notification(
                booking.user_id,
                'Booking Cancelled',
                f'Your booking #{booking.id} has been cancelled by admin.',
                'warning',
                f'/user/orders'
            )
            flash(f'Booking #{booking_id} cancelled.', 'success')
        
        else:
            flash(f'Booking #{booking_id} updated to {new_status}', 'success')
        
        db.session.commit()
    
    return redirect(url_for('admin.bookings'))

@admin_bp.route('/notifications')
@login_required
@admin_required
def notifications():
    all_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return render_template('admin/notifications.html', notifications=all_notifications)

@admin_bp.route('/connections')
@login_required
@admin_required
def connections():
    all_connections = Connection.query.order_by(Connection.created_at.desc()).all()
    return render_template('admin/connections.html', connections=all_connections)

@admin_bp.route('/connection/<int:connection_id>/update', methods=['POST'])
@login_required
@admin_required
def update_connection(connection_id):
    connection = Connection.query.get_or_404(connection_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'approved', 'rejected']:
        connection.status = new_status
        if new_status == 'approved':
            connection.approved_at = datetime.utcnow()
            create_notification(
                connection.user_id,
                'Connection Approved! 🎉',
                'Your new LPG connection request has been approved. You can now book cylinders.',
                'success',
                '/user/book'
            )
        elif new_status == 'rejected':
            create_notification(
                connection.user_id,
                'Connection Rejected',
                'Your LPG connection request was rejected. Please contact support for details.',
                'warning',
                '/user/dashboard'
            )
        db.session.commit()
        flash(f'Connection #{connection_id} updated to {new_status}', 'success')
    
    return redirect(url_for('admin.connections'))
