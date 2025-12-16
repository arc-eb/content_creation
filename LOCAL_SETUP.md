# Local Development Setup

## Setting Environment Variables on Windows

### For PowerShell (Current Session Only)

```powershell
$env:GEMINI_API_KEY='your-api-key-here'
$env:SECRET_KEY='your-secret-key-here'
```

**Note**: This only lasts for the current PowerShell session. When you close the terminal, you'll need to set it again.

### For PowerShell (Permanent - Current User)

To set permanently for your user account:

```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here', 'User')
[System.Environment]::SetEnvironmentVariable('SECRET_KEY', 'your-secret-key-here', 'User')
```

After setting, restart your terminal/PowerShell for it to take effect.

### For Command Prompt (cmd)

```cmd
set GEMINI_API_KEY=your-api-key-here
set SECRET_KEY=your-secret-key-here
```

### Using .env File (Recommended)

Create a `.env` file in your project root:

```env
GEMINI_API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
```

Then install `python-dotenv`:
```bash
pip install python-dotenv
```

And update `app.py` to load it:
```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file
```

**Note**: Make sure `.env` is in your `.gitignore` (it already is!)

---

## Running the App Locally

### Option 1: Using Flask's built-in server

```powershell
# Set environment variables
$env:GEMINI_API_KEY='your-api-key'
$env:SECRET_KEY='your-secret-key'

# Run the app
python app.py
```

### Option 2: Using Gunicorn (Production-like)

```powershell
# Set environment variables
$env:GEMINI_API_KEY='your-api-key'
$env:SECRET_KEY='your-secret-key'

# Install gunicorn if needed
pip install gunicorn

# Run with gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --reload
```

### Access the App

Once running, open: **http://localhost:5000**

---

## Verify Environment Variables

Check if they're set:

```powershell
echo $env:GEMINI_API_KEY
echo $env:SECRET_KEY
```

---

## Troubleshooting

### "GEMINI_API_KEY not set" Error
- Make sure you set the variable in the same terminal session where you run the app
- Verify with: `echo $env:GEMINI_API_KEY`
- If empty, set it again

### Variables Not Persisting
- PowerShell variables only last for the current session
- Use permanent method above or set them each time
- Or use a `.env` file (see above)

### App Still Not Working
- Restart the terminal after setting permanent variables
- Make sure you're in the correct directory
- Check that all dependencies are installed: `pip install -r requirements.txt`

