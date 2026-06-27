# MyShop - Flask E-Commerce Application

A simple, clean Flask-based e-commerce application with admin and user dashboards, payment integration, and email notifications.

## 🎯 Features

- **User System:** Registration, login, profile management
- **Admin Panel:** Product management, order tracking, revenue analysis
- **Super Admin:** Overall dashboard, admin management
- **Payment Gateway:** Razorpay integration for online payments
- **Email Notifications:** Order confirmations, password resets
- **Shopping Cart:** Add/remove products, checkout
- **PDF Invoices:** Automatic invoice generation
- **User Dashboard:** Order history, shipping addresses
- **Product Management:** Upload images, manage inventory

## 📋 Requirements

- Python 3.11+
- Flask
- SQLite (included with Python)
- See `requirements.txt` for all dependencies

## 🚀 Quick Start (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-app.git
cd ecommerce-app
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 5. Run the application
```bash
python app.py
```

Visit `http://localhost:5000`

## 🔐 Environment Variables

Create a `.env` file (copy from `.env.example`) and add:

```
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
DEBUG=False
```

## 🌐 Deployment

For cloud deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Quick Links:**
- [Deploy to Heroku](DEPLOYMENT_GUIDE.md#option-1-deploy-to-heroku-recommended-for-beginners)
- [Deploy to PythonAnywhere](DEPLOYMENT_GUIDE.md#option-2-deploy-to-pythonanywhere-easiest-for-python-apps)
- [Deploy to Railway.app](DEPLOYMENT_GUIDE.md#option-3-deploy-to-railwayapp)

## 📁 Project Structure

```
ecommerce-app/
├── app.py                 # Main application file
├── config.py              # Configuration (uses environment variables)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── Procfile               # Heroku deployment config
├── runtime.txt            # Python version for deployment
├── DEPLOYMENT_GUIDE.md    # Detailed deployment instructions
├── README.md              # This file
├── static/
│   ├── css/
│   │   └── style.css
│   └── upload/            # User uploads (images, profiles)
├── templates/
│   ├── base.html
│   ├── admin/             # Admin templates
│   ├── superadmin/        # Super admin templates
│   └── user/              # User templates
└── utils/
    └── pdf_generator.py   # Invoice PDF generation
```

## 🔧 Configuration

### Email Setup (Gmail)
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use 16-char password in MAIL_PASSWORD

### Payment Setup (Razorpay)
1. Sign up at https://razorpay.com
2. Get API keys from Settings → API Keys
3. Use Test keys for development, Live keys for production

## 📚 API Routes

### User Routes
- `GET /user-login` - User login page
- `POST /user-signup` - User registration
- `GET /user/home` - User dashboard
- `GET /user/products` - Browse products
- `GET /user/cart` - Shopping cart
- `POST /user/checkout` - Checkout process

### Admin Routes
- `GET /admin-login` - Admin login
- `GET /admin/dashboard` - Admin dashboard
- `POST /admin/add-product` - Add new product
- `GET /admin/orders` - View orders

### Super Admin Routes
- `GET /superadmin-login` - Super admin login
- `GET /superadmin/dashboard` - System overview
- `GET /superadmin/admins` - Manage admins
- `GET /superadmin/revenue` - Revenue analytics

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Email not sending | Check MAIL_USERNAME, MAIL_PASSWORD, and use App Password from Gmail |
| File uploads not working | Ensure `static/upload` folder exists and has write permissions |
| Database error | Delete `smartcart.db` and restart app to reinitialize |
| Import errors | Run `pip install -r requirements.txt` |

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements.

## 📄 License

This project is open source and available under the MIT License.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Status:** ✅ Production Ready  
**Last Updated:** 2025  
**Author:** Your Name
