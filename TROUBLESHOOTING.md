# Troubleshooting Guide

## "Failed to fetch" Error

This error means the browser cannot connect to the Flask server. Here's how to fix it:

### 1. Check if Server is Running

Make sure you started the Flask server:
```bash
python app.py
```

You should see:
```
============================================================
Bompard Garment Swap Web Interface
============================================================

Starting server...
Open your browser and go to: http://127.0.0.1:5000
```

### 2. Check the Browser Console

Open browser developer tools (F12) and check the Console tab for detailed error messages.

### 3. Verify the URL

Make sure you're accessing:
```
http://127.0.0.1:5000
```

NOT:
- `http://localhost:5000` (might have issues on some systems)
- `https://...` (should be http, not https)

### 4. Check for Port Conflicts

If port 5000 is already in use, you'll see:
```
❌ ERROR: Port 5000 is already in use!
```

**Solution:** Change the port in `app.py`:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Change to 5001
```

Then access: `http://127.0.0.1:5001`

### 5. Check Firewall/Antivirus

Some firewalls or antivirus software may block local connections. Try:
- Temporarily disabling firewall/antivirus
- Adding Python to firewall exceptions

### 6. Check Terminal for Errors

Look at the terminal where you ran `python app.py` for any error messages. Common issues:

**Import Error:**
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Install Flask
```bash
pip install Flask
```

**API Key Error:**
```
ValueError: GEMINI_API_KEY environment variable not set
```
**Solution:** Set your API key
```bash
export GEMINI_API_KEY='your-api-key-here'
```

### 7. Test Server Connection

Open a new terminal and test:
```bash
curl http://127.0.0.1:5000/health
```

Or visit in browser: `http://127.0.0.1:5000/health`

You should see: `{"status":"ok","message":"Server is running"}`

## Other Common Errors

### "AttributeError: 'NoneType' object has no attribute 'parts'"

This means the API response was unexpected. The code has been updated to handle this better. If it still occurs:
- Check the terminal for detailed error messages
- Verify your API key is correct
- Check if the Gemini API is accessible

### "File upload fails"

- Check file size (max 16MB)
- Ensure files are images (PNG, JPG, JPEG, WEBP)
- Check browser console for errors

### "Generation takes too long"

- Normal: 30-60 seconds per generation
- If it takes longer, check terminal for API errors
- The API may be rate-limited

## Getting Help

1. Check the terminal where Flask is running for error messages
2. Check browser console (F12 → Console tab)
3. Check browser Network tab (F12 → Network) to see the request/response
4. Verify all dependencies are installed: `pip install -r requirements.txt`

