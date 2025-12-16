# How to Push to GitHub

Your push likely needs authentication. Here are the options:

## Option 1: Use GitHub Personal Access Token (Recommended)

1. **Create a Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: `content_creation_push`
   - Expiration: Choose 90 days or custom
   - Select scope: **`repo`** (Full control of private repositories)
   - Click "Generate token"
   - **COPY THE TOKEN** (you won't see it again!)

2. **Push using the token**:
   ```bash
   git push -u origin main
   ```
   
   When prompted:
   - **Username**: `arc-eb`
   - **Password**: Paste your Personal Access Token (NOT your GitHub password)

## Option 2: Use GitHub CLI (Easier)

1. **Install GitHub CLI** (if not installed):
   - Windows: `winget install GitHub.cli` or download from https://cli.github.com
   - Or: `scoop install gh`

2. **Authenticate**:
   ```bash
   gh auth login
   ```
   Follow the prompts to authenticate.

3. **Push**:
   ```bash
   git push -u origin main
   ```

## Option 3: Use SSH (More secure, one-time setup)

1. **Generate SSH key** (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add SSH key to GitHub**:
   - Copy your public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste your public key
   - Save

3. **Change remote to SSH**:
   ```bash
   git remote set-url origin git@github.com:arc-eb/content_creation.git
   ```

4. **Push**:
   ```bash
   git push -u origin main
   ```

## Quick Test

After pushing, verify files are on GitHub:
- Visit: https://github.com/arc-eb/content_creation
- You should see all your files there!

