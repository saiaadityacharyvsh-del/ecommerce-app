# ▶️ START DEPLOYMENT NOW - Interactive Checklist

## 📍 YOU ARE HERE: Ready to Deploy

Start with **PHASE 1** and work through each section.  
Check off each item as you complete it. ✅

---

# 🎯 PHASE 1: PREPARE CREDENTIALS (10 minutes)

### Step 1.1: Get Gmail App Password ⏱️ 5 minutes
```
Goal: Get 16-character Gmail password
```

**Do this:**
1. [ ] Go to https://myaccount.google.com/apppasswords
2. [ ] Login with your Gmail
3. [ ] Select "Mail" from dropdown
4. [ ] Select "Windows Computer" from dropdown
5. [ ] Click "Generate"
6. [ ] Copy the 16-character password shown
7. [ ] **SAVE THIS:** Keep it in a notepad

**You should have:** `abcd efgh ijkl mnop` (16 characters, spaces included)

---

### Step 1.2: Get Razorpay Test Keys ⏱️ 5 minutes
```
Goal: Get Razorpay API keys
```

**Do this:**
1. [ ] Go to https://dashboard.razorpay.com/
2. [ ] Sign up or login
3. [ ] Go to **Settings** → **API Keys**
4. [ ] Copy **Key ID** (starts with `rzp_test_`)
5. [ ] Copy **Key Secret**
6. [ ] **SAVE THESE:** Keep them in notepad

**You should have:**
- Key ID: `rzp_test_xxxxxxxxxxxxx`
- Key Secret: `xxxxxxxxxxxxxxxxxxx`

---

### Step 1.3: Generate SECRET_KEY ⏱️ 2 minutes
```
Goal: Create random secret key
```

**Do this in PowerShell:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**You should see:** 
```
abc123def456xyz789...  (64 characters)
```

**SAVE THIS** in your notepad

---

## 🔧 PHASE 2: SETUP ENVIRONMENT (5 minutes)

### Step 2.1: Create .env file
```
Goal: Create file with your secrets
```

**Do this:**
1. [ ] Open PowerShell in your project folder
2. [ ] Run: `copy .env.example .env`
3. [ ] Run: `notepad .env`

---

### Step 2.2: Edit .env file
```
Goal: Add your actual values
```

**Current .env will look like:**
```
SECRET_KEY=your-super-secret-key-here-change-this-in-production
MAIL_USERNAME=your-email@gmail.com
...
```

**Replace with YOUR values:**

1. [ ] Find line: `SECRET_KEY=...`
   - Replace with your generated key (from Step 1.3)

2. [ ] Find line: `MAIL_USERNAME=...`
   - Replace with your Gmail: `youremail@gmail.com`

3. [ ] Find line: `MAIL_PASSWORD=...`
   - Replace with Gmail app password (from Step 1.2)
   - Example: `abcd efgh ijkl mnop`

4. [ ] Find line: `RAZORPAY_KEY_ID=...`
   - Replace with your Razorpay Key ID

5. [ ] Find line: `RAZORPAY_KEY_SECRET=...`
   - Replace with your Razorpay Secret

6. [ ] Find line: `DEBUG=False`
   - Leave as `False` (important for production!)

**Save:** `Ctrl+S` then close

---

## ✅ PHASE 3: TEST LOCALLY (5 minutes)

### Step 3.1: Install dependencies
```bash
pip install -r requirements.txt
```

**Wait for:** "Successfully installed Flask, Gunicorn..."

- [ ] Installed

---

### Step 3.2: Start your app
```bash
python app.py
```

**Wait for:** 
```
 * Running on http://0.0.0.0:5000
```

- [ ] Running

---

### Step 3.3: Test in browser
```
Do this: Open browser and visit http://localhost:5000
```

- [ ] You see your e-commerce app homepage
- [ ] No error messages

**Stop the app:** Press `Ctrl+C` in PowerShell

---

## 🐙 PHASE 4: GITHUB SETUP (10 minutes)

### Step 4.1: Create GitHub account
```
If you don't have one yet
```

1. [ ] Go to https://github.com/signup
2. [ ] Fill in email, password, username
3. [ ] Verify email
4. [ ] GitHub account ready

