#!/bin/bash
# Monthly Dependency Update Script
# Run this script monthly to update dependencies and reduce real vulnerabilities

set -e

echo "🔄 Monthly Dependency Update Process"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Navigate to project root
cd "$(dirname "$0")/.."

echo "📦 Step 1: Update Node.js Dependencies (Auth Service)"
echo "-----------------------------------------------------"
cd services/auth-service

echo "Current package versions:"
npm list --depth=0 2>/dev/null || true

echo ""
echo "Checking for updates..."
npm outdated || true

echo ""
echo -e "${YELLOW}Updating to latest compatible versions...${NC}"
npm update

echo ""
echo -e "${YELLOW}Checking for security vulnerabilities...${NC}"
npm audit

echo ""
echo -e "${YELLOW}Attempting automatic fixes...${NC}"
npm audit fix

echo ""
echo -e "${GREEN}✅ Auth Service dependencies updated${NC}"
echo ""

cd ../..

echo "🐍 Step 2: Update Python Dependencies (Task Service)"
echo "-----------------------------------------------------"
cd services/task-service

echo "Current package versions:"
pip3 freeze | grep -E "(Flask|mysql|PyJWT|python-dotenv|Werkzeug|pydantic)" || true

echo ""
echo -e "${YELLOW}Updating packages...${NC}"
pip3 install --upgrade Flask flask-cors mysql-connector-python PyJWT python-dotenv Werkzeug Flask-Limiter pydantic

echo ""
echo "Updated versions:"
pip3 freeze | grep -E "(Flask|mysql|PyJWT|python-dotenv|Werkzeug|pydantic)"

echo ""
echo -e "${GREEN}✅ Task Service dependencies updated${NC}"
echo ""

cd ../..

echo "🎨 Step 3: Update Frontend Dependencies"
echo "-----------------------------------------------------"
cd services/frontend

echo "Current package versions:"
npm list --depth=0 2>/dev/null || true

echo ""
echo "Checking for updates..."
npm outdated || true

echo ""
echo -e "${YELLOW}Updating to latest compatible versions...${NC}"
npm update

echo ""
echo -e "${YELLOW}Checking for security vulnerabilities...${NC}"
npm audit

echo ""
echo -e "${YELLOW}Attempting automatic fixes...${NC}"
npm audit fix

echo ""
echo -e "${GREEN}✅ Frontend dependencies updated${NC}"
echo ""

cd ../..

echo "📝 Step 4: Update requirements.txt files"
echo "-----------------------------------------------------"

# Update auth-service package.json if changes were made
if [ -n "$(git status --porcelain services/auth-service/package*.json)" ]; then
    echo -e "${GREEN}✅ Auth service package files updated${NC}"
fi

# Update task-service requirements.txt
echo "Updating task-service/requirements.txt..."
cd services/task-service
pip3 freeze | grep -E "(Flask|flask-cors|mysql-connector-python|PyJWT|python-dotenv|Werkzeug|Flask-Limiter|pydantic)" > requirements.txt.new
if [ -f requirements.txt.new ]; then
    mv requirements.txt.new requirements.txt
    echo -e "${GREEN}✅ Task service requirements.txt updated${NC}"
fi

cd ../..

# Update frontend package.json if changes were made
if [ -n "$(git status --porcelain services/frontend/package*.json)" ]; then
    echo -e "${GREEN}✅ Frontend package files updated${NC}"
fi

echo ""
echo "🔍 Step 5: Test Services (Quick Smoke Test)"
echo "-----------------------------------------------------"

# Quick syntax checks
echo "Checking auth-service syntax..."
node -c services/auth-service/server.js && echo -e "${GREEN}✅ Auth service: OK${NC}" || echo -e "${RED}❌ Auth service: SYNTAX ERROR${NC}"

echo "Checking task-service syntax..."
python3 -m py_compile services/task-service/app.py && echo -e "${GREEN}✅ Task service: OK${NC}" || echo -e "${RED}❌ Task service: SYNTAX ERROR${NC}"

echo ""
echo "📊 Step 6: Generate Update Summary"
echo "-----------------------------------------------------"

echo ""
echo "Changes made:"
git diff --stat services/*/package*.json services/*/requirements.txt 2>/dev/null || echo "No dependency file changes"

echo ""
echo "🎯 Next Steps:"
echo "-------------"
echo "1. Review changes: git diff"
echo "2. Test locally: docker-compose up --build"
echo "3. Commit changes: git add . && git commit -m 'chore: update dependencies'"
echo "4. Push: git push"
echo "5. Monitor CI/CD pipeline for build success"
echo ""
echo -e "${GREEN}✅ Monthly update complete!${NC}"
echo ""
echo "📅 Next update due: $(date -d '+1 month' '+%B %Y')"
