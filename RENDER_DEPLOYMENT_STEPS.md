# Render.com Deployment - Step by Step

## ✅ Step 1: Push Code to GitHub (Required)

Render needs your code in a Git repository. Follow these steps:

### A. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `bompard-garment-swap` (or any name you prefer)
3. Set to **Public** or **Private** (your choice)
4. **DO NOT** initialize with README, .gitignore, or license
5. Click "Create repository"

### B. Push Your Code

After creating the repo, GitHub will show you commands. Use these:

```bash
# Add your GitHub repo as remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push code
git push -u origin main
```

**Note**: You'll need a GitHub Personal Access Token for authentication:
- Go to: https://github.com/settings/tokens
- Generate new token (classic) with `repo` scope
- Use token as password when pushing

---

## ✅ Step 2: Deploy on Render.com

### A. Create Account

1. Go to https://render.com
2. Sign up (free account works)
3. Connect your GitHub account when prompted

### B. Create Web Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - Select the repository you just created
   - Click "Connect"

### C. Configure Service

Fill in these settings:

- **Name**: `bompard-garment-swap` (or your preferred name)
- **Region**: Choose closest to you (e.g., Frankfurt, Oregon)
- **Branch**: `main` (or `master` if that's your default)
- **Root Directory**: (leave empty)
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt gunicorn
  ```
- **Start Command**: 
  ```
  gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
  ```

### D. Set Environment Variables

Click **"Environment"** tab and add these variables:

1. **GEMINI_API_KEY**
   - Value: Your Gemini API key from https://makersuite.google.com/app/apikey
   - Required: Yes

2. **SECRET_KEY**
   - Value: Generate using: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Required: Yes (for Flask sessions)

3. **PYTHON_VERSION** (Optional but recommended)
   - Value: `3.11.0`
   - Required: No

### E. Deploy!

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies
   - Build your app
   - Deploy it
3. Wait 2-5 minutes for first deployment
4. You'll get a URL like: `https://bompard-garment-swap.onrender.com`

---

## ✅ Step 3: Test Your Deployment

1. Visit your Render URL
2. Upload test images (model + flat-lay)
3. Generate a garment swap
4. Verify everything works!

---

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure Python version is compatible

### App Crashes
- Check logs in Render dashboard
- Verify environment variables are set correctly
- Check that `GEMINI_API_KEY` is valid

### Timeout Errors
- Increase timeout in start command: `--timeout 180`
- Check API response times
- Consider upgrading to paid plan for better performance

### Free Tier Limitations
- App spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Upgrade to paid plan for always-on service

---

## 📝 Quick Reference

**Render Dashboard**: https://dashboard.render.com

**Your App URL**: Will be shown after deployment (format: `https://your-app-name.onrender.com`)

**Update Code**: Just push to GitHub, Render auto-deploys!

**View Logs**: Click on your service → "Logs" tab

---

## 🎉 Success!

Once deployed, your app will be live and accessible from anywhere!

