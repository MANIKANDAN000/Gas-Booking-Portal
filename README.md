# 🔥 Gas Booking Portal

A modern Flask web application for LPG gas cylinder booking with **animated UI**, **glassmorphism design**, and **real-time order tracking**.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- MySQL (via XAMPP) or SQLite

### Installation

```bash
# Navigate to project folder
cd "d:\Project GIt\Final year project\Gas Booking Portal"

# Install dependencies
pip install -r requirements.txt
pip install pymysql   # For MySQL support

# Run the application
python app.py
```

Open: **http://127.0.0.1:5000**

---

## 🗄️ Database Setup

### Option 1: SQLite (No Setup Required)
Change `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///gas_booking.db'
```

### Option 2: MySQL (XAMPP)
1. Start XAMPP → Start Apache & MySQL
2. Open phpMyAdmin → Create database: `gas_booking`
3. Keep `config.py` as:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/gas_booking'
```

Tables are created automatically when you run the app.

---

## 👤 Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@gasbooking.com` | `admin123` |
| **Customer** | Register new account | - |

---

## 🔄 Testing Admin & Customer Simultaneously

To access **both Admin and Customer** in different tabs:

| Method | Admin | Customer |
|--------|-------|----------|
| **Recommended** | Chrome Normal Window | Chrome Incognito (Ctrl+Shift+N) |
| **Alternative** | Chrome Browser | Firefox/Edge Browser |

> ⚠️ Same browser tabs share sessions. Use incognito or different browsers.

---

## ✨ Features

### Customer Features
- 📦 Book gas cylinders
- 💳 Pay online with receipt generation
- 🚚 Track orders with animated delivery
- 🔔 Real-time notifications
- 🧾 Download/print payment receipts

### Admin Features  
- 📊 Dashboard with statistics
- ✅ Approve bookings → triggers payment notification to customer
- 💰 View paid orders → mark as delivered
- 🔔 Receive notifications for:
  - New booking requests
  - Payment confirmations
  - Delivery completions

---

## 📋 Booking Workflow

```
1. Customer books cylinder
      ↓
2. Admin confirms → Customer notified to pay
      ↓
3. Customer pays → Receipt generated → Admin notified
      ↓
4. Admin marks delivered → Customer notified → Admin logged
```

---

## 📁 Project Structure

```
Gas Booking Portal/
├── app.py              # Main Flask app
├── config.py           # Configuration
├── models.py           # Database models
├── routes/
│   ├── auth.py         # Login/Register
│   ├── user.py         # Customer routes
│   └── admin.py        # Admin routes
├── templates/          # HTML templates
└── static/             # CSS, JS files
```

---

## 🛠️ Tech Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Database:** MySQL / SQLite
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript
- **Animations:** AOS.js, CSS Keyframes

---

**Made for Final Year Project** 🎓
