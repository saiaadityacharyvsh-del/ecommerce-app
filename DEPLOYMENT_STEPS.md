# 🚀 Complete Deployment Process - Step by Step

## PART 1: PREPARE YOUR LOCAL PROJECT (30 minutes)

### Step 1.1: Setup Environment Variables
```bash
# Navigate to your project
cd "c:\Users\sowmy\OneDrive\Documents\Desktop\ecommers app - Copy"

# Copy the template
copy .env.example .env

# Edit .env file with your actual values (see below for how to get each value)
```

**Edit `.env` with these values:**

```
SECRET_KEY=your-random-secret-key-here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
DEBUG=False
UPLOAD_FOLDER=static/upload
```

**How to get each value:**

#### A) SECRET_KEY (Generate a random one)
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste in .env

#### B) MAIL_USERNAME & MAIL_PASSWORD (Gmail)
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Google will generate a 16-character password
4. Copy it to MAIL_PASSWORD in .env

#### C) RAZORPAY_KEY_ID & RAZORPAY_KEY_SECRET
1. Go to https://dashboard.razorpay.com/
2. Sign up or login
3. Go to Settings → API Keys
4. Copy "Key ID" and "Key Secret" (Test keys)
5. Paste in .env

---

### Step 1.2: Test Locally
```bash
# Install all dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://0.0.0.0:5000
```

**Test in browser:** Visit http://localhost:5000

If you see errors, check:
- `.env` file exists and has correct values
- All dependencies installed (`pip install -r requirements.txt`)
- Port 5000 is not in use

---

## PART 2: SETUP GITHUB (10 minutes)

### Step 2.1: Create GitHub Account
1. Go to https://github.com/signup
2. Enter email, password, username
3. Verify your email

### Step 2.2: Create Repository
1. Go to https://github.com/new
2. **Repository name:** `ecommerce-app`
3. **Description:** `Flask E-Commerce Application with Admin Panel`
4. **Visibility:** Public (required for free deployment)
5. Click **Create repository**
6. Copy the repository URL (looks like `https://github.com/YOUR_USERNAME/ecommerce-app.git`)

### Step 2.3: Push Code to GitHub

```bash
# Configure Git (one time only)
git config --global user.name "Your Full Name"
git config --global user.email "your-email@gmail.com"

# Navigate to project
cd "c:\Users\sowmy\OneDrive\Documents\Desktop\ecommers app - Copy"

# Initialize Git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - production ready e-commerce app"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-app.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**Verify on GitHub:**
- Go to https://github.com/YOUR_USERNAME/ecommerce-app
- You should see all your files
- **Important:** `.env` file should NOT be visible (protected by `.gitignore`)

---

## PART 3: DEPLOY TO PYTHONANYWHERE (Recommended - 15 minutes)

### Why PythonAnywhere?
✅ No credit card needed  
✅ Free tier available  
✅ Best for Flask apps  
✅ Automatic HTTPS  
✅ Easy setup  

### Step 3.1: Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com/
2. Click **Pricing** → **Free** tier
3. Enter email and create account
4. Verify email

### Step 3.2: Setup Your App

**A) Open Bash Console:**
- Dashboard → **Consoles** → **Bash** → Click to open

**B) Clone your GitHub repository:**
```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-app.git
cd ecommerce-app
```

**C) Create virtual environment:**
```bash
# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.11 ecommerce

# Install dependencies
pip install -r requirements.txt
```

**D) Create `.env` file on PythonAnywhere:**
```bash
# Use nano editor
nano .env
```

Paste your environment variables:
```
SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
DEBUG=False
UPLOAD_FOLDER=static/upload
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

### Step 3.3: Configure Web App

**A) Go to Web tab:**
- Dashboard → **Web**
- Click **Add a new web app**

**B) Choose Python and Framework:**
- Select **Python 3.11**
- Select **Flask**

**C) Create WSGI configuration:**
- Click on the **WSGI configuration file** link
- Replace the entire content with:

```python
import os
import sys

# Add your project path
path = '/home/YOUR_PYTHONANYWHERE_USERNAME/ecommerce-app'
if path not in sys.path:
    sys.path.append(path)

# Change to app directory
os.chdir(path)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import and run Flask app
from app import app as application
```

**Save the file**

**D) Set Virtualenv:**
- Go back to Web app settings
- Find **Virtualenv** section
- Click and enter: `/home/YOUR_PYTHONANYWHERE_USERNAME/.virtualenvs/ecommerce`

**E) Set Environment Variables:**
- Scroll to **Web app settings**
- Under **Environment variables**, add each from your `.env`:
  - SECRET_KEY
  - MAIL_USERNAME
  - MAIL_PASSWORD
  - RAZORPAY_KEY_ID
  - RAZORPAY_KEY_SECRET

