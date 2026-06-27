# Deploy to PythonAnywhere (Complete Guide)

## Why PythonAnywhere?

✓ **Easiest** - No Docker, no complex setup  
✓ **Affordable** - Free tier available ($5-50/month paid)  
✓ **Python-Friendly** - Built for Python apps  
✓ **Git Integration** - Direct GitHub cloning  
✓ **File Manager** - Easy file uploads  
✓ **SSL Included** - HTTPS by default  

---

## Step 1: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Click "Sign up" → Choose **free** or **paid** tier
   - **Free**: Limited but works for testing
   - **Paid**: $5+/month for production
3. Verify your email
4. Log in to your PythonAnywhere dashboard

---

## Step 2: Clone Your GitHub Repository

### In PythonAnywhere Dashboard:

1. Click **"Consoles"** tab
2. Click **"Bash"** to open a terminal
3. Run these commands:

```bash
# Go to home directory
cd ~

# Clone your GitHub repository
git clone https://github.com/YOUR_USERNAME/ecommerce-app.git mysite

# Navigate into project folder
cd mysite

# Check if all files are there
ls -la
```

**Replace** `YOUR_USERNAME` with your actual GitHub username.

---

## Step 3: Create Python Virtual Environment

In the same Bash console:

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

This creates an isolated Python environment for your app.

---

## Step 4: Create .env File on PythonAnywhere

In the same Bash console:

```bash
# Create .env file
nano .env
```

This opens a text editor. Copy and paste:

```env
SECRET_KEY=your-secret-key-change-this
DEBUG=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
DB_PATH=/home/YOUR_USERNAME/mysite/smartcart.db
PORT=5000
```

**Then:**
1. Press `Ctrl + X`
2. Press `Y` (yes)
3. Press `Enter` (confirm filename)

---

## Step 5: Configure Web App

1. Go to **"Web"** tab in PythonAnywhere
2. Click **"Add a new web app"**
3. Choose:
   - Domain: `yourname.pythonanywhere.com`
   - Framework: **Manual configuration** → **Python 3.11**
4. Click "Create web app"

---

## Step 6: Configure WSGI File

PythonAnywhere created a WSGI file for you. Edit it:

1. In the **"Web"** tab, find **WSGI configuration file**
2. Click the path (should look like `/var/www/yourname_pythonanywhere_com_wsgi.py`)
3. Delete the entire content and replace with:

```python
# WSGI configuration for Flask app
import sys
import os

# Add your project directory to the Python path
project_home = '/home/YOUR_USERNAME/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Use the virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
exec(open(activate_this).read(), dict(__name__='__main__'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import and run Flask app
from app import app as application
```

**Replace** `YOUR_USERNAME` with your PythonAnywhere username.

---

## Step 7: Configure Virtualenv in Web Tab

Still in the **"Web"** tab:

1. Scroll down to **"Virtualenv"**
2. Enter the path: `/home/YOUR_USERNAME/mysite/venv`
3. Click the checkmark to confirm

---

## Step 8: Configure Static Files

In the **"Web"** tab, find **"Static files"** section:

Click "Add a new static files mapping":

| URL | Directory |
|-----|-----------|
| `/static` | `/home/YOUR_USERNAME/mysite/static` |

This serves your CSS, JS, and uploaded images.

---

## Step 9: Reload Web App

1. At the top of the **"Web"** tab, click **"Reload"** (green button)
2. Wait 10-15 seconds
3. Go to your domain: `https://yourname.pythonanywhere.com`
4. Your app should be live! 🎉

---

## Step 10: Troubleshooting

### "ModuleNotFoundError" or App Crashes?

Check error logs:
1. **"Web"** tab → Scroll down → **"Error log"**
2. Click the path to see error messages
3. Common issues:
   - Missing `.env` file → Create it again
   - Wrong paths in WSGI → Check `/home/USERNAME/` is correct
   - Virtual environment not activated → Check Virtualenv setting

### Database Not Found?

The database path in `.env` must exist or be writable:

```bash
# In Bash console
cd ~/mysite
touch smartcart.db
chmod 644 smartcart.db
```

### File Uploads Not Working?

Ensure upload folders exist and are writable:

```bash
# In Bash console
mkdir -p static/upload/product_images
mkdir -p static/upload/profile_pics
chmod 777 static/upload
chmod 777 static/upload/product_images
chmod 777 static/upload/profile_pics
```

### Want to See Console Output?

In Bash console, run:

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask directly (for testing)
python app.py

# Or with Gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

---

## Step 11: Set Up Email (Gmail)

For password reset emails to work:

1. Go to https://accounts.google.com/account/security
2. Enable 2-factor authentication
3. Generate **App Password** (not your Gmail password):
   - Search "App passwords"
   - Generate one for "Mail"
   - Copy the 16-character password
4. Put this in `.env`:

```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

---

## Step 12: HTTPS & Custom Domain (Optional)

### Use Free HTTPS
Already enabled by default on `yourname.pythonanywhere.com` ✓

### Add Custom Domain ($5-15/year)
1. Buy domain from GoDaddy, Namecheap, etc.
2. PythonAnywhere **"Web"** tab → Add your domain
3. Update DNS records to point to PythonAnywhere
4. PythonAnywhere auto-generates SSL certificate

---

## Step 13: Scheduled Tasks (Optional)

To run maintenance tasks on a schedule:

1. **"Tasks"** tab in PythonAnywhere
2. Click "Create a new scheduled task"
3. Set time and command:

```bash
/home/YOUR_USERNAME/mysite/venv/bin/python /home/YOUR_USERNAME/mysite/cleanup.py
```

---

## Production Checklist

Before going live, verify:

- [ ] `.env` has real Razorpay keys
- [ ] `.env` has real Gmail credentials
- [ ] `DEBUG=False` in `.env`
- [ ] Database (`smartcart.db`) exists and is writable
- [ ] Upload folders exist (`static/upload/*`)
- [ ] Web app is reloaded after changes
- [ ] WSGI file is correct with your username
- [ ] Virtual environment path is set correctly
- [ ] All static files are accessible (`/static` path)
- [ ] Email sending works (test forgot password)
- [ ] Payment gateway working (test with Razorpay test mode)

---

## Making Updates

After pushing code to GitHub:

```bash
# In PythonAnywhere Bash console
cd ~/mysite

# Pull latest code
git pull origin main

# If dependencies changed
source venv/bin/activate
pip install -r requirements.txt

# Reload web app
```

Then go to **"Web"** tab and click **"Reload"**.

---

## Free vs Paid

| Feature | Free | Paid |
|---------|------|------|
| Apps | 1 | Unlimited |
| Always-on | No (idle = sleep) | Yes ✓ |
| CPU | Shared | Dedicated |
| Web access | ✓ | ✓ |
| Scheduled tasks | ❌ | ✓ |
| Database size | 100MB | Larger |
| Cost | FREE | $5-50/month |

---

## Support & Help

- **PythonAnywhere Help**: https://help.pythonanywhere.com
- **Flask Docs**: https://flask.palletsprojects.com
- **Common Issues**: Check `Error log` in Web tab

---

## Next Steps

1. ✓ Push to GitHub (see GITHUB_DEPLOYMENT.md)
2. ✓ Deploy to PythonAnywhere (this guide)
3. Test all features (login, products, payment, orders)
4. Monitor error logs and performance
5. Keep code updated via `git pull`

**Your app is now live! 🚀**
