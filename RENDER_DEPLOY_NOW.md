# Deploy to Render.com - Step by Step Guide

## ✅ Step 1: Create Render Account

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with your GitHub account (recommended - makes connecting repos easier)
4. Authorize Render to access your GitHub repositories

## ✅ Step 2: Create New Web Service

1. Once logged in, you'll see the Render Dashboard
2. Click the **"New +"** button (top right corner)
3. Select **"Web Service"**

## ✅ Step 3: Connect Your Repository

1. In the "Connect a repository" section:
   - Select **GitHub** as your Git provider
   - Search for or select: **`arc-eb/content_creation`**
   - Click **"Connect"**

## ✅ Step 4: Configure Your Service

Fill in these settings:

### Basic Settings:
- **Name**: `bompard-garment-swap` (or any name you prefer)
- **Region**: Choose closest to you (e.g., Frankfurt, Oregon, Singapore)
- **Branch**: `main`
- **Root Directory**: (leave empty)

### Build & Deploy:
- **Environment**: Select **"Python 3"**
- **Build Command**: 
  ```
  pip install -r requirements.txt gunicorn
  ```
- **Start Command**: 
  ```
  gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
  ```

### Instance Type:
- For free tier: Leave default (Free)
- For production: Select "Starter" ($7/month) for always-on service

## ✅ Step 5: Set Environment Variables

Click the **"Advanced"** button, then click **"Add Environment Variable"**:

### Required Variables:

1. **GEMINI_API_KEY**
   - Key: `GEMINI_API_KEY`
   - Value: Your API key from https://makersuite.google.com/app/apikey
   - Click **"Save"**

2. **SECRET_KEY**
   - Key: `SECRET_KEY`
   - Value: Generate one using: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Or use any random 64-character string
   - Click **"Save"**

3. **PYTHON_VERSION** (Optional but recommended)
   - Key: `PYTHON_VERSION`
   - Value: `3.11.0`
   - Click **"Save"**

## ✅ Step 6: Deploy!

1. Scroll down and click **"Create Web Service"**
2. Render will now:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Build your application
   - Deploy it
3. **Wait 2-5 minutes** for the first deployment
4. You'll see build logs in real-time

## ✅ Step 7: Access Your App

Once deployment completes:
- You'll see a URL like: `https://bompard-garment-swap.onrender.com`
- Click on it or copy the URL
- Your app is live! 🎉

## 🔍 Verify Deployment

1. Visit your Render URL
2. You should see the Bompard Garment Swap interface
3. Upload test images (model + flat-lay)
4. Generate a garment swap to test

## 📊 Monitor Your App

- **Dashboard**: View your service status
- **Logs**: Click on your service → "Logs" tab to see application logs
- **Metrics**: Monitor CPU, memory, and request metrics
- **Events**: See deployment history and events

## 🔄 Update Your App

To update your deployed app:
1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```
3. Render will automatically detect the push and redeploy!

## ⚠️ Free Tier Notes

- App spins down after **15 minutes** of inactivity
- First request after spin-down takes ~30 seconds (cold start)
- For production use, upgrade to **Starter plan ($7/month)** for:
  - Always-on service (no spin-down)
  - Better performance
  - Faster cold starts

## 🆘 Troubleshooting

### Build Fails
- Check the "Logs" tab for error messages
- Verify `requirements.txt` has all dependencies
- Ensure Python version is compatible

### App Doesn't Start
- Check logs for startup errors
- Verify environment variables are set correctly
- Ensure `GEMINI_API_KEY` is valid

### 500 Errors
- Check application logs
- Verify API key is working
- Check for any missing dependencies

## 🎉 Success!

Your Bompard Garment Swap app is now live on Render.com!

**Your app URL**: Will be shown after deployment

Need help? Check the Render dashboard logs or see `DEPLOYMENT.md` for more details.

