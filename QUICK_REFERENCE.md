# 📌 QUICK REFERENCE CARD

Print this or keep it handy while deploying!

---

## 🎯 DEPLOYMENT PATH DECISION TREE

```
START HERE
    ↓
Are you ready    NO → Read QUICK_START.md (5 min)
to deploy now?       ↓
    ↓          YES   Do it again ↻
   YES
    ↓
Do you want     NO → Read DEPLOYMENT_STEPS.md
detailed info?       (20 min)
    ↓          YES   ↓
              Then use CHECKLIST_NOW.md
    ↓
Use CHECKLIST_NOW.md
    ↓
Follow each step
    ↓
🎉 APP LIVE!
```

---

## 📋 FILES YOU NEED

### During Setup
- .env.example → copy to .env
- requirements.txt → for dependencies
- config.py → for configuration

### During Deployment
- app.py → your application
- Procfile → cloud config
- static/ → CSS and uploads
- templates/ → HTML files

### Keep In Pocket
- CHECKLIST_NOW.md → follow this
- EXACT_COMMANDS.md → copy commands
- DEPLOYMENT_GUIDE.md → if errors

---

## ⏱️ TIMELINE AT A GLANCE

```
0:00 - 0:05    Read guide
0:05 - 0:10    Get credentials
0:10 - 0:15    Create .env
0:15 - 0:20    Test locally
0:20 - 0:30    Setup GitHub
0:30 - 0:45    Deploy PythonAnywhere
0:45 - 0:50    Test live
────────────────
0:50 TOTAL     🎉 LIVE!
```

---

## 🔑 CREDENTIALS YOU NEED

### Gmail App Password
- Go: https://myaccount.google.com/apppasswords
- Get: 16-character password
- Use: In MAIL_PASSWORD

### Razorpay Keys
- Go: https://dashboard.razorpay.com/
- Get: Key ID + Secret
- Use: In .env file

### GitHub
- Go: https://github.com/new
- Create: public repository
- Use: For git push

### PythonAnywhere
- Go: https://www.pythonanywhere.com/
- Create: free account
- Use: For deployment

---

## 💾 CRITICAL .env VALUES

```
SECRET_KEY=                    (generate: python -c "import secrets; print(secrets.token_hex(32))")
MAIL_USERNAME=                 (your gmail)
MAIL_PASSWORD=                 (16-char app password)
RAZORPAY_KEY_ID=               (from dashboard)
RAZORPAY_KEY_SECRET=           (from dashboard)
DEBUG=False                    (IMPORTANT!)
```

**NEVER commit .env to GitHub! ⚠️**

---

## 🔑 CRITICAL COMMANDS

### Local Test
```bash
pip install -r requirements.txt
python app.py
# Visit: http://localhost:5000
```

### GitHub Push
```bash
git add .
git commit -m "message"
git push origin main
```

### PythonAnywhere (Bash Console)
```bash
git clone YOUR_REPO_URL
cd ecommerce-app
mkvirtualenv --python=/usr/bin/python3.11 ecommerce
pip install -r requirements.txt
nano .env
# (paste your values, Ctrl+X, Y, Enter)
```

---

## ⚠️ COMMON MISTAKES

```
❌ Use regular Gmail password
✅ Use 16-char App Password from myaccount.google.com/apppasswords

❌ Commit .env to GitHub
✅ .gitignore protects it automatically

❌ Leave DEBUG=True
✅ Set DEBUG=False for production

❌ Skip local testing
✅ Test with python app.py first

❌ Forget to click Reload
✅ Always click green Reload button

❌ Use Razorpay live keys immediately
✅ Use TEST keys first, switch to LIVE later
```

---

## 🚨 IF YOU GET STUCK

| Error | Check |
|-------|-------|
| ModuleNotFoundError | Run: pip install -r requirements.txt |
| .env not found | Create .env (nano .env) |
| WSGI error | Check WSGI file path |
| Email not sending | Verify MAIL_PASSWORD is 16 chars |
| App not loading | Check PythonAnywhere Error log |

---

## ✅ DEPLOYMENT CHECKLIST

```
BEFORE LOCAL TEST:
☐ .env file created
☐ All values filled
☐ DEBUG=False

BEFORE GITHUB PUSH:
☐ App works locally
☐ .env NOT in git (check .gitignore)
☐ All files ready

BEFORE PYTHONANYWHERE DEPLOY:
☐ GitHub repo public
☐ Repository accessible
☐ PythonAnywhere account created

BEFORE CLICKING RELOAD:
☐ Virtual environment created
☐ Dependencies installed
☐ .env file on server
☐ WSGI file configured
☐ Environment variables set
☐ Source code path set

AFTER RELOAD:
☐ Wait 10 seconds
☐ Visit your URL
☐ Check Error log for issues
☐ Test your app

FINAL:
☐ User registration works
☐ Admin login works
☐ Email sending works
☐ Payments work (test mode)
☐ CSS loads correctly
```

---

## 🌐 YOUR LIVE URLS

```
PythonAnywhere:  https://USERNAME.pythonanywhere.com
Heroku:          https://app-name.herokuapp.com
Railway.app:     https://app-name-random.railway.app
Custom domain:   https://yourdomain.com
```

---

## 📞 HELP URLS

```
Gmail App Password:    https://myaccount.google.com/apppasswords
Razorpay Dashboard:    https://dashboard.razorpay.com/
GitHub New Repo:       https://github.com/new
PythonAnywhere:        https://www.pythonanywhere.com/
Heroku:                https://www.heroku.com/
Railway.app:           https://railway.app/
```

---

## 🎯 NEXT ACTIONS

```
1. Open: START_HERE.md
2. Choose: Your guide
3. Gather: Credentials
4. Follow: Step-by-step
5. Deploy: 45 minutes
6. Live: Your app online! 🎉
```

---

## 💡 REMEMBER

✅ Your code is production-ready  
✅ All documentation is complete  
✅ You have multiple platforms  
✅ Security is configured  
✅ Takes 45 minutes  
✅ You CAN do this!  

---

**Status:** ✅ Ready to Deploy  
**Time:** 45 minutes ⏱️  
**Next:** Read START_HERE.md  

🚀 **Let's deploy!**
