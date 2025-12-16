# Deployment Guide

This guide covers deploying the Bompard Garment Swap application to various platforms.

## Prerequisites

1. **Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Python 3.11+**: Required for the application
3. **Git**: For version control and deployment

## Environment Variables

Create a `.env` file (or set in your deployment platform) with:

```bash
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_random_secret_key_here
```

**Generate SECRET_KEY**: Run this command:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Deployment Options

### Option 1: Render.com (Recommended - Free tier available)

1. **Create account** at [render.com](https://render.com)

2. **Connect repository**:
   - Go to Dashboard → New → Web Service
   - Connect your Git repository

3. **Configure service**:
   - **Name**: `bompard-garment-swap`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: (leave empty)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt gunicorn`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

4. **Set environment variables**:
   - Go to Environment tab
   - Add:
     - `GEMINI_API_KEY`: Your API key
     - `SECRET_KEY`: Generate random string
     - `PYTHON_VERSION`: `3.11.0`

5. **Deploy**: Click "Create Web Service"

**Note**: Free tier has limitations (spins down after inactivity). For production, use paid tier.

---

### Option 2: Railway.app

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Initialize project**:
   ```bash
   railway init
   ```

4. **Set environment variables**:
   ```bash
   railway variables set GEMINI_API_KEY=your_api_key
   railway variables set SECRET_KEY=your_secret_key
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

---

### Option 3: Heroku

1. **Install Heroku CLI**: [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create app**:
   ```bash
   heroku create bompard-garment-swap
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key
   heroku config:set SECRET_KEY=your_secret_key
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

6. **Open app**:
   ```bash
   heroku open
   ```

---

### Option 4: Docker Deployment

1. **Build image**:
   ```bash
   docker build -t bompard-garment-swap .
   ```

2. **Run container**:
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e GEMINI_API_KEY=your_api_key \
     -e SECRET_KEY=your_secret_key \
     -v $(pwd)/uploads:/app/uploads \
     -v $(pwd)/output_web:/app/output_web \
     --name bompard-app \
     bompard-garment-swap
   ```

3. **Access**: http://localhost:5000

**For production Docker deployment** (e.g., AWS ECS, Google Cloud Run):
- Push to container registry (Docker Hub, AWS ECR, GCR)
- Deploy to your container service
- Set environment variables in your container service

---

### Option 5: VPS/Cloud Server (DigitalOcean, AWS EC2, etc.)

1. **SSH into server**

2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip nginx
   ```

3. **Clone repository**:
   ```bash
   git clone <your-repo-url>
   cd content_creation
   ```

4. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt gunicorn
   ```

5. **Create systemd service** (`/etc/systemd/system/bompard.service`):
   ```ini
   [Unit]
   Description=Bompard Garment Swap
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/content_creation
   Environment="GEMINI_API_KEY=your_api_key"
   Environment="SECRET_KEY=your_secret_key"
   ExecStart=/usr/local/bin/gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 120

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start service**:
   ```bash
   sudo systemctl start bompard
   sudo systemctl enable bompard
   ```

7. **Configure Nginx** (reverse proxy):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

8. **Reload Nginx**:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

## Local Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   # Linux/Mac
   export GEMINI_API_KEY=your_api_key
   export SECRET_KEY=your_secret_key

   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your_api_key"
   $env:SECRET_KEY="your_secret_key"
   ```

3. **Run application**:
   ```bash
   python app.py
   ```

   Or with gunicorn:
   ```bash
   gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --reload
   ```

4. **Access**: http://localhost:5000

---

## Security Checklist

- [ ] Remove hardcoded API keys
- [ ] Set strong SECRET_KEY
- [ ] Use HTTPS (most platforms provide this)
- [ ] Set up rate limiting (for production)
- [ ] Configure CORS if needed
- [ ] Set up file size limits
- [ ] Regular backups of important data

---

## Troubleshooting

### "GEMINI_API_KEY not set"
- Verify environment variable is set correctly
- Check if variable name is correct
- Restart application after setting variables

### "Port already in use"
- Change PORT environment variable
- Or stop the process using the port

### "Timeout errors"
- Increase timeout in gunicorn command
- Check API response times
- Reduce image sizes

### "Memory issues"
- Reduce number of workers
- Use smaller image sizes
- Consider upgrading server resources

---

## Post-Deployment

1. **Test the application**:
   - Upload test images
   - Verify generation works
   - Check error handling

2. **Monitor logs**:
   - Check application logs regularly
   - Monitor API usage
   - Watch for errors

3. **Set up domain** (optional):
   - Point your domain to the deployment
   - Configure SSL certificate (most platforms auto-provide)

---

## Support

For issues or questions, check:
- Application logs
- Platform-specific documentation
- Gemini API status

