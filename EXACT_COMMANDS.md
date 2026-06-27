# 🎯 EXACT COMMANDS TO RUN - Copy & Paste

## LOCAL SETUP (Do these on your computer)

### 1️⃣ Copy .env template
```bash
copy .env.example .env
```
✅ This creates `.env` file

### 2️⃣ Edit .env with your values
```bash
# Open in Notepad
notepad .env
```

Add these (replace with YOUR values):
```
SECRET_KEY=your-random-key-here
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-16-char-app-password
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
DEBUG=False
```

✅ Save and close

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

✅ Should see "Successfully installed Flask, Gunicorn, etc..."

### 4️⃣ Test locally
```bash
python app.py
```

✅ Should see:
```
 * Running on http://0.0.0.0:5000
```

Visit: http://localhost:5000 in browser

---

## GITHUB SETUP (Push your code online)

### 5️⃣ Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@gmail.com"
```

✅ Done (only need to do once)

### 6️⃣ Initialize Git
```bash
git init
```

✅ Creates `.git` folder

### 7️⃣ Add files
```bash
git add .
```

✅ Stages all files

### 8️⃣ Create commit
```bash
git commit -m "Initial commit - production ready"
```

✅ Should show files added

### 9️⃣ Add remote repository
```bash
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-app.git
```

⚠️ **Replace:**
- `YOUR_USERNAME` with your GitHub username

✅ Links to your GitHub

### 🔟 Push to GitHub
```bash
git branch -M main
git push -u origin main
```

✅ Should see "Counting objects, Writing objects"

---

## PYTHONANYWHERE DEPLOYMENT (Recommended!)

### 1️⃣ Go to PythonAnywhere
https://www.pythonanywhere.com

### 2️⃣ Open Bash Console
Dashboard → Consoles → Bash → Open bash console

### 3️⃣ Clone your GitHub repo
```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-app.git
cd ecommerce-app
```

✅ Files downloaded

### 4️⃣ Create virtual environment
```bash
mkvirtualenv --python=/usr/bin/python3.11 ecommerce
pip install -r requirements.txt
```

✅ All dependencies installed (may take 2-3 minutes)

### 5️⃣ Create .env file
```bash
nano .env
```

Paste:
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

✅ Press: **Ctrl+X**, then **Y**, then **Enter**

### 6️⃣ Go to Web tab
Dashboard → Web → Add a new web app

### 7️⃣ Select Python 3.11 + Flask

### 8️⃣ Edit WSGI file
Click on WSGI configuration file link (looks like `/var/www/`)

Replace entire content with:
```python
import os
import sys

path = '/home/YOUR_USERNAME/ecommerce-app'
if path not in sys.path:
    sys.path.append(path)

os.chdir(path)

from dotenv import load_dotenv
load_dotenv()

from app import app as application
```

⚠️ Replace `YOUR_USERNAME` with your PythonAnywhere username

✅ Save

### 9️⃣ Set Virtualenv path
Web tab → Virtualenv:
```
/home/YOUR_USERNAME/.virtualenvs/ecommerce
```

✅ Enter

### 🔟 Set Environment variables
Web tab → Environment variables:
Add these one by one:
- `SECRET_KEY` = your-secret-key
- `MAIL_USERNAME` = your-email
- `MAIL_PASSWORD` = app-password
- `RAZORPAY_KEY_ID` = your-key
- `RAZORPAY_KEY_SECRET` = your-secret

### 1️⃣1️⃣ Set Source code
Web tab → Source code:
```
/home/YOUR_USERNAME/ecommerce-app
```

### 1️⃣2️⃣ RELOAD APP
Click green **Reload** button

---

## ✅ YOUR APP IS LIVE!

**Your app is now live at:**
```
https://YOUR_USERNAME.pythonanywhere.com
```

---

## TESTING YOUR LIVE APP

1. **Visit your URL:** `https://YOUR_USERNAME.pythonanywhere.com`
2. **Try user login:** Go to `/user-login`
3. **Try admin login:** Go to `/admin-login`
4. **Test email:** Try "Forgot Password"
5. **Test payment:** Try checkout with test card

### Test Razorpay Card
Use these test cards:
- Card: `4111 1111 1111 1111`
- Expiry: `12/25`
- CVV: `123`

---

## IF YOU GET ERRORS

### Error: "ModuleNotFoundError: No module named 'flask'"
```bash
# In PythonAnywhere bash:
pip install -r requirements.txt
```

### Error: "No such file or directory: '.env'"
```bash
# Check .env exists:
ls -la .env

# If not, create it:
nano .env
# (paste content and save)
```

### Error: "WSGI application not found"
Check your WSGI file path is correct in step 8

### Email not working
- Verify MAIL_USERNAME is correct
- Use 16-char Google App Password (not regular password)
- Enable App Passwords: https://myaccount.google.com/apppasswords

### Can't see your app after reload
- Wait 10 seconds and refresh
- Check **Error log** in Web tab
- Check `.env` file exists and has values

---

## HEROKU ALTERNATIVE (if you prefer)

```bash
# Install Heroku CLI first

heroku login
heroku create your-app-name
heroku config:set SECRET_KEY="your-key"
heroku config:set MAIL_USERNAME="your-email@gmail.com"
heroku config:set MAIL_PASSWORD="your-password"
heroku config:set RAZORPAY_KEY_ID="your-key"
heroku config:set RAZORPAY_KEY_SECRET="your-secret"
heroku config:set DEBUG="False"
git push heroku main
heroku open
```

---

## RAILWAY.APP ALTERNATIVE

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select your `ecommerce-app` repo
5. Add environment variables
6. Deploy!

Your app: `https://your-app-[random].railway.app`

---

## SUMMARY

| Step | What | Time |
|------|------|------|
| 1-4 | Local setup & test | 10 min |
| 5-10 | GitHub setup | 10 min |
| 1-12 | PythonAnywhere deploy | 15 min |
| **Total** | **Everything** | **35 min** |

---

**Status:** Ready to Deploy ✅  
**Estimated Time:** ~35 minutes  
**Difficulty:** Easy ⭐⭐☆☆☆
