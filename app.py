# ============================================================
# MyShop - Simple Flask E-commerce App
# Clean & easy-to-read structure
# ============================================================

from flask import Flask, render_template, request, redirect, session, flash, make_response
from flask_mail import Mail, Message
import sqlite3
import bcrypt
import random
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import razorpay
import json
import traceback

import config
from utils.pdf_generator import generate_pdf


app = Flask(__name__)
app.secret_key = config.SECRET_KEY

RAZORPAY_KEY_ID = config.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = config.RAZORPAY_KEY_SECRET

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

app.config.update(
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_USE_TLS=config.MAIL_USE_TLS,
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_TIMEOUT=config.MAIL_TIMEOUT,
)

mail = Mail(app)


@app.route('/')
def index():
    return redirect('/user-login')


# ============================================================
# DATABASE + HELPERS
# ============================================================

def get_db_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            profile_pic TEXT DEFAULT NULL,
            phone TEXT DEFAULT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            price REAL,
            image TEXT,
            admin_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            razorpay_order_id TEXT,
            razorpay_payment_id TEXT,
            amount REAL,
            payment_status TEXT,
            shipping_address TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            price REAL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def products_table_has_admin_id():
    """Check if the admin_id column exists in products table (for safe migration)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(products)")
    exists = any(row["name"] == "admin_id" for row in cursor.fetchall())
    cursor.close()
    conn.close()
    return exists


def ensure_products_admin_id_column(default_admin_id=None):
    """Idempotent helper: adds admin_id column + FK if missing.
    If default_admin_id is provided, backfills all NULL admin_id rows with it
    (so previously added products become visible to the first admin who triggers setup)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Add admin_id column if missing
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN admin_id INTEGER")
    except Exception:
        pass

    # SQLite cannot add a foreign key constraint after table creation.
    # The column is still added and can be used for filtering.

    # Backfill old products (NULL admin_id) to the given admin if provided
    if default_admin_id is not None:
        try:
            cursor.execute(
                "UPDATE products SET admin_id = ? WHERE admin_id IS NULL",
                (default_admin_id,)
            )
        except Exception:
            pass

    conn.commit()
    cursor.close()
    conn.close()
    return True


def ensure_orders_table():
    """Idempotent migration helper — ensures orders table has all columns used by current code.
    Replaces repeated ALTER + backfill blocks to reduce code size."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN shipping_address TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'pending'")
    except:
        pass
    try:
        cursor.execute("UPDATE orders SET status='pending' WHERE status IS NULL OR status=''")
    except:
        pass
    conn.commit()
    cursor.close()
    conn.close()


def ensure_admin_role_status_columns():
    """Idempotent migration: adds role + status columns to admin table (for Super Admin feature).
    Safe to run multiple times. Defaults keep old admins working."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE admin ADD COLUMN role VARCHAR(20) DEFAULT 'admin'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE admin ADD COLUMN status VARCHAR(20) DEFAULT 'approved'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE admin ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except:
        pass

    # Backfill old admins (who existed before super admin feature)
    try:
        cursor.execute("UPDATE admin SET role='admin' WHERE role IS NULL OR role=''")
        cursor.execute("UPDATE admin SET status='approved' WHERE status IS NULL OR status=''")
    except:
        pass

    conn.commit()
    cursor.close()
    conn.close()


