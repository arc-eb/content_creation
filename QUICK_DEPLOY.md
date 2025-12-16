# Quick Deployment Guide

## 🚀 Fastest Option: Render.com (Recommended)

### Step 1: Prepare Your Code
1. Make sure you have all files committed to Git (we'll set this up)

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up (free account available)

### Step 3: Deploy
1. Click "New +" → "Web Service"
2. Connect your GitHub/GitLab repository (or deploy from a public repo)
3. Configure:
   - **Name**: `bompard-garment-swap`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt gunicorn`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### Step 4: Set Environment Variables
Click "Environment" tab and add:
- `GEMINI_API_KEY` = `your_api_key_here`
- `SECRET_KEY` = `(generate below)`
- `PYTHON_VERSION` = `3.11.0`

### Step 5: Deploy!
Click "Create Web Service" - Render will build and deploy automatically!

---

## 📦 Option 2: Docker (Run Anywhere)

### Build and Run:
```bash
# Build image
docker build -t bompard-app .

# Run container
docker run -d \
  -p 5000:5000 \
  -e GEMINI_API_KEY=your_api_key \
  -e SECRET_KEY=your_secret_key \
  --name bompard-app \
  bompard-app
```

**Access**: http://localhost:5000

---

## 🔑 Generate SECRET_KEY

Run this command to generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and use it as your `SECRET_KEY` environment variable.

---

## ✅ Pre-Deployment Checklist

- [ ] Get your Gemini API Key from https://makersuite.google.com/app/apikey
- [ ] Generate SECRET_KEY using command above
- [ ] Choose deployment platform
- [ ] Set environment variables
- [ ] Deploy!
- [ ] Test the deployed app

---

## 🆘 Need Help?

See `DEPLOYMENT.md` for detailed instructions for all platforms.

