#!/bin/bash

# Git Security Verification Script
# Run this before pushing to Git to ensure no credentials are exposed

echo "=========================================="
echo "  Git Security Verification"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check 1: .gitignore exists
echo "1. Checking .gitignore exists..."
if [ -f .gitignore ]; then
    echo -e "${GREEN}✓ .gitignore found${NC}"
else
    echo -e "${RED}✗ .gitignore NOT found!${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 2: .env is in .gitignore
echo "2. Checking .env is in .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo -e "${GREEN}✓ .env is in .gitignore${NC}"
else
    echo -e "${RED}✗ .env is NOT in .gitignore!${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: .env is not tracked by git
echo "3. Checking .env is not tracked by git..."
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo -e "${RED}✗ .env IS tracked by git! Run: git rm --cached .env${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ .env is not tracked${NC}"
fi
echo ""

# Check 4: .env.example exists
echo "4. Checking .env.example exists..."
if [ -f .env.example ]; then
    echo -e "${GREEN}✓ .env.example found${NC}"
else
    echo -e "${YELLOW}⚠ .env.example NOT found (recommended)${NC}"
fi
echo ""

# Check 5: Search for potential API keys in tracked files
echo "5. Searching for potential API keys in tracked files..."
FOUND_KEYS=0

# Check for apikey pattern
if git grep -i "apikey-" -- '*.py' '*.js' '*.jsx' 2>/dev/null | grep -v ".env"; then
    echo -e "${RED}✗ Found potential API keys in tracked files!${NC}"
    FOUND_KEYS=1
fi

# Check for cloudant URLs
if git grep -i "cloudant.com" -- '*.py' '*.js' '*.jsx' 2>/dev/null | grep -v ".env"; then
    echo -e "${RED}✗ Found Cloudant URLs in tracked files!${NC}"
    FOUND_KEYS=1
fi

if [ $FOUND_KEYS -eq 0 ]; then
    echo -e "${GREEN}✓ No API keys found in tracked files${NC}"
else
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 6: output directory is ignored
echo "6. Checking output/ is in .gitignore..."
if grep -q "^output/" .gitignore; then
    echo -e "${GREEN}✓ output/ is in .gitignore${NC}"
else
    echo -e "${YELLOW}⚠ output/ is NOT in .gitignore (recommended)${NC}"
fi
echo ""

# Check 7: log files are ignored
echo "7. Checking log files are in .gitignore..."
if grep -q "^\*\.log$" .gitignore; then
    echo -e "${GREEN}✓ *.log is in .gitignore${NC}"
else
    echo -e "${YELLOW}⚠ *.log is NOT in .gitignore (recommended)${NC}"
fi
echo ""

# Final summary
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All security checks passed!${NC}"
    echo -e "${GREEN}✓ Safe to push to Git${NC}"
    echo "=========================================="
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS security issue(s)${NC}"
    echo -e "${RED}✗ DO NOT push to Git yet!${NC}"
    echo "=========================================="
    echo ""
    echo "Fix the issues above before pushing."
    exit 1
fi

# Made with Bob