def ensure_superadmin_table():
    """Ensure dedicated superadmin table exists in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS superadmin (
                superadmin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'approved',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception:
        pass
    conn.commit()
    cursor.close()
    conn.close()


def ensure_bootstrap_superadmin():
    """Create or update the bootstrap superadmin from environment variables."""
    if not config.SUPERADMIN_EMAIL or not config.SUPERADMIN_PASSWORD:
        return False, "Superadmin environment variables are not configured."

    ensure_superadmin_table()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM superadmin WHERE LOWER(email)=LOWER(?)', (config.SUPERADMIN_EMAIL.lower(),))
    existing_admin = cursor.fetchone()

    if existing_admin is None:
        cursor.execute(
            """
            INSERT INTO superadmin (name, email, password, status)
            VALUES (?, ?, ?, 'approved')
            """,
            (config.SUPERADMIN_NAME, config.SUPERADMIN_EMAIL, config.SUPERADMIN_PASSWORD)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Superadmin account created successfully."

    cursor.execute(
        """
        UPDATE superadmin
        SET name = ?, password = ?, status = 'approved'
        WHERE LOWER(email)=LOWER(?)
        """,
        (config.SUPERADMIN_NAME, config.SUPERADMIN_PASSWORD, config.SUPERADMIN_EMAIL.lower())
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Superadmin account updated successfully."


def send_otp_email(email, otp):
    if not config.MAIL_ENABLED:
        app.logger.warning("OTP email skipped because MAIL_ENABLED is false.")
        return False

    if not config.MAIL_USERNAME or not config.MAIL_PASSWORD:
        app.logger.warning("OTP email skipped because SMTP credentials are missing.")
        return False

    subject = 'Admin Registration OTP'
    body = f'Your verification OTP is: {otp}\n\nIf you did not request this, please ignore this message.'

    message = Message(subject=subject, sender=config.MAIL_USERNAME, recipients=[email], body=body)

    try:
        mail.send(message)
        return True
    except Exception as exc:
        app.logger.exception("Failed to send OTP email to %s", email)
        return False


# Initialize database after helper functions are defined
initialize_database()


# ============================================================
# AUTH HELPERS
# ============================================================

def require_admin():
    """Redirect to admin login if not logged in or not approved."""
    if 'admin_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/admin-login')
    if session.get('admin_status') != 'approved':
        flash("Your account is not approved.", "danger")
        return redirect('/admin-login')
    return None


def require_super_admin():
    """Redirect if not logged in as superadmin."""
    if 'admin_id' not in session or session.get('admin_role') != 'superadmin':
        flash("Super Admin access required.", "danger")
        return redirect('/superadmin-login')
    return None


def require_user():
    """Redirect to user login if not logged in."""
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/user-login')
    return None


# ============================================================
# ADMIN AUTH ROUTES
# ============================================================

@app.route('/admin-signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'GET':
        return render_template('admin/admin_signup.html')

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()

    if not name or not email:
        flash('Name and email are required.', 'danger')
        return redirect('/admin-signup')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE email=?', (email,))
    existing_admin = cursor.fetchone()
    cursor.close()
    conn.close()

    if existing_admin is not None:
        flash('This email is already registered. Please login instead.', 'danger')
        return redirect('/admin-login')

    otp = str(random.randint(100000, 999999))
    session['pending_admin'] = {'name': name, 'email': email, 'otp': otp}

    if not send_otp_email(email, otp):
        if config.OTP_FALLBACK_ENABLED:
            flash(f'Email could not be sent. Demo OTP: {otp}', 'warning')
            return render_template('admin/verify_otp.html')
        flash('Could not send OTP email. Please try again later.', 'danger')
        return redirect('/admin-signup')

    flash('OTP sent to your email. Enter it below to complete registration.', 'success')
    return render_template('admin/verify_otp.html')


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    pending_admin = session.get('pending_admin')
    if pending_admin is None:
        flash('Please start registration first.', 'danger')
        return redirect('/admin-signup')

    if request.method == 'GET':
        return render_template('admin/verify_otp.html')

    otp = request.form.get('otp', '').strip()
    password = request.form.get('password', '').strip()

    if not otp or not password:
        flash('OTP and password are required.', 'danger')
        return redirect('/verify-otp')

    if otp != pending_admin.get('otp'):
        flash('Invalid OTP. Please try again.', 'danger')
        return redirect('/verify-otp')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    ensure_admin_role_status_columns()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO admin (name, email, password, role, status) VALUES (?, ?, ?, 'admin', 'pending')",
        (pending_admin['name'], pending_admin['email'], hashed_password)
    )
    conn.commit()
    cursor.close()
    conn.close()

    session.pop('pending_admin', None)
    flash('Registration complete. Please login with your new account. (Waiting for Super Admin approval)', 'success')
    return redirect('/admin-login')


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/admin_login.html')

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()

    if not email or not password:
        flash('Email and password are required.', 'danger')
        return redirect('/admin-login')

    ensure_admin_role_status_columns()
    ensure_superadmin_table()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM superadmin')
    superadmin_count = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM admin WHERE LOWER(email)=LOWER(?)', (email,))
    admin = cursor.fetchone()

    if admin is None:
        cursor.close()
        conn.close()
        flash('Email not found. Please register first.', 'danger')
        return redirect('/admin-login')

    # If no superadmin exists yet, approve the first admin automatically.
    if admin['status'] != 'approved' and superadmin_count == 0:
        cursor.execute('UPDATE admin SET status = ? WHERE admin_id = ?', ('approved', admin['admin_id']))
        conn.commit()
        admin_status = 'approved'
    else:
        admin_status = admin['status']

    if admin_status != 'approved':
        cursor.close()
        conn.close()
        flash('Your account is not approved yet. Please contact Super Admin.', 'danger')
        return redirect('/admin-login')

    # Only regular admins can login here, not superadmins
    if admin['role'] == 'superadmin':
        flash('This login is for regular Admins only. Please use Super Admin login.', 'danger')
        return redirect('/admin-login')

    stored_hashed_password = admin['password'].encode('utf-8')
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        flash('Incorrect password. Try again.', 'danger')
        return redirect('/admin-login')

    session['admin_id'] = admin['admin_id']
    session['admin_name'] = admin['name']
    session['admin_email'] = admin['email']
    session['admin_role'] = admin['role'] if 'role' in admin.keys() else 'admin'
    session['admin_status'] = admin['status'] if 'status' in admin.keys() else 'approved'

    # Clear any previous flash messages
    session.pop('_flashes', None)

    flash('Login successful!', 'success')

    return redirect('/admin/dashboard')


@app.route('/admin-dashboard')
@app.route('/admin/dashboard')
def admin_dashboard():
    resp = require_admin()
    if resp:
        return resp

    return render_template('admin/dashboard.html', admin_name=session['admin_name'])


@app.route('/superadmin-login', methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'GET':
        return render_template('superadmin/login.html')

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()

    if not email or not password:
        flash('Email and password are required.', 'danger')
        return redirect('/superadmin-login')

    ensure_admin_role_status_columns()
    ensure_superadmin_table()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM superadmin WHERE LOWER(email)=LOWER(?)', (email,))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    if admin is None:
        flash('Email not found.', 'danger')
        return redirect('/superadmin-login')

    if admin['status'] != 'approved':
        flash('Your Super Admin account is not approved.', 'danger')
        return redirect('/superadmin-login')

    stored_password = admin['password']
    if password != stored_password:
        flash('Incorrect password.', 'danger')
        return redirect('/superadmin-login')

    # Create session
    session['admin_id'] = admin['superadmin_id']
    session['admin_name'] = admin['name']
    session['admin_email'] = admin['email']
    session['admin_role'] = 'superadmin'
    session['admin_status'] = admin['status'] if 'status' in admin.keys() else 'approved'

    session.pop('_flashes', None)
    flash('Welcome, Super Admin!', 'success')
    return redirect('/superadmin/dashboard')


@app.route('/setup-superadmin')
def setup_superadmin():
    ok, message = ensure_bootstrap_superadmin()
    flash(message, 'success' if ok else 'danger')
    return redirect('/superadmin-login')


# ============================================================
# SUPER ADMIN ROUTES (NEW)
# ============================================================

@app.route('/superadmin/dashboard')
def superadmin_dashboard():
    resp = require_super_admin()
    if resp:
        return resp

    ensure_admin_role_status_columns()
    ensure_orders_table()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Platform Stats for Super Admin Dashboard
    cursor.execute("SELECT COUNT(*) as total FROM admin")
    total_admins = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as pending FROM admin WHERE status='pending'")
    pending_admins = cursor.fetchone()['pending']

    cursor.execute("SELECT COUNT(*) as total FROM products")
    total_products = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM orders")
    total_orders = cursor.fetchone()['total']

    cursor.execute("SELECT COALESCE(SUM(amount), 0) as revenue FROM orders WHERE payment_status='paid'")
    total_revenue = cursor.fetchone()['revenue'] or 0

    cursor.execute("SELECT COUNT(*) as today FROM orders WHERE date(created_at) = date('now')")
    orders_today = cursor.fetchone()['today'] or 0

    cursor.close()
    conn.close()

    stats = {
        'total_admins': total_admins,
        'pending_admins': pending_admins,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders_today': orders_today
    }

    return render_template('superadmin/dashboard.html',
                           admin_name=session['admin_name'],
                           stats=stats)


@app.route('/superadmin/admins')
def superadmin_admins():
    resp = require_super_admin()
    if resp:
        return resp

    ensure_admin_role_status_columns()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin ORDER BY created_at DESC")
    all_admins = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('superadmin/admins.html', 
                           admins=all_admins, 
                           admin_name=session['admin_name'],
                           current_admin_id=session.get('admin_id'))


@app.route('/superadmin/admins/approve/<int:admin_id>')
def approve_admin(admin_id):
    resp = require_super_admin()
    if resp:
        return resp

    # Prevent self-approval issues
    if admin_id == session.get('admin_id'):
        flash("You cannot change your own status.", "warning")
        return redirect('/superadmin/admins')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE admin SET status='approved' WHERE admin_id=?", (admin_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Admin approved successfully!", "success")
    return redirect('/superadmin/admins')


@app.route('/superadmin/admins/reject/<int:admin_id>')
def reject_admin(admin_id):
    resp = require_super_admin()
    if resp:
        return resp

    if admin_id == session.get('admin_id'):
        flash("You cannot reject your own account.", "warning")
        return redirect('/superadmin/admins')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE admin SET status='rejected' WHERE admin_id=?", (admin_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Admin rejected.", "danger")
    return redirect('/superadmin/admins')


@app.route('/superadmin/products')
def superadmin_products():
    resp = require_super_admin()
    if resp:
        return resp

    # Ensure admin_id column exists (safe for old DBs)
    if not products_table_has_admin_id():
        ensure_products_admin_id_column()

    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch ALL products + owner admin info (global view for Super Admin)
    cursor.execute("""
        SELECT p.*, a.name as admin_name, a.email as admin_email 
        FROM products p 
        LEFT JOIN admin a ON p.admin_id = a.admin_id 
        ORDER BY p.product_id DESC
    """)
    all_products = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('superadmin/products.html', 
                            products=all_products, 
                            admin_name=session['admin_name'])


@app.route('/superadmin/products/delete/<int:product_id>')
def superadmin_delete_product(product_id):
    """Super Admin can delete ANY product on the platform (no ownership restriction)."""
    resp = require_super_admin()
    if resp:
        return resp

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get image to delete file
    cursor.execute("SELECT image FROM products WHERE product_id=?", (product_id,))
    product = cursor.fetchone()

    if product:
        image_name = product['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass

        cursor.execute("DELETE FROM products WHERE product_id=?", (product_id,))
        conn.commit()
        flash("Product deleted by Super Admin.", "success")
    else:
        flash("Product not found.", "danger")

    cursor.close()
    conn.close()
    return redirect('/superadmin/products')


@app.route('/superadmin/orders')
def superadmin_orders():
    resp = require_super_admin()
    if resp:
        return resp

    ensure_orders_table()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get ALL orders + customer info (global view)
    cursor.execute("""
        SELECT o.*, u.name as user_name, u.email as user_email 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.user_id 
        ORDER BY o.created_at DESC
    """)
    all_orders = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('superadmin/orders.html', 
                            orders=all_orders, 
                            admin_name=session['admin_name'])


@app.route('/superadmin/orders/status/<int:order_id>/<status>')
def superadmin_update_order_status(order_id, status):
    """Allow Super Admin to force update order status globally."""
    resp = require_super_admin()
    if resp:
        return resp

    allowed = ['pending', 'shipped', 'delivered', 'cancelled']
    if status not in allowed:
        flash("Invalid status.", "danger")
        return redirect('/superadmin/orders')

    ensure_orders_table()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Order #{order_id} marked as {status}.", "success")
    return redirect('/superadmin/orders')


@app.route('/superadmin/revenue')
def superadmin_revenue():
    resp = require_super_admin()
    if resp:
        return resp

    ensure_orders_table()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Global Totals
    cursor.execute("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(amount) as total_revenue,
            SUM(CASE WHEN payment_status = 'paid' THEN amount ELSE 0 END) as paid_revenue
        FROM orders
    """)
    totals = cursor.fetchone()

    # 2. Revenue per Admin (by joining order_items → products → admin)
    cursor.execute("""
        SELECT 
            a.admin_id,
            a.name as admin_name,
            a.email as admin_email,
            COUNT(DISTINCT o.order_id) as order_count,
            SUM(oi.price * oi.quantity) as admin_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN admin a ON p.admin_id = a.admin_id
        WHERE o.payment_status = 'paid'
        GROUP BY a.admin_id, a.name, a.email
        ORDER BY admin_revenue DESC
    """)
    per_admin = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('superadmin/revenue.html',
                           totals=totals,
                           per_admin=per_admin,
                           admin_name=session['admin_name'])