**F) Set Source code location:**
- Source code: `/home/YOUR_PYTHONANYWHERE_USERNAME/ecommerce-app`

**G) Reload your app:**
- Click green **Reload** button at top

---

### Step 3.4: Test Your Live App

**Your app is now live at:**
```
https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com
```

**Visit in browser:**
- If you see your app → ✅ **SUCCESS!**
- If you see error → Check **Error log** in Web tab

---

## PART 4: ALTERNATIVE DEPLOYMENT OPTIONS

### Option A: Deploy to Heroku (Popular)

**Prerequisites:** Heroku CLI installed

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set MAIL_USERNAME="your-email@gmail.com"
heroku config:set MAIL_PASSWORD="your-app-password"
heroku config:set RAZORPAY_KEY_ID="your-key"
heroku config:set RAZORPAY_KEY_SECRET="your-secret"
heroku config:set DEBUG="False"

# Deploy from Git
git push heroku main

# View logs
heroku logs --tail

# Visit your app
heroku open
```

---

### Option B: Deploy to Railway.app (Modern & Affordable)

1. Go to https://railway.app
2. Click **Dashboard** → **New Project**
3. Select **Deploy from GitHub repo**
4. Select your `ecommerce-app` repository
5. Add environment variables from your `.env`
6. Deploy (automatic!)

**Your app will be live at:**
```
https://your-app-[random-string].railway.app
```

---

## PART 5: AFTER DEPLOYMENT

### Step 5.1: Verify Everything Works

Test these features:
- ✅ User login/register
- ✅ Admin login
- ✅ Product browsing
- ✅ Email sending (check spam folder)
- ✅ File uploads (product images)
- ✅ Razorpay payment (test mode)

### Step 5.2: Switch to Production Keys (When Ready)

```bash
# Go to Razorpay dashboard
# Settings → API Keys → Copy Live keys
# Update environment variables with Live keys
```

**For PythonAnywhere:**
- Dashboard → Web → Environment variables
- Update RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET

**For Heroku:**
```bash
heroku config:set RAZORPAY_KEY_ID="your-live-key"
heroku config:set RAZORPAY_KEY_SECRET="your-live-secret"
```

### Step 5.3: Setup Custom Domain (Optional)

PythonAnywhere:
- Web tab → Domain name section
- Add your custom domain

Heroku:
```bash
heroku domains:add example.com
```

---

## TROUBLESHOOTING

### "Module not found" Error
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Email not sending
- Check MAIL_USERNAME is correct
- Verify MAIL_PASSWORD is 16-char app password (not regular password)
- Check Gmail 2FA is enabled
- Verify App Passwords at https://myaccount.google.com/apppasswords

### Database errors
- For PythonAnywhere: Database initializes automatically on first run
- If error persists: Delete `smartcart.db` and reload

### File uploads not working
- Ensure `static/upload` folder exists
- For cloud: Use external storage (AWS S3 or Cloudinary)

### Static files (CSS) not loading
- Flask serves static files automatically
- If not working: Clear browser cache (Ctrl+Shift+Delete)

---

## DEPLOYMENT CHECKLIST

- [ ] Created `.env` with all credentials
- [ ] Tested locally (`python app.py`)
- [ ] Created GitHub account
- [ ] Pushed code to GitHub
- [ ] Created PythonAnywhere/Heroku account
- [ ] Cloned repository on hosting platform
- [ ] Installed dependencies
- [ ] Configured WSGI/Procfile
- [ ] Set environment variables
- [ ] Reloaded app
- [ ] Tested live app
- [ ] Email working
- [ ] Razorpay integration working

---

## LIVE APP URLS

| Platform | Your URL |
|----------|----------|
| **PythonAnywhere** | `https://USERNAME.pythonanywhere.com` |
| **Heroku** | `https://your-app-name.herokuapp.com` |
| **Railway.app** | `https://your-app-[random].railway.app` |

---

## QUICK REFERENCE

### Most Important Files
```
.env                 ← Your secrets (keep private!)
config.py           ← Loads from .env
requirements.txt    ← All dependencies
Procfile            ← Heroku config
runtime.txt         ← Python version
app.py              ← Main app
```

### Essential Commands
```bash
pip install -r requirements.txt    # Install dependencies
python app.py                       # Run locally
git add .                           # Stage changes
git commit -m "message"             # Commit
git push                            # Push to GitHub
```

---

**Status:** Ready for Deployment ✅  
**Recommended Platform:** PythonAnywhere  
**Estimated Time:** 30-45 minutes total