---

### Step 4.2: Create repository
```
Where your code will live on internet
```

1. [ ] Go to https://github.com/new
2. [ ] **Repository name:** `ecommerce-app`
3. [ ] **Description:** `Flask E-Commerce App`
4. [ ] **Visibility:** Public (important!)
5. [ ] Click **Create repository**
6. [ ] Copy the URL shown (looks like https://github.com/YOUR_USERNAME/ecommerce-app.git)

- [ ] Repository created

---

### Step 4.3: Configure Git locally
```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@gmail.com"
```

- [ ] Git configured

---

### Step 4.4: Push code to GitHub
```bash
git init
git add .
git commit -m "Initial commit - production ready e-commerce app"
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-app.git
git branch -M main
git push -u origin main
```

**Important:** Replace `YOUR_USERNAME` with your GitHub username

**Wait for:** "Counting objects, Writing objects..."

- [ ] Code pushed to GitHub

---

### Step 4.5: Verify on GitHub
```
Do this: Visit https://github.com/YOUR_USERNAME/ecommerce-app
```

1. [ ] You see all your files
2. [ ] `.env` file is NOT visible (protected by .gitignore) ✅
3. [ ] Files like app.py, requirements.txt are visible

**If .env IS visible:**
- Delete .env from GitHub
- Run: `git rm --cached .env`

---

## 🚀 PHASE 5: DEPLOY TO PYTHONANYWHERE (15 minutes)

### Step 5.1: Create PythonAnywhere account
```
https://www.pythonanywhere.com
```

1. [ ] Go to https://www.pythonanywhere.com/
2. [ ] Click **Pricing** → **Free** tier
3. [ ] Sign up with email
4. [ ] Verify email
5. [ ] Login

- [ ] Account created

---

### Step 5.2: Clone your code on PythonAnywhere
```
Do this: In PythonAnywhere
```

1. [ ] Go to **Consoles** tab
2. [ ] Click **Bash** console
3. [ ] Run:
```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-app.git
cd ecommerce-app
```

- [ ] Code cloned

---

### Step 5.3: Create virtual environment
```bash
mkvirtualenv --python=/usr/bin/python3.11 ecommerce
pip install -r requirements.txt
```

**Wait for:** "Successfully installed..." (2-3 minutes)

- [ ] Virtual environment ready

---

### Step 5.4: Create .env on PythonAnywhere
```bash
nano .env
```

1. [ ] Paste your .env values (same as local)
2. [ ] Press `Ctrl+X`
3. [ ] Press `Y`
4. [ ] Press `Enter`

- [ ] .env created on PythonAnywhere

---

### Step 5.5: Go to Web app section
```
Do this: In PythonAnywhere dashboard
```

1. [ ] Click **Web** tab
2. [ ] Click **Add a new web app**

---

### Step 5.6: Select Python & Flask
```
Choose settings
```

1. [ ] Select **Python 3.11**
2. [ ] Select **Flask**

- [ ] Web app created

---

### Step 5.7: Edit WSGI file
```
Do this: In Web app settings
```

1. [ ] Find "WSGI configuration file" link
2. [ ] Click on it (opens text editor)
3. [ ] Delete all content
4. [ ] Paste this:

```python
import os
import sys

path = '/home/YOUR_PYTHONANYWHERE_USERNAME/ecommerce-app'
if path not in sys.path:
    sys.path.append(path)

os.chdir(path)

from dotenv import load_dotenv
load_dotenv()

from app import app as application
```

⚠️ **Replace:** `YOUR_PYTHONANYWHERE_USERNAME` with your actual username (shown in top right)

5. [ ] Save (Ctrl+S)

---

### Step 5.8: Set Virtualenv
```
Do this: Back in Web app settings
```

1. [ ] Find **Virtualenv** section
2. [ ] Click the path field
3. [ ] Enter: `/home/YOUR_PYTHONANYWHERE_USERNAME/.virtualenvs/ecommerce`
4. [ ] Press Enter

- [ ] Virtualenv set

---

### Step 5.9: Set Environment Variables
```
Do this: In Web app settings
```

1. [ ] Find **Environment variables** section
2. [ ] Add these ONE BY ONE:

| Variable | Value |
|----------|-------|
| SECRET_KEY | Your generated key |
| MAIL_SERVER | smtp.gmail.com |
| MAIL_PORT | 587 |
| MAIL_USE_TLS | True |
| MAIL_USERNAME | your-email@gmail.com |
| MAIL_PASSWORD | your-app-password |
| RAZORPAY_KEY_ID | your-key |
| RAZORPAY_KEY_SECRET | your-secret |
| DEBUG | False |

- [ ] All variables added

---

### Step 5.10: Set Source code
```
Do this: In Web app settings
```

1. [ ] Find **Source code** section
2. [ ] Enter: `/home/YOUR_PYTHONANYWHERE_USERNAME/ecommerce-app`

---

### Step 5.11: RELOAD YOUR APP
```
⚠️ IMPORTANT: Don't forget this step!
```

1. [ ] Find big green **Reload** button at top
2. [ ] Click it
3. [ ] Wait 10 seconds

---

## ✨ PHASE 6: YOUR APP IS LIVE!

### Step 6.1: Get your live URL
```
Your app is now at:
https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com
```

- [ ] Visit this URL in your browser

---

### Step 6.2: Test your app
```
Do this: Test all features
```

1. [ ] Can you see the homepage? ✅
2. [ ] Try user login
3. [ ] Try user signup
4. [ ] Try admin login

**If you see errors:**
- Go to **Web** tab
- Scroll down to **Error log**
- Check what the error is

---

### Step 6.3: Test email sending (Optional)
```
Do this: Try "Forgot Password" feature
```

1. [ ] Click "Forgot Password"
2. [ ] Enter an email
3. [ ] Check if email arrives
4. [ ] If not, check MAIL_PASSWORD is correct

---

### Step 6.4: Test Razorpay (Optional)
```
Do this: Try checkout with test card
```

1. [ ] Add product to cart
2. [ ] Go to checkout
3. [ ] Use test card: `4111 1111 1111 1111`
4. [ ] Expiry: `12/25`
5. [ ] CVV: `123`
6. [ ] Should show "Payment Successful"

---

## 🎉 YOU'RE DONE!

```
✅ Your app is LIVE on the internet!
✅ Anyone can access it with your URL
✅ Your code is on GitHub
✅ Your secrets are protected (.env not visible)
```

### Your live app URL:
```
https://YOUR_USERNAME.pythonanywhere.com
```

### Share this URL with:
- [ ] Friends
- [ ] Family  
- [ ] Your portfolio
- [ ] Your resume

---

## 📊 WHAT YOU ACCOMPLISHED

| Task | Status |
|------|--------|
| Local setup | ✅ Complete |
| Environment variables | ✅ Secure |
| GitHub repository | ✅ Online |
| Code deployed | ✅ Live |
| App accessible | ✅ 24/7 |

---

## ⏱️ TIME TAKEN

- Phase 1 (Credentials): `___` min
- Phase 2 (Setup): `___` min
- Phase 3 (Local test): `___` min
- Phase 4 (GitHub): `___` min
- Phase 5 (Deploy): `___` min
- **TOTAL: `___` minutes**

(Typical: 35-45 minutes total)

---

## 🆘 NEED HELP?

| Issue | Solution |
|-------|----------|
| Can't find app password | See Step 1.2 or EXACT_COMMANDS.md |
| Git push fails | Check GitHub URL is correct |
| App not loading | Check Error log in PythonAnywhere Web tab |
| Email not working | Verify MAIL_PASSWORD is 16-char app password |
| Razorpay test fails | Use exact test card numbers from Step 6.4 |

---

## ✅ FINAL CHECKLIST

Before you celebrate, verify:

- [ ] Live URL is accessible
- [ ] Homepage loads
- [ ] No CSS/styling issues
- [ ] Database works (products load)
- [ ] At least one feature tested
- [ ] .env is NOT on GitHub
- [ ] code is on GitHub

**All checked? Congratulations! 🎉 Your app is deployed!**

---

**Status:** Ready to Deploy Now ✅  
**Next Action:** Start with Step 1.1 above