@app.route('/admin-logout')
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    session.pop('admin_role', None)
    session.pop('admin_status', None)

    # Clear any previous flashes so only the single logout message appears
    session.pop('_flashes', None)

    flash('Logged out successfully.', 'success')
    return redirect('/admin-login')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('admin/forgot_password.html')

    email = request.form.get('email', '').strip()
    if not email:
        flash('Email is required.', 'danger')
        return redirect('/forgot-password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE email=?', (email,))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    # Do not reveal whether the email exists.
    if admin:
        otp = str(random.randint(100000, 999999))
        send_otp_email(email, otp)

    flash('If the email exists, a reset link/OTP has been sent to your inbox.', 'success')
    return redirect('/admin-login')


@app.route('/admin/orders')
def admin_orders():
    resp = require_admin()
    if resp:
        return resp
    return render_template('admin/orders.html')


@app.route('/admin/profile')
def admin_profile():
    resp = require_admin()
    if resp:
        return resp
    return render_template('admin/profile.html', admin_name=session.get('admin_name'), admin_email=session.get('admin_email'))


# ============================================================
# UPLOAD FOLDERS
# ============================================================

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'upload', 'product_images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PROFILE_UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'upload', 'profile_pics')
app.config['PROFILE_UPLOAD_FOLDER'] = PROFILE_UPLOAD_FOLDER
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# ADMIN PRODUCT ROUTES
# ============================================================

