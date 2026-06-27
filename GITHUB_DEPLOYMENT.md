# Deploy to GitHub & PythonAnywhere

## Step 1: Setup GitHub Repository

### Option A: Create New Repository on GitHub (Recommended)

1. **Go to GitHub and create a new repository:**
   - Visit https://github.com/new
   - Repository name: `ecommerce-app` (or your preferred name)
   - Description: `Python Flask E-commerce Application`
   - Choose: **Private** (to keep credentials safe)
   - Do NOT initialize with README (we already have one)
   - Click "Create repository"

2. **Copy the repository URL** (you'll need it next)
   - It should look like: `https://github.com/YOUR_USERNAME/ecommerce-app.git`

---

## Step 2: Push Code to GitHub (from your local machine)

### Open PowerShell and run these commands:

```powershell
# Navigate to your project folder
cd "c:\Users\sowmy\OneDrive\Documents\Desktop\ecommers app - Copy"

# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: E-commerce Flask application"

# Add remote repository (replace with YOUR GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-app.git

# Rename branch to main (GitHub standard)
git branch -M main

# Push code to GitHub
git push -u origin main

# Verify it worked
git status
```

### What this does:
- `git init` - Creates a local git repository
- `git add .` - Stages all files (respects .gitignore)
- `git commit` - Creates a snapshot with a message
- `git remote add origin` - Links to your GitHub repo
- `git push` - Uploads code to GitHub

---

## Step 3: Verify on GitHub

1. Go to your GitHub repository URL
2. Verify all your files are there (except .env, venv/, etc. - protected by .gitignore)
3. Your code is now backed up and ready for deployment!

---

## Step 4: Future GitHub Updates

When you make changes locally:

```powershell
# See what changed
git status

# Add changes
git add .

# Commit with a message
git commit -m "Describe your changes here"

# Push to GitHub
git push
```

---

## Common Git Commands

| Command | What it does |
|---------|-------------|
| `git status` | See current changes |
| `git log` | View commit history |
| `git pull` | Get latest changes from GitHub |
| `git clone <url>` | Download repo to new location |
| `git branch` | List all branches |
| `git checkout -b new-branch` | Create and switch to new branch |

---

## ⚠️ IMPORTANT: Keep .env Secret

**NEVER push .env file to GitHub!**
- Already protected by `.gitignore` ✓
- Use `.env.example` for other developers
- Each deployment has its own `.env` file

---

## Next: Deploy to PythonAnywhere

See **PYTHONANYWHERE_DEPLOYMENT.md** for step-by-step deployment instructions.
