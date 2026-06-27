# config.py
# ------------------------------------
# This file holds all configurations
# Load from environment variables for security
# ------------------------------------

import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_change_in_production')

# Database Configuration
DB_PATH = os.getenv('DB_PATH', 'smartcart.db')

# Email SMTP Settings
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

# Flask App Settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/upload')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