@app.route('/admin/add-item', methods=['GET'])
def add_item_page():
    resp = require_admin()
    if resp:
        return resp
    return render_template("admin/add_items.html")


@app.route('/admin/add-item', methods=['POST'])
def add_item():
    resp = require_admin()
    if resp:
        return resp

    if not products_table_has_admin_id():
        current_admin = session.get('admin_id')
        ensure_products_admin_id_column(default_admin_id=current_admin)
        flash("Admin product isolation activated automatically! Old products assigned to you.", "success")

    # 1️⃣ Get form data
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    price = request.form.get('price', '').strip()
    image_file = request.files.get('image')

    # 2️⃣ Validate form fields
    if not name or not description or not category or not price:
        flash("All fields are required!", "danger")
        return redirect('/admin/add-item')

    if not image_file or image_file.filename == "":
        flash("Please upload a product image!", "danger")
        return redirect('/admin/add-item')

    # 3️⃣ Secure the file name
    filename = secure_filename(image_file.filename)

    # 4️⃣ Create full path
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # 5️⃣ Save image into folder
    image_file.save(image_path)

    # 6️⃣ Insert product into database
    conn = get_db_connection()
    cursor = conn.cursor()

    admin_id = session.get('admin_id')
    cursor.execute(
        "INSERT INTO products (name, description, category, price, image, admin_id) VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, category, price, filename, admin_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    flash("Product added successfully!", "success")
    return redirect('/admin/add-item')


@app.route('/admin/item-list')
def item_list():
    resp = require_admin()
    if resp:
        return resp

    if not products_table_has_admin_id():
        current_admin = session.get('admin_id')
        ensure_products_admin_id_column(default_admin_id=current_admin)
        flash("Admin product isolation activated automatically! Old products assigned to you.", "success")

    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    admin_id = session.get('admin_id')

    # 1️⃣ Fetch category list for dropdown (only this admin's categories)
    cursor.execute("SELECT DISTINCT category FROM products WHERE admin_id = ?", (admin_id,))
    categories = cursor.fetchall()

    # 2️⃣ Build dynamic query based on filters (only this admin's products)
    query = "SELECT * FROM products WHERE admin_id = ?"
    params = [admin_id]

    if search:
        query += " AND name LIKE ?"
        params.append("%" + search + "%")

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    cursor.execute(query, tuple(params))
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin/items_list.html",
        products=products,
        categories=categories
    )


@app.route('/admin/view-item/<int:item_id>')
def view_item(item_id):
    resp = require_admin()
    if resp:
        return resp

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE product_id = ?", (item_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    current_admin = session.get('admin_id')
    if not product or product['admin_id'] != current_admin:
        flash("Product not found or access denied!", "danger")
        return redirect('/admin/item-list')

    return render_template("admin/view_items.html", product=product)


@app.route('/admin/update-item/<int:item_id>', methods=['GET'])
def update_item_page(item_id):
    resp = require_admin()
    if resp:
        return resp

    # Fetch product data
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE product_id = ?", (item_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    current_admin = session.get('admin_id')
    if not product or product['admin_id'] != current_admin:
        flash("Product not found or access denied!", "danger")
        return redirect('/admin/item-list')

    return render_template("admin/update_item.html", product=product)


@app.route('/admin/update-item/<int:item_id>', methods=['POST'])
def update_item(item_id):
    resp = require_admin()
    if resp:
        return resp

    # 1️⃣ Get updated form data
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    price = request.form.get('price', '').strip()

    if not name or not description or not category or not price:
        flash("All fields are required!", "danger")
        return redirect('/admin/update-item/' + str(item_id))

    # 2️⃣ Fetch and verify ownership early
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?", (item_id,))
    product = cursor.fetchone()

    current_admin = session.get('admin_id')
    if not product or product['admin_id'] != current_admin:
        cursor.close()
        conn.close()
        flash("Product not found or access denied!", "danger")
        return redirect('/admin/item-list')

    new_image = request.files.get('image')
    old_image_name = product['image']

    # 3️⃣ If admin uploaded a new image → replace it
    if new_image and new_image.filename != "":
        
        # Secure filename
        new_filename = secure_filename(new_image.filename)

        # Save new image
        new_image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        new_image.save(new_image_path)

        # Delete old image file
        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image_name)
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

        final_image_name = new_filename

    else:
        # No new image uploaded → keep old one
        final_image_name = old_image_name

    # 4️⃣ Update product in the database (with ownership guard)
    cursor.execute("""
        UPDATE products
        SET name=?, description=?, category=?, price=?, image=?
        WHERE product_id=? AND admin_id=?
    """, (name, description, category, price, final_image_name, item_id, current_admin))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Product updated successfully!", "success")
    return redirect('/admin/item-list')


@app.route('/admin/delete-item/<int:item_id>')
def delete_item(item_id):
    resp = require_admin()
    if resp:
        return resp

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1️⃣ Fetch product to get image name + verify ownership
    cursor.execute("SELECT image, admin_id FROM products WHERE product_id=?", (item_id,))
    product = cursor.fetchone()

    current_admin = session.get('admin_id')
    if not product or product['admin_id'] != current_admin:
        flash("Product not found or access denied!", "danger")
        cursor.close()
        conn.close()
        return redirect('/admin/item-list')

    image_name = product['image']

    # Delete image from folder
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    if os.path.exists(image_path):
        os.remove(image_path)

    # 2️⃣ Delete product from DB (with ownership guard)
    cursor.execute("DELETE FROM products WHERE product_id=? AND admin_id=?", (item_id, current_admin))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Product deleted successfully!", "success")
    return redirect('/admin/item-list')


# ============================================================
# USER AUTH ROUTES
# ============================================================

