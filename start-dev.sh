#!/bin/bash
# MindX Online Judge - Development Startup Script
# Round 2 MVP: Auth + Database + Frontend

set -e

echo "🚀 MindX Online Judge - Starting Development Environment"
echo "========================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the project root
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Step 1: Check Python dependencies
echo -e "\n${BLUE}[1/4]${NC} Checking Python environment..."
cd api-server
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3.12 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Python dependencies ready${NC}"
cd ..

# Step 2: Initialize database if needed
echo -e "\n${BLUE}[2/4]${NC} Checking database..."
if [ ! -f "api-server/data/mindx_judge.db" ]; then
    echo -e "${YELLOW}Database not found. Initializing...${NC}"
    cd api-server
    source venv/bin/activate
    python3.12 -m app.db.init_db
    cd ..
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${GREEN}✓ Database exists${NC}"
fi

# Step 3: Check Node.js dependencies
echo -e "\n${BLUE}[3/4]${NC} Checking Node.js dependencies..."
cd web-app
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm packages...${NC}"
    npm install
fi
echo -e "${GREEN}✓ Node.js dependencies ready${NC}"
cd ..

# Step 4: Start services
echo -e "\n${BLUE}[4/4]${NC} Starting services..."
echo -e "${GREEN}✓ Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}✓ Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}✓ API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo "========================================================="

# Start backend in background
cd api-server
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend in foreground
cd web-app
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT
