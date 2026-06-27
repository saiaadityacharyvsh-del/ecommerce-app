# MyShop E-Commerce App - Deployment Guide

## ✅ Pre-Deployment Checklist

Your project is now compatible for deployment! Here's what was fixed:

- ✅ Removed hardcoded credentials (moved to `.env`)
- ✅ Added environment variable support
- ✅ Created production-ready configuration
- ✅ Added Gunicorn for production WSGI server
- ✅ Updated dependencies with version pinning
- ✅ Created `.gitignore` to protect sensitive files
- ✅ Added `Procfile` for cloud deployment
- ✅ Added `runtime.txt` for Python version specification

## 🚀 Deployment Options

### Option 1: Deploy to Heroku (Recommended for beginners)

#### Prerequisites:
- GitHub account
- Heroku account (https://www.heroku.com)
- Heroku CLI installed

#### Steps:

1. **Initialize Git repository:**
   ```bash
   cd "c:\Users\sowmy\OneDrive\Documents\Desktop\ecommers app - Copy"
   git init
   git add .
   git commit -m "Initial commit - ready for deployment"
   ```

2. **Create a GitHub repository:**
   - Go to https://github.com/new
   - Create a new repository named `ecommerce-app`
   - Push your local code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ecommerce-app.git
   git branch -M main
   git push -u origin main
   ```

3. **Create Heroku app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

4. **Set environment variables on Heroku:**
   ```bash
   heroku config:set SECRET_KEY="your-random-secret-key"
   heroku config:set MAIL_USERNAME="your-email@gmail.com"
   heroku config:set MAIL_PASSWORD="your-app-password"
   heroku config:set RAZORPAY_KEY_ID="your-razorpay-key"
   heroku config:set RAZORPAY_KEY_SECRET="your-razorpay-secret"
   heroku config:set DEBUG="False"
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **View logs:**
   ```bash
   heroku logs --tail
   ```

---

### Option 2: Deploy to PythonAnywhere (Easiest for Python apps)

#### Prerequisites:
- PythonAnywhere account (https://www.pythonanywhere.com)

#### Steps:

1. **Push to GitHub (same as Option 1, steps 1-2)**

2. **On PythonAnywhere dashboard:**
   - Click "Add a new web app"
   - Choose "Python 3.11" + "Flask"
   - Clone your GitHub repo in the code section:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ecommerce-app.git
   ```

3. **Set up virtual environment:**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 myapp
   pip install -r requirements.txt
   ```

4. **Configure WSGI file** (edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`):
   ```python
   import os
   import sys
   
   path = '/home/yourusername/ecommerce-app'
   if path not in sys.path:
       sys.path.append(path)
   
   os.chdir(path)
   from app import app as application
   ```

5. **Set environment variables** in Web app settings section

6. **Reload your app**

---

### Option 3: Deploy to Railway.app

#### Prerequisites:
- Railway account (https://railway.app)

#### Steps:

1. **Push to GitHub (same as Option 1)**

2. **On Railway dashboard:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your ecommerce-app repository
   - Railway auto-detects Flask app

3. **Add environment variables:**
   - Go to Variables section
   - Add all variables from `.env.example`

4. **Deploy automatically (happens on git push)**

---

### Option 4: Deploy Locally with Docker (Advanced)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p static/upload/product_images static/upload/profile_pics

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

Create a `docker-compose.yml`:
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - MAIL_USERNAME=${MAIL_USERNAME}
      - MAIL_PASSWORD=${MAIL_PASSWORD}
      - RAZORPAY_KEY_ID=${RAZORPAY_KEY_ID}
      - RAZORPAY_KEY_SECRET=${RAZORPAY_KEY_SECRET}
```

---

## 🔐 Important Security Notes

### Before pushing to GitHub:

1. **Create `.env` file locally (NOT in git):**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

2. **Verify `.gitignore` is working:**
   ```bash
   git status  # Should NOT show .env or smartcart.db
   ```

3. **Generate a strong SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### Gmail App Password Setup:

1. Enable 2-Factor Authentication on your Gmail account
2. Go to: https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Generate a 16-character password
5. Use this in MAIL_PASSWORD, not your actual Gmail password

### Razorpay Setup:

1. Sign up at https://razorpay.com
2. Go to Settings → API Keys
3. Copy Test Key ID and Secret
4. Use these in RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET

---

## 🔄 GitHub Setup Instructions

1. **Create GitHub Account:**
   - Go to https://github.com/signup

2. **Create New Repository:**
   - Click "+" → "New repository"
   - Name: `ecommerce-app`
   - Description: "Flask E-Commerce Application"
   - Public (so deployment platforms can access it)

3. **Push Your Code:**
   ```bash
   cd "c:\Users\sowmy\OneDrive\Documents\Desktop\ecommers app - Copy"
   git config --global user.email "your-email@gmail.com"
   git config --global user.name "Your Name"
   git init
   git add .
   git commit -m "Initial commit - production ready"
   git remote add origin https://github.com/YOUR_USERNAME/ecommerce-app.git
   git branch -M main
   git push -u origin main
   ```

4. **Verify on GitHub:**
   - Visit https://github.com/YOUR_USERNAME/ecommerce-app
   - You should see your files (but NOT `.env` or `smartcart.db`)

---

## 📋 Post-Deployment Checklist

- ✅ Database initializes on first run
- ✅ Email configuration tested
- ✅ Razorpay payment gateway connected
- ✅ File uploads working (check `static/upload` permissions)
- ✅ Static files loading correctly
- ✅ All routes responding

---

## ⚠️ Common Issues & Fixes

### Issue: Database not initializing
**Solution:** Ensure `initialize_database()` is called in Procfile release phase
```
release: python -c "from app import initialize_database; initialize_database()"
```

### Issue: Static files not loading (CSS/JS)
**Solution:** Flask serves static files automatically from `static/` folder

### Issue: Email not sending
**Solution:** 
- Check MAIL_USERNAME and MAIL_PASSWORD are correct
- Use Gmail App Password, not regular password
- Enable "Less secure app access" if needed

### Issue: File uploads not working
**Solution:**
- Ensure `static/upload` folder exists
- Check folder permissions
- For cloud (Heroku), use external storage (AWS S3, Cloudinary)

### Issue: "Module not found" errors
**Solution:** 
```bash
pip install -r requirements.txt
```

---

## 📱 For Production (After Testing)

1. **Switch Razorpay to Live Keys:**
   - Go to Razorpay Dashboard → Settings
   - Copy Live Key ID and Secret
   - Update environment variables

2. **Set DEBUG=False:**
   ```bash
   heroku config:set DEBUG="False"  # or equivalent for your platform
   ```

3. **Enable HTTPS:**
   - All deployment platforms provide free HTTPS

4. **Monitor Performance:**
   - Use platform's dashboard
   - Set up error alerts

---

## 💬 Need Help?

- **Heroku Docs:** https://devcenter.heroku.com
- **PythonAnywhere Docs:** https://www.pythonanywhere.com/help
- **Flask Docs:** https://flask.palletsprojects.com
- **GitHub Docs:** https://docs.github.com

---

**Created:** 2025  
**Status:** Ready for Production ✅