@app.route('/user-register', methods=['GET', 'POST'])
def user_register():

    if request.method == 'GET':
        return render_template("user/user_register.html")

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Check if user already exists
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        flash("Email already registered! Please login.", "danger")
        return redirect('/user-register')

    # Hash password (store as UTF-8 string)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Insert new user
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hashed_password)
    )
    conn.commit()

    cursor.close()
    conn.close()

    flash("Registration successful! Please login.", "success")
    return redirect('/user-login')


@app.route('/user-login', methods=['GET', 'POST'])



def user_login():

    if request.method == 'GET':
        return render_template("user/user_login.html")

    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        flash("Email not found! Please register.", "danger")
        return redirect('/user-login')

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        flash("Incorrect password!", "danger")
        return redirect('/user-login')

    # Create user session
    session['user_id'] = user['user_id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['user_profile_pic'] = user['profile_pic'] if 'profile_pic' in user.keys() else None
    session['user_phone'] = user['phone'] if 'phone' in user.keys() else None

    flash("Login successful!", "success")
    return redirect('/user-dashboard')


@app.route('/user-dashboard')
def user_dashboard():
    resp = require_user()
    if resp:
        return resp

    return render_template("user/user_home.html", user_name=session['user_name'])


@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    resp = require_user()
    if resp:
        return resp

    # Ensure profile_pic and phone columns exist (safe for existing DBs)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_pic VARCHAR(255) DEFAULT NULL")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT NULL")
    except:
        pass
    conn.commit()
    cursor.close()
    conn.close()

    # Fetch fresh user data (including profile_pic and phone)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    current_profile_pic = user['profile_pic'] if user and 'profile_pic' in user.keys() else None
    session['user_profile_pic'] = current_profile_pic
    user_phone = user['phone'] if user and 'phone' in user.keys() else None

    # Handle POST actions: photo upload OR profile details update
    if request.method == 'POST':
        profile_pic_file = request.files.get('profile_pic')
        if profile_pic_file and profile_pic_file.filename != "":
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            ext = profile_pic_file.filename.rsplit('.', 1)[1].lower() if '.' in profile_pic_file.filename else ''
            if ext not in allowed_extensions:
                flash("Only PNG, JPG, JPEG or GIF files are allowed.", "danger")
                return redirect('/user/profile')

            filename = secure_filename(profile_pic_file.filename)
            filename = f"user_{session['user_id']}_{filename}"

            upload_folder = app.config.get('PROFILE_UPLOAD_FOLDER')
            save_path = os.path.join(upload_folder, filename)

            try:
                if current_profile_pic:
                    old_path = os.path.join(upload_folder, current_profile_pic)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                profile_pic_file.save(save_path)

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET profile_pic=? WHERE user_id=?", (filename, session['user_id']))
                conn.commit()
                cursor.close()
                conn.close()

                session['user_profile_pic'] = filename
                flash("Profile photo uploaded successfully!", "success")
            except Exception:
                flash("Failed to save the photo. Please try again.", "danger")

            return redirect('/user/profile')

        elif request.form.get('action') == 'update_profile':
            new_name = request.form.get('name', '').strip()
            new_email = request.form.get('email', '').strip().lower()
            new_phone = request.form.get('phone', '').strip()

            if not new_name or not new_email:
                flash("Name and email are required.", "danger")
                return redirect('/user/profile')

            # Check email uniqueness (exclude self)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE email=? AND user_id != ?", (new_email, session['user_id']))
            email_taken = cursor.fetchone()
            cursor.close()
            conn.close()

            if email_taken:
                flash("This email is already used by another account.", "danger")
                return redirect('/user/profile')

            # Update DB (phone column already ensured above)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET name=?, email=?, phone=? WHERE user_id=?",
                (new_name, new_email, new_phone or None, session['user_id'])
            )
            conn.commit()
            cursor.close()
            conn.close()

            # Refresh session
            session['user_name'] = new_name
            session['user_email'] = new_email
            session['user_phone'] = new_phone or None

            flash("Profile details updated successfully!", "success")
            return redirect('/user/profile')

        else:
            flash("No valid action submitted.", "danger")
            return redirect('/user/profile')

    # GET: prepare address info (from session as before)
    addresses = session.get('shipping_addresses', [])
    selected_addr = session.get('selected_address') or (addresses[0] if addresses else {})

    # Prefer user's saved phone (from profile), fallback to shipping address phone
    mobile = user_phone or (selected_addr.get('phone', 'Not provided') if selected_addr else 'Not provided')

    addr_parts = []
    if selected_addr.get('address'):
        addr_parts.append(selected_addr['address'])
    if selected_addr.get('city'):
        addr_parts.append(selected_addr['city'])
    if selected_addr.get('state'):
        addr_parts.append(selected_addr['state'])
    if selected_addr.get('pincode'):
        addr_parts.append('PIN: ' + selected_addr['pincode'])
    address_str = ', '.join(addr_parts) if addr_parts else 'Not provided'

    return render_template(
        'user/profile.html',
        user_name=session.get('user_name', 'User'),
        user_email=session.get('user_email', ''),
        mobile=mobile,
        address=address_str,
        has_address=bool(addr_parts),
        profile_pic=session.get('user_profile_pic'),
        user_phone=user_phone
    )


@app.route('/user-logout')

def user_logout():
    
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('user_profile_pic', None)
    session.pop('user_phone', None)

    # Clear any previous flashes so only the single logout message appears
    session.pop('_flashes', None)

    flash("Logged out successfully!", "success")
    return redirect('/user-login')


@app.route('/user/products')
def user_products():
    resp = require_user()
    if resp:
        return resp

    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch categories for filter dropdown
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = cursor.fetchall()

    # Build dynamic SQL
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND name LIKE ?"
        params.append("%" + search + "%")

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    cursor.execute(query, params)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "user/user_products.html",
        products=products,
        categories=categories
    )


@app.route('/user/product/<int:product_id>')
def user_product_details(product_id):
    resp = require_user()
    if resp:
        return resp

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    if not product:
        flash("Product not found!", "danger")
        return redirect('/user/products')

    return render_template("user/product_details.html", product=product)


