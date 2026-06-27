# 🚀 Master Deployment Checklist

**Complete these steps in order to deploy your e-commerce app to GitHub & PythonAnywhere**

---

## PHASE 1: GitHub Setup (Local Machine)

### ✓ Step 1: Open PowerShell

```
Open a PowerShell terminal in your project folder
```

### ✓ Step 2: Initialize Git

```powershell
git init
git config user.name "Your Name"
git config user.email "your.email@gmail.com"
```

### ✓ Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `ecommerce-app`
   - **Description:** `Python Flask E-commerce App`
   - **Privacy:** Private (to keep credentials safe)
3. **DO NOT** check "Add README" (we have one)
4. Click **"Create repository"**
5. **Copy the URL** shown (looks like `https://github.com/YOUR_USERNAME/ecommerce-app.git`)

### ✓ Step 4: Add Files to Git

```powershell
# Stage all files (respects .gitignore)
git add .

# Create commit
git commit -m "Initial commit: E-commerce app ready for deployment"
```

### ✓ Step 5: Push to GitHub

```powershell
# Add remote (replace with your copied URL)
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-app.git

# Rename branch to main
git branch -M main

# Upload code
git push -u origin main
```

### ✓ Step 6: Verify on GitHub

Visit `https://github.com/YOUR_USERNAME/ecommerce-app`

✅ You should see all your files there!

---

## PHASE 2: PythonAnywhere Setup (Online)

### ✓ Step 1: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Sign up (free or paid)
3. Verify email
4. Log in

### ✓ Step 2: Clone Your Repository

1. Click **"Consoles"** → **"Bash"**
2. Run:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/ecommerce-app.git mysite
cd mysite
ls -la
```

### ✓ Step 3: Setup Python Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### ✓ Step 4: Create .env File

```bash
nano .env
```

Paste this (update with YOUR values):

```env
SECRET_KEY=super-secret-change-this-to-random-string
DEBUG=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret-key
DB_PATH=/home/YOUR_PYTHONANYWHERE_USERNAME/mysite/smartcart.db
PORT=5000
```

Then: `Ctrl+X` → `Y` → `Enter`

### ✓ Step 5: Setup PythonAnywhere Web App

1. Click **"Web"** tab
2. Click **"Add a new web app"**
3. Choose domain (e.g., `yourname.pythonanywhere.com`)
4. **Manual configuration** → **Python 3.11**
5. Click **"Create web app"**

### ✓ Step 6: Configure WSGI File

1. In **"Web"** tab, click the WSGI file path
2. Delete everything and paste:

```python
import sys
import os

project_home = '/home/YOUR_PYTHONANYWHERE_USERNAME/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
exec(open(activate_this).read(), dict(__name__='__main__'))

from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from app import app as application
```

**Replace username in paths!**

### ✓ Step 7: Set Virtual Environment

In **"Web"** tab → **"Virtualenv"** section:

Enter: `/home/YOUR_PYTHONANYWHERE_USERNAME/mysite/venv`

Click checkmark ✓

### ✓ Step 8: Map Static Files

In **"Web"** tab → **"Static files"**:

Click "Add mapping":
- **URL:** `/static`
- **Directory:** `/home/YOUR_PYTHONANYWHERE_USERNAME/mysite/static`

### ✓ Step 9: Create Upload Directories

In **Bash console**, run:

```bash
cd ~/mysite
mkdir -p static/upload/product_images
mkdir -p static/upload/profile_pics
chmod 777 static/upload/product_images
chmod 777 static/upload/profile_pics
```

### ✓ Step 10: Reload & Test

1. In **"Web"** tab, click **"Reload"** (green button)
2. Wait 10-15 seconds
3. Visit your domain: `https://yourname.pythonanywhere.com`
4. **Your app is LIVE!** 🎉

---

## Key Values to Replace

| Placeholder | Where to Find |
|-------------|--------------|
| `YOUR_USERNAME` | Your GitHub username |
| `YOUR_PYTHONANYWHERE_USERNAME` | Your PythonAnywhere username |
| `your-email@gmail.com` | Your Gmail address |
| `your-gmail-app-password` | Generate from Gmail (see guide) |
| `your-razorpay-key-id` | From Razorpay dashboard |
| `your-razorpay-secret-key` | From Razorpay dashboard |

---

## Troubleshooting

### App Shows "Application Error"?

1. Check **Error log** in PythonAnywhere **"Web"** tab
2. Look for:
   - Missing `.env` file
   - Wrong usernames in WSGI
   - Module import errors

### Database Not Working?

```bash
# In Bash console
cd ~/mysite
touch smartcart.db
chmod 644 smartcart.db
```

### Can't Upload Files?

```bash
# Make directories writable
chmod 777 static/upload -R
```

### Need to Update Code?

```bash
# In Bash console
cd ~/mysite
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

Then reload in **"Web"** tab.

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) | Detailed GitHub setup |
| [PYTHONANYWHERE_DEPLOYMENT.md](PYTHONANYWHERE_DEPLOYMENT.md) | Detailed PythonAnywhere guide |
| [config.py](config.py) | Environment variable configuration |
| [requirements.txt](requirements.txt) | Python dependencies |

---

## Post-Deployment Tasks

- [ ] Test login (admin & user)
- [ ] Test product upload
- [ ] Test cart and checkout
- [ ] Test payment (use Razorpay test mode)
- [ ] Check email notifications work
- [ ] Verify upload folders are writable
- [ ] Monitor error logs regularly
- [ ] Keep dependencies updated
- [ ] Set up daily backups

---

## Support Resources

- **PythonAnywhere:** https://help.pythonanywhere.com
- **GitHub:** https://docs.github.com
- **Flask:** https://flask.palletsprojects.com
- **Razorpay:** https://razorpay.com/docs

---

## Status

✅ **Your app is ready to deploy!**

Follow this checklist in order. If stuck on any step, check the detailed guides mentioned above.

**You're doing great! 🚀**
