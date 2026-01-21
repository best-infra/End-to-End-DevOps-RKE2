#!/bin/bash

# GitHub Actions CI/CD Setup Script
# This script helps you configure GitHub secrets and test the pipeline

set -e

echo "╔══════════════════════Vulnerabilities══════════════════════════════════════╗"
echo "║   GitHub Actions CI/CD Pipeline Setup                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if logged in
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI is ready${NC}"
echo ""

# Ask which registry to use
echo "Which container registry will you use?"
echo "1) Docker Hub (easier, free)"
echo "2) AWS ECR (production-ready)"
read -p "Enter choice (1 or 2): " REGISTRY_CHOICE

if [ "$REGISTRY_CHOICE" = "1" ]; then
    echo ""
    echo -e "${BLUE}📦 Setting up Docker Hub integration${NC}"
    echo ""
    
    read -p "Enter your Docker Hub username: " DOCKER_USERNAME
    read -sp "Enter your Docker Hub password or token: " DOCKER_PASSWORD
    echo ""
    
    echo "Setting GitHub secrets..."
    echo "$DOCKER_USERNAME" | gh secret set DOCKER_USERNAME
    echo "$DOCKER_PASSWORD" | gh secret set DOCKER_PASSWORD
    
    echo -e "${GREEN}✅ Docker Hub secrets configured${NC}"
    echo ""
    echo "Active workflow: .github/workflows/ci-cd-pipeline.yml"
    
elif [ "$REGISTRY_CHOICE" = "2" ]; then
    echo ""
    echo -e "${BLUE}☁️  Setting up AWS ECR integration${NC}"
    echo ""
    
    read -p "Enter your AWS Access Key ID: " AWS_ACCESS_KEY_ID
    read -sp "Enter your AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
    echo ""
    read -p "Enter your AWS Account ID: " AWS_ACCOUNT_ID
    read -p "Enter AWS Region (default: us-east-1): " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    
    echo "Setting GitHub secrets..."
    echo "$AWS_ACCESS_KEY_ID" | gh secret set AWS_ACCESS_KEY_ID
    echo "$AWS_SECRET_ACCESS_KEY" | gh secret set AWS_SECRET_ACCESS_KEY
    echo "$AWS_ACCOUNT_ID" | gh secret set AWS_ACCOUNT_ID
    
    echo -e "${GREEN}✅ AWS ECR secrets configured${NC}"
    echo ""
    echo "Active workflow: .github/workflows/ci-cd-ecr.yml"
else
    echo -e "${RED}Invalid choice${NC}"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Configured secrets:"
gh secret list
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Testing the pipeline..."
echo ""

# Run test workflow
if gh workflow run test-pipeline.yml; then
    echo -e "${GREEN}✅ Test workflow triggered${NC}"
    echo ""
    echo "View status: gh run list"
    echo "View logs: gh run view --log"
else
    echo -e "${YELLOW}⚠️  Could not trigger test workflow automatically${NC}"
    echo "Manually trigger it from: Actions → Test CI Pipeline → Run workflow"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Wait for test workflow to complete"
echo "   → gh run watch"
echo ""
echo "2. Make a change to test the full pipeline:"
echo "   → echo '// test' >> services/frontend/src/App.jsx"
echo "   → git add services/frontend/src/App.jsx"
echo "   → git commit -m 'test: trigger CI pipeline'"
echo "   → git push"
echo ""
echo "3. Monitor the pipeline:"
echo "   → gh run list --workflow=ci-cd-pipeline.yml"
echo "   → gh run watch"
echo ""
echo "4. View security scan results:"
echo "   → Open GitHub → Security tab → Code scanning"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🚀 Your CI/CD pipeline is ready!${NC}"
echo ""