@app.route('/user/add-to-cart/<int:product_id>', methods=['GET'])
@app.route('/user/cart/add', methods=['POST'])
def add_to_cart(product_id=None):
    resp = require_user()
    if resp:
        return resp

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1
    else:
        # GET quick add (qty=1)
        if product_id is None:
            flash("Invalid product.", "danger")
            return redirect('/user/products')
        quantity = 1

    if not product_id:
        flash("Invalid product.", "danger")
        return redirect(request.referrer or '/user/products')

    product_id = int(product_id)

    # Create cart if doesn't exist
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    # Get product
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id=?", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if not product:
        flash("Product not found.", "danger")
        return redirect(request.referrer or '/user/products')

    pid = str(product_id)

    # If exists → increase quantity
    if pid in cart:
        cart[pid]['quantity'] += quantity
    else:
        cart[pid] = {
            'name': product['name'],
            'price': float(product['price']),
            'image': product['image'],
            'quantity': quantity
        }

    session['cart'] = cart

    flash(f"Added {quantity} × {product['name']} to cart!", "success")

    # For Buy Now from listing (?buy=1), go straight to cart
    if request.method == 'GET' and request.args.get('buy'):
        return redirect('/user/cart')
    return redirect(request.referrer or '/user/products')


@app.route('/user/cart')
def view_cart():
    resp = require_user()
    if resp:
        return resp

    cart = session.get('cart', {})

    # Calculate total
    grand_total = sum(item['price'] * item['quantity'] for item in cart.values())

    return render_template("user/cart.html", cart=cart, grand_total=grand_total)


@app.route('/user/checkout', methods=['GET', 'POST'])
def user_checkout():
    resp = require_user()
    if resp:
        return resp

    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty!", "danger")
        return redirect('/user/products')

    if request.method == 'POST':
        form_action = request.form.get('action')

        if form_action == 'select_items':
            selected_items = request.form.getlist('selected_items')
            selected_items = [pid for pid in selected_items if pid in cart]
            if not selected_items:
                flash("Please select at least one product to checkout.", "danger")
                return redirect('/user/cart')
            session['checkout_items'] = selected_items
            session.pop('selected_address', None)
            return redirect('/user/checkout')

        if form_action == 'add_address':
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            landmark = request.form.get('landmark', '').strip()
            city = request.form.get('city', '').strip()
            district = request.form.get('district', '').strip()
            state = request.form.get('state', '').strip()
            country = request.form.get('country', '').strip() or 'India'
            pincode = request.form.get('pincode', '').strip()

            if not full_name or not phone or not address or not landmark or not city or not district or not state or not pincode:
                flash("Please fill in all required address fields.", "danger")
                return redirect('/user/checkout')

            addresses = session.get('shipping_addresses', [])
            next_id = max([addr['id'] for addr in addresses], default=0) + 1
            saved_address = {
                'id': next_id,
                'name': full_name,
                'phone': phone,
                'address': address,
                'landmark': landmark,
                'city': city,
                'district': district,
                'state': state,
                'country': country,
                'pincode': pincode,
            }
            addresses.append(saved_address)
            session['shipping_addresses'] = addresses
            session['selected_address'] = saved_address
            flash("Address saved. Proceeding to payment.", "success")
            return redirect('/user/pay')

        if form_action == 'use_address':
            selected_address = request.form.get('selected_address')
            addresses = session.get('shipping_addresses', [])
            address = next((addr for addr in addresses if str(addr['id']) == selected_address), None)
            if not address:
                flash("Please select a shipping address.", "danger")
                return redirect('/user/checkout')
            session['selected_address'] = address
            return redirect('/user/pay')

        if request.form.get('delete_address_id'):
            address_id = request.form.get('delete_address_id')
            addresses = session.get('shipping_addresses', [])
            addresses = [addr for addr in addresses if str(addr['id']) != address_id]
            session['shipping_addresses'] = addresses
            if session.get('selected_address') and str(session['selected_address'].get('id')) == address_id:
                session.pop('selected_address', None)
            flash("Address deleted.", "success")
            return redirect('/user/checkout')

        if request.form.get('edit_address_id'):
            address_id = request.form.get('edit_address_id')
            addresses = session.get('shipping_addresses', [])
            address = next((addr for addr in addresses if str(addr['id']) == address_id), None)
            if address:
                session['editing_address'] = address
            return redirect('/user/checkout')

        if form_action == 'save_edit_address':
            address_id = request.form.get('address_id')
            addresses = session.get('shipping_addresses', [])
            for addr in addresses:
                if str(addr['id']) == address_id:
                    addr['name'] = request.form.get('full_name', '').strip()
                    addr['phone'] = request.form.get('phone', '').strip()
                    addr['address'] = request.form.get('address', '').strip()
                    addr['landmark'] = request.form.get('landmark', '').strip()
                    addr['city'] = request.form.get('city', '').strip()
                    addr['district'] = request.form.get('district', '').strip()
                    addr['state'] = request.form.get('state', '').strip()
                    addr['country'] = request.form.get('country', '').strip() or 'India'
                    addr['pincode'] = request.form.get('pincode', '').strip()
                    break
            session['shipping_addresses'] = addresses
            session.pop('editing_address', None)
            flash("Address updated.", "success")
            return redirect('/user/checkout')
 
    # Handle edit/delete via query params (more reliable than form submit)
    if request.method == 'GET':
        edit_id = request.args.get('edit')
        if edit_id:
            addresses = session.get('shipping_addresses', [])
            address = next((addr for addr in addresses if str(addr['id']) == edit_id), None)
            if address:
                session['editing_address'] = address
            return redirect('/user/checkout')

        delete_id = request.args.get('delete')
        if delete_id:
            addresses = session.get('shipping_addresses', [])
            addresses = [addr for addr in addresses if str(addr['id']) != delete_id]
            session['shipping_addresses'] = addresses
            if session.get('selected_address') and str(session['selected_address'].get('id')) == delete_id:
                session.pop('selected_address', None)
            flash("Address deleted.", "success")
            return redirect('/user/checkout')

    selected_ids = session.get('checkout_items', [])
    if not selected_ids:
        flash("Please select at least one product from your cart before checkout.", "danger")
        return redirect('/user/cart')

    selected_cart = {pid: cart[pid] for pid in selected_ids if pid in cart}
    if not selected_cart:
        flash("The selected cart items are no longer available. Please select again.", "danger")
        return redirect('/user/cart')

    selected_total = sum(item['price'] * item['quantity'] for item in selected_cart.values())

    addresses = session.get('shipping_addresses', [])
    editing_address = session.get('editing_address')
    return render_template(
        'user/shipping_address.html',
        selected_cart=selected_cart,
        selected_total=selected_total,
        addresses=addresses,
        editing_address=editing_address
    )


