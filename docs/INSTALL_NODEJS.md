# 📦 Install Node.js and npm

## Problem
You're getting: `zsh: command not found: npm`

This means Node.js is not installed on your system.

---

## ✅ Solution: Install Node.js

### Option 1: Using Homebrew (Recommended for Mac)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js (includes npm)
brew install node

# Verify installation
node --version
npm --version
```

### Option 2: Download from Official Website

1. Go to: https://nodejs.org/
2. Download the **LTS version** (Long Term Support)
3. Run the installer
4. Follow the installation wizard
5. Restart your terminal

### Option 3: Using nvm (Node Version Manager)

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart terminal or run:
source ~/.zshrc

# Install Node.js
nvm install --lts

# Verify
node --version
npm --version
```

---

## 🔄 After Installing Node.js

Once Node.js is installed, run:

```bash
cd /Users/kesojusaipriya/Dormant-ID/frontend
npm install
npm start
```

Browser will open to: **http://localhost:3000**

---

## 🎯 Alternative: Use Backend API Directly

If you don't want to install Node.js right now, you can still use the backend API directly with curl:

### Start a Retrieval
```bash
curl -X POST http://localhost:5001/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2023-01-01", "end_date": "2024-12-31"}'
```

### Check Status
```bash
curl http://localhost:5001/api/status
```

### Monitor Progress (in a loop)
```bash
while true; do
  clear
  echo "=== Data Retrieval Status ==="
  curl -s http://localhost:5001/api/status | python3 -m json.tool
  echo ""
  echo "Press Ctrl+C to stop monitoring"
  sleep 2
done
```

---

## 📊 What Each Option Gives You

| Option | What You Get |
|--------|--------------|
| **Install Node.js** | Full web interface with Carbon Design System |
| **Use curl** | Command-line access to APIs (no UI) |
| **Original scripts** | Standalone data retrieval (no web interface) |

---

## 💡 Recommendation

**Install Node.js** to get the full web interface experience with:
- Beautiful Carbon Design System UI
- Date pickers
- Progress bars
- Real-time status updates
- Professional IBM design

---

## 🚀 Quick Install (Mac with Homebrew)

```bash
# One command to install Node.js
brew install node

# Then start the frontend
cd frontend
npm install
npm start
```

---

## ✅ Verify Installation

After installing, check:

```bash
node --version   # Should show: v18.x.x or higher
npm --version    # Should show: 9.x.x or higher
```

If you see version numbers, you're ready to go!

---

## 🆘 Need Help?

If you have issues installing Node.js:
1. Check: https://nodejs.org/en/download/
2. Or use the backend API directly with curl (see above)
3. Or use the original standalone scripts: `python run.py`