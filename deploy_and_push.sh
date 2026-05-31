#!/bin/bash
# Deploy script for pushing bot updates to GitHub

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

echo "=================================================="
echo "🚀 DLBot Deployment Script"
echo "=================================================="
echo ""

# 1. Check if we're in correct directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: main.py not found in current directory${NC}"
    echo "   Please run this script from project root directory"
    exit 1
fi

# 2. Check git status
echo -e "${YELLOW}📊 Git Status:${NC}"
git status --short

echo ""
echo -e "${YELLOW}❓ Files to commit (review above)${NC}"

# 3. Ask for confirmation
read -p "Proceed with commit? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# 4. Get commit message
echo ""
echo -e "${YELLOW}📝 Commit Message (one-line):${NC}"
read commit_msg

if [ -z "$commit_msg" ]; then
    echo -e "${RED}❌ Commit message cannot be empty${NC}"
    exit 1
fi

# 5. Stage all changes
echo ""
echo -e "${YELLOW}📦 Staging changes...${NC}"
git add .

# 6. Show diff
echo ""
echo -e "${YELLOW}🔍 Changes to commit:${NC}"
git diff --cached --stat

# 7. Confirm again
echo ""
read -p "Confirm commit? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    git reset
    exit 0
fi

# 8. Commit
echo ""
echo -e "${YELLOW}💾 Creating commit...${NC}"
git commit -m "$commit_msg" \
    -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

# 9. Push
echo ""
echo -e "${YELLOW}🚀 Pushing to GitHub...${NC}"
git push origin main

# 10. Success
echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""
echo "📊 Commit info:"
git log -1 --oneline
echo ""
echo "🔗 View on GitHub:"
echo "   https://github.com/yekaweb/dlbot-telegram/commits/main"
echo ""

# Optional: notify
echo -e "${GREEN}✨ Done!${NC}"