# =================================================================
# INCREASE QUANTITY
# =================================================================
@app.route('/user/cart/increase/<pid>')
def increase_quantity(pid):

    cart = session.get('cart', {})

    if pid in cart:
        cart[pid]['quantity'] += 1

    session['cart'] = cart
    return redirect('/user/cart')

# =================================================================
# DECREASE QUANTITY
# =================================================================
@app.route('/user/cart/decrease/<pid>')
def decrease_quantity(pid):

    cart = session.get('cart', {})

    if pid in cart:
        cart[pid]['quantity'] -= 1

        # If quantity becomes 0 → remove item
        if cart[pid]['quantity'] <= 0:
            cart.pop(pid)

    session['cart'] = cart
    return redirect('/user/cart')


# =================================================================
# REMOVE ITEM
# =================================================================
@app.route('/user/cart/remove/<pid>')
def remove_from_cart(pid):

    cart = session.get('cart', {})

    if pid in cart:
        cart.pop(pid)

    session['cart'] = cart

    flash("Item removed!", "success")
    return redirect('/user/cart')


@app.route('/user/pay')
def user_pay():
    resp = require_user()
    if resp:
        return resp

    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty!", "danger")
        return redirect('/user/products')

    selected_items = session.get('checkout_items', [])
    if not selected_items:
        flash("Please select at least one product from your cart before payment.", "danger")
        return redirect('/user/checkout')

    selected_items = [pid for pid in selected_items if pid in cart]
    if not selected_items:
        flash("Selected products are no longer available in your cart. Please select again.", "danger")
        return redirect('/user/cart')

    selected_address = session.get('selected_address')
    if not selected_address:
        flash("Please choose a shipping address before continuing to payment.", "danger")
        return redirect('/user/checkout')

    total_amount = sum(cart[pid]['price'] * cart[pid]['quantity'] for pid in selected_items)
    if total_amount <= 0:
        flash("Selected cart total must be greater than zero.", "danger")
        return redirect('/user/cart')

    session['pending_order_items'] = selected_items

    razorpay_amount = int(total_amount * 100)  # convert to paise
    try:
        razorpay_order = razorpay_client.order.create({
            "amount": razorpay_amount,
            "currency": "INR",
            "payment_capture": "1"
        })
        session['razorpay_order_id'] = razorpay_order['id']
    except Exception:
        flash("Unable to create payment order right now. Please try again later.", "danger")
        return redirect('/user/checkout')

    return render_template(
        "user/payment.html",
        amount=total_amount,
        key_id=config.RAZORPAY_KEY_ID,
        order_id=session['razorpay_order_id'],
        selected_address=selected_address
    )


