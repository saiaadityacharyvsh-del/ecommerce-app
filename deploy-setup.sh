#!/bin/bash

# Quick Deployment Setup Script for Linux/Mac

echo ""
echo "==================================================="
echo "MyShop E-Commerce App - Deployment Setup"
echo "==================================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "ERROR: Git is not installed. Please install from https://git-scm.com"
    exit 1
fi

# Initialize git repo
echo "[1/5] Initializing Git repository..."
git init
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
echo "[1/5] DONE"

# Create .env file
echo "[2/5] Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[2/5] .env created. Please edit with your credentials!"
else
    echo "[2/5] .env already exists"
fi

# Add and commit
echo "[3/5] Adding files to Git..."
git add .
git commit -m "Initial commit - production ready"
echo "[3/5] DONE"

# Install dependencies
echo "[4/5] Installing Python dependencies..."
pip install -r requirements.txt
echo "[4/5] DONE"

# Initialize database
echo "[5/5] Initializing database..."
python -c "from app import initialize_database; initialize_database()"
echo "[5/5] DONE"

echo ""
echo "==================================================="
echo "Setup Complete!"
echo "==================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Create GitHub repository at https://github.com/new"
echo "3. Run: git remote add origin https://github.com/YOUR_USERNAME/ecommerce-app.git"
echo "4. Run: git branch -M main"
echo "5. Run: git push -u origin main"
echo "6. Follow the DEPLOYMENT_GUIDE.md for cloud deployment"
echo ""
echo "To test locally:"
echo "  python app.py"
echo "  Visit http://localhost:5000"
echo ""
