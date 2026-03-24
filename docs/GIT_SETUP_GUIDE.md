# Git Setup Guide

## 🔒 Security First - Protecting API Credentials

This guide helps you safely push your project to Git without exposing sensitive API credentials.

---

## ✅ What's Already Protected

### 1. `.gitignore` Created
The following files/folders are excluded from Git:
- ✅ `.env` - Contains API credentials
- ✅ `frontend/.env` - Contains frontend config
- ✅ `output/` - Contains retrieved user data
- ✅ `*.log` - Log files
- ✅ `retrieval_checkpoint.json` - May contain sensitive data
- ✅ `retrieval_history.json` - May contain sensitive data
- ✅ `node_modules/` - Dependencies
- ✅ `__pycache__/` - Python cache

### 2. `.env.example` Files Created
Template files for other developers:
- ✅ `.env.example` - Backend API credentials template
- ✅ `frontend/.env.example` - Frontend config template

### 3. No Hardcoded Credentials
- ✅ All Python files checked - no hardcoded API keys
- ✅ Credentials only in `.env` files (which are gitignored)

---

## 🚀 How to Push to Git

### Step 1: Initialize Git Repository

```bash
# Initialize git (if not already done)
git init

# Check what will be committed
git status
```

### Step 2: Verify `.env` is Ignored

```bash
# This should show .env is ignored
git status

# If .env appears in the list, something is wrong!
# Make sure .gitignore exists and contains .env
```

### Step 3: Add Files to Git

```bash
# Add all files (except those in .gitignore)
git add .

# Verify .env is NOT in the staged files
git status
```

### Step 4: Commit Changes

```bash
git commit -m "Initial commit: Data retrieval system with history feature"
```

### Step 5: Add Remote Repository

```bash
# Add your GitHub/GitLab repository
git remote add origin https://github.com/yourusername/your-repo.git

# Or use SSH
git remote add origin git@github.com:yourusername/your-repo.git
```

### Step 6: Push to Remote

```bash
# Push to main branch
git push -u origin main

# Or if using master branch
git push -u origin master
```

---

## 📋 Setup Instructions for Other Developers

When someone clones your repository, they need to:

### 1. Copy Environment Files

```bash
# Backend credentials
cp .env.example .env

# Frontend config
cp frontend/.env.example frontend/.env
```

### 2. Fill in Credentials

Edit `.env` with actual Cloudant credentials:
```bash
API_BASE_URL=https://your-cloudant-instance.cloudant.com/...
API_KEY=your-actual-api-key
API_PASSWORD=your-actual-password
```

Edit `frontend/.env` if needed:
```bash
REACT_APP_API_URL=http://localhost:5001
```

### 3. Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 4. Run the System

```bash
# Use the restart script
./restart_servers.sh

# Or manually
cd backend && python app.py
cd frontend && npm start
```

---

## ⚠️ Important Security Notes

### Never Commit These Files:
- ❌ `.env` - Contains real API credentials
- ❌ `frontend/.env` - May contain sensitive config
- ❌ `output/*.jsonl` - Contains user data
- ❌ `*.log` - May contain sensitive information
- ❌ `retrieval_checkpoint.json` - May contain data
- ❌ `retrieval_history.json` - May contain data

### Always Commit These Files:
- ✅ `.env.example` - Template for credentials
- ✅ `frontend/.env.example` - Template for config
- ✅ `.gitignore` - Protects sensitive files
- ✅ All source code files (`.py`, `.js`, `.jsx`)
- ✅ Documentation files (`.md`)
- ✅ Configuration files (`package.json`, `requirements.txt`)

---

## 🔍 Verify Before Pushing

### Check for Exposed Credentials

```bash
# Search for potential API keys in staged files
git grep -i "apikey" $(git diff --cached --name-only)
git grep -i "password" $(git diff --cached --name-only)
git grep -i "cloudant" $(git diff --cached --name-only)

# If any results appear, DO NOT PUSH!
```

### Check .gitignore is Working

```bash
# .env should NOT appear here
git status

# If it does, add it to .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore"
```

---

## 🛠️ If You Accidentally Committed Credentials

### Remove from Git History

```bash
# Remove .env from git tracking
git rm --cached .env
git rm --cached frontend/.env

# Commit the removal
git commit -m "Remove .env files from tracking"

# Push the changes
git push origin main
```

### Rotate Credentials
If credentials were pushed to a public repository:
1. **Immediately** change your API keys in Cloudant
2. Update your local `.env` with new credentials
3. Never reuse the exposed credentials

---

## 📚 Additional Resources

### Git Best Practices
- Always review `git status` before committing
- Use `git diff` to see what changed
- Write clear commit messages
- Never force push to shared branches

### Security Best Practices
- Keep `.env` files local only
- Use different credentials for dev/prod
- Rotate API keys regularly
- Use environment-specific configs

---

## ✅ Checklist Before First Push

- [ ] `.gitignore` file exists and includes `.env`
- [ ] `.env.example` files created
- [ ] No hardcoded credentials in source code
- [ ] Ran `git status` - `.env` is NOT listed
- [ ] Tested `.env.example` works for setup
- [ ] Documentation updated with setup instructions
- [ ] Verified no sensitive data in commit

---

**Ready to push!** Your API credentials are safe and won't be exposed in Git.

For questions or issues, refer to the main README.md or project documentation.