@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    resp = require_user()
    if resp:
        return resp

    # Read values posted from frontend
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')

    if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
        flash("Payment verification failed (missing data).", "danger")
        return redirect('/user/cart')

    # Build verification payload required by Razorpay client.utility
    payload = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }

    try:
        # This will raise an error if signature invalid
        razorpay_client.utility.verify_payment_signature(payload)

    except Exception as e:
        # Verification failed
        app.logger.error("Razorpay signature verification failed: ?", str(e))
        flash("Payment verification failed. Please contact support.", "danger")
        return redirect('/user/cart')

    # Signature verified — now store order and items into DB
    user_id = session['user_id']
    cart = session.get('cart', {})

    if not cart:
        flash("Cart is empty. Cannot create order.", "danger")
        return redirect('/user/products')

    # Calculate total amount (ensure same as earlier)
    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())

    # Get the selected shipping address at checkout time
    selected_address = session.get('selected_address', {})
    address_json = json.dumps(selected_address) if selected_address else None

    # DB insert: orders and order_items
    conn = get_db_connection()
    cursor = conn.cursor()

    ensure_orders_table()

    try:
        order_db_id = None

        # Try to insert with shipping_address + status (for newer DBs)
        try:
            cursor.execute("""
                INSERT INTO orders (user_id, razorpay_order_id, razorpay_payment_id, amount, payment_status, shipping_address, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, razorpay_order_id, razorpay_payment_id, total_amount, 'paid', address_json, 'pending'))
            order_db_id = cursor.lastrowid

        except Exception as insert_err:
            # Fallback: old database without shipping_address column
            if "Unknown column 'shipping_address'" in str(insert_err):
                app.logger.warning("shipping_address column missing — saving order without address")
                cursor.execute("""
                    INSERT INTO orders (user_id, razorpay_order_id, razorpay_payment_id, amount, payment_status, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, razorpay_order_id, razorpay_payment_id, total_amount, 'paid', 'pending'))
                order_db_id = cursor.lastrowid
            else:
                raise   # re-raise other errors

        # Insert all items
        for pid_str, item in cart.items():
            product_id = int(pid_str)
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                VALUES (?, ?, ?, ?, ?)
            """, (order_db_id, product_id, item['name'], item['quantity'], item['price']))

        # Commit transaction
        conn.commit()

        # Clear cart and temporary checkout data
        session.pop('cart', None)
        session.pop('razorpay_order_id', None)
        session.pop('selected_address', None)
        session.pop('checkout_items', None)

        flash("Payment successful and order placed!", "success")
        return redirect(f"/user/order-success/{order_db_id}")

    except Exception as e:
        # Rollback and log error
        conn.rollback()
        app.logger.error("Order storage failed: ?\n?", str(e), traceback.format_exc())
        flash("There was an error saving your order. Contact support.", "danger")
        return redirect('/user/cart')

    finally:
        cursor.close()
        conn.close()


# =================================================================
@app.route('/user/order-success/<int:order_db_id>')
def order_success(order_db_id):
    resp = require_user()
    if resp:
        return resp

    conn = get_db_connection()
    ensure_orders_table()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_id=? AND user_id=?", (order_db_id, session['user_id']))
    order = cursor.fetchone()

    cursor.execute("SELECT * FROM order_items WHERE order_id=?", (order_db_id,))
    items = cursor.fetchall()

    # Parse shipping address JSON if present
    shipping_address = {}
    if order and 'shipping_address' in order.keys() and order['shipping_address']:
        try:
            shipping_address = json.loads(order['shipping_address'])
        except Exception:
            shipping_address = {}

    cursor.close()
    conn.close()

    if not order:
        flash("Order not found.", "danger")
        return redirect('/user/products')

    return render_template("user/order_success.html", order=order, items=items, shipping_address=shipping_address)



@app.route('/user/download-invoice/<int:order_db_id>')
def download_invoice(order_db_id):
    resp = require_user()
    if resp:
        return resp

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_id=? AND user_id=?", (order_db_id, session['user_id']))
    order = cursor.fetchone()

    cursor.execute("SELECT * FROM order_items WHERE order_id=?", (order_db_id,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    if not order:
        flash("Order not found.", "danger")
        return redirect('/user/products')

    # Fetch customer name and email for the invoice
    conn2 = get_db_connection()
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT name, email FROM users WHERE user_id=?", (session['user_id'],))
    customer = cursor2.fetchone() or {'name': 'N/A', 'email': 'N/A'}

    # Parse shipping address safely (works even for old orders without the column)
    shipping_address = {}
    try:
        if order and 'shipping_address' in order.keys() and order['shipping_address']:
            shipping_address = json.loads(order['shipping_address'])
    except Exception:
        app.logger.warning("Could not parse shipping_address for order ?", order_db_id)
        shipping_address = {}

    # Temporary fallback: Use address from current session (for testing old orders)
    if not shipping_address:
        shipping_address = session.get('selected_address', {}) or {}

    cursor2.close()
    conn2.close()

    # Render invoice HTML template to string
    html = render_template("user/invoice.html", order=order, items=items, customer=customer, shipping_address=shipping_address)

    # Generate PDF bytes
    pdf = generate_pdf(html)
    if pdf is None:
        flash("Failed to generate PDF invoice.", "danger")
        return redirect(f"/user/order-success/{order_db_id}")

    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{order_db_id}.pdf'
    return response


# =================================================================
@app.route('/user/my-orders')
def my_orders():
    resp = require_user()
    if resp:
        return resp

    conn = get_db_connection()
    ensure_orders_table()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (session['user_id'],))
    orders = cursor.fetchall()
    cursor.close()   # Close immediately to avoid "Unread result found" / connector sync errors with sub-queries

    # Enrich each order with product names and address summary for the card display
    for order in orders:
        # Fetch product names for this order
        item_cursor = conn.cursor()
        item_cursor.execute(
            "SELECT product_name FROM order_items WHERE order_id=?",
            (order['order_id'],)
        )
        items = item_cursor.fetchall()
        item_cursor.close()

        names = [i['product_name'] for i in items]
        if len(names) > 2:
            order['product_summary'] = ", ".join(names[:2]) + f" +{len(names)-2} more"
        elif names:
            order['product_summary'] = ", ".join(names)
        else:
            order['product_summary'] = "No items"

        # Parse and summarize shipping address
        shipping_address = {}
        if 'shipping_address' in order.keys() and order['shipping_address']:
            try:
                shipping_address = json.loads(order['shipping_address'])
            except Exception:
                shipping_address = {}

        if shipping_address:
            parts = []
            if shipping_address.get('name'):
                parts.append(shipping_address['name'])
            if shipping_address.get('city'):
                parts.append(shipping_address['city'])
            if shipping_address.get('state'):
                parts.append(shipping_address['state'])
            order['address_summary'] = ", ".join(parts) if parts else "Address available"
        else:
            order['address_summary'] = "Address not available"

    conn.close()

    return render_template("user/my_orders.html", orders=orders)


@app.route('/user/cancel-order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    resp = require_user()
    if resp:
        return resp

    conn = get_db_connection()
    ensure_orders_table()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_id=? AND user_id=?", (order_id, session['user_id']))
    order = cursor.fetchone()

    if not order:
        flash("Order not found or access denied.", "danger")
        cursor.close()
        conn.close()
        return redirect('/user/my-orders')

    current_status = (order['status'] if 'status' in order.keys() and order['status'] else 'pending').lower().strip()

    if current_status != 'pending':
        flash("Order cannot be cancelled (already shipped, delivered or cancelled).", "warning")
        cursor.close()
        conn.close()
        return redirect('/user/my-orders')

    # Perform cancel
    try:
        cursor.execute("UPDATE orders SET status='cancelled' WHERE order_id=?", (order_id,))
        conn.commit()
        flash("Order #? has been cancelled successfully." % order_id, "success")
    except Exception as e:
        conn.rollback()
        app.logger.error("Cancel failed: ?", str(e))
        flash("Failed to cancel the order. Please try again.", "danger")

    cursor.close()
    conn.close()
    return redirect('/user/my-orders')


@app.route('/setup-orders-table')
def setup_orders_table():
    resp = require_admin()
    if resp:
        return resp

    ensure_orders_table()
    flash("Orders table migrated/updated successfully!", "success")
    return redirect('/admin/dashboard')


@app.route('/setup-products-fk')
def setup_products_fk():
    resp = require_admin()
    if resp:
        return resp

    current_admin = session.get('admin_id')
    ensure_products_admin_id_column(default_admin_id=current_admin)

    flash("Products table updated with admin_id foreign key + old products assigned to current admin!", "success")
    return redirect('/admin/dashboard')


if __name__ == '__main__':
    initialize_database()
    os.makedirs(os.path.join('static', 'upload', 'product_images'), exist_ok=True)
    os.makedirs(os.path.join('static', 'upload', 'profile_pics'), exist_ok=True)
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=config.DEBUG
    )



# http://127.0.0.1:5000/superadmin-login
