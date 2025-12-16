# PowerShell script to start Flask
# Usage: .\START_FLASK.ps1
#
# Note: The app will automatically load GEMINI_API_KEY from .env file
# Make sure you have created a .env file with: GEMINI_API_KEY=your-key-here

Write-Host "🚀 Starting Flask app..."
Write-Host "📝 Access at: http://localhost:5000"
Write-Host ""
Write-Host "Note: API key is loaded from .env file (if present)"
Write-Host ""

# Start Flask
python app.py

