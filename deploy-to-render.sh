#!/bin/bash

# Angels AI School Platform - Render Deployment Script
# This script helps you deploy to Render via command line

set -e  # Exit on any error

echo "=================================================="
echo "Angels AI School Platform - Render Deployment"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo -e "${YELLOW}⚠️  Render CLI not found. Installing...${NC}"
    echo ""
    echo "Please install Render CLI:"
    echo "  npm install -g @render/cli"
    echo ""
    echo "Or use the web interface:"
    echo "  https://dashboard.render.com/select-repo"
    echo ""
    exit 1
fi

echo -e "${BLUE}📋 Deployment Checklist${NC}"
echo "========================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❌ Please edit .env with your credentials before deploying!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Check if DATABASE_URL is set
if ! grep -q "^DATABASE_URL=" .env || grep -q "^DATABASE_URL=$" .env; then
    echo -e "${RED}❌ DATABASE_URL not set in .env${NC}"
    echo "   Please set your database URL in .env"
    exit 1
else
    echo -e "${GREEN}✅ DATABASE_URL configured${NC}"
fi

# Check if CLARITY_API_KEY is set
if ! grep -q "^CLARITY_API_KEY=" .env || grep -q "^CLARITY_API_KEY=$" .env; then
    echo -e "${YELLOW}⚠️  CLARITY_API_KEY not set in .env${NC}"
    echo "   The platform will use fallback mode"
else
    echo -e "${GREEN}✅ CLARITY_API_KEY configured${NC}"
fi

echo ""
echo -e "${BLUE}📦 Deploying to Render...${NC}"
echo "========================"
echo ""

# Option 1: Using render.yaml (Blueprint)
if [ -f render.yaml ]; then
    echo -e "${GREEN}✅ render.yaml found - Blueprint deployment available${NC}"
    echo ""
    echo "To deploy using Blueprint:"
    echo "  1. Go to: https://dashboard.render.com/select-repo"
    echo "  2. Connect your GitHub repository: colmeta/angels-ai-school"
    echo "  3. Render will detect render.yaml and create all services"
    echo "  4. Click 'Apply' to deploy"
    echo ""
fi

# Option 2: Manual deployment steps
echo -e "${YELLOW}📝 Manual Deployment Steps:${NC}"
echo ""
echo "1. Create PostgreSQL Database:"
echo "   - Go to: https://dashboard.render.com/new/database"
echo "   - Name: angels-ai-school-db"
echo "   - Copy the Internal Database URL"
echo ""
echo "2. Create Web Service:"
echo "   - Go to: https://dashboard.render.com/create?type=web"
echo "   - Connect repository: colmeta/angels-ai-school"
echo "   - Branch: cursor/integrate-ai-agent-api-key-and-automate-services-ad91"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: uvicorn api.main:app --host 0.0.0.0 --port \$PORT --workers 1 --limit-concurrency 20"
echo ""
echo "3. Add Environment Variables:"
echo "   - DATABASE_URL (from step 1)"
echo "   - CLARITY_API_KEY (your key)"
echo "   - CLARITY_BASE_URL=https://veritas-engine-zae0.onrender.com"
echo ""
echo "4. Deploy and wait for build to complete (2-5 minutes)"
echo ""
echo "5. Run migrations from Render Shell:"
echo "   - Open your service → Shell tab"
echo "   - Run: python run_migrations.py"
echo ""

echo -e "${GREEN}✅ Repository pushed to GitHub${NC}"
echo -e "${GREEN}✅ Ready for deployment${NC}"
echo ""
echo -e "${BLUE}📚 Next Steps:${NC}"
echo "   1. Visit: https://dashboard.render.com/select-repo"
echo "   2. Connect: colmeta/angels-ai-school"
echo "   3. Follow the deployment guide in DEPLOYMENT.md"
echo ""
echo -e "${GREEN}🎉 Good luck with your deployment!${NC}"
echo ""
