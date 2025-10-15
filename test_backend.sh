#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Backend API Connection Test"
echo "========================================"

# Check if backend is running
echo -e "\n${YELLOW}1. Checking if backend is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}[PASS] Backend is running on port 5000${NC}"
else
    echo -e "${RED}[FAIL] Backend is NOT running on port 5000${NC}"
    echo "Please start the backend with: cd backend && python app.py"
    exit 1
fi

# Test health endpoint
echo -e "\n${YELLOW}2. Testing /health endpoint...${NC}"
response=$(curl -s http://localhost:8000/health)
if echo "$response" | grep -q "healthy"; then
    echo -e "${GREEN}[PASS] Health check passed${NC}"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo -e "${RED}[FAIL] Health check failed${NC}"
fi

# Test root endpoint
echo -e "\n${YELLOW}3. Testing root / endpoint...${NC}"
response=$(curl -s http://localhost:8000/)
if echo "$response" | grep -q "Inventory Management API"; then
    echo -e "${GREEN}[PASS] Root endpoint working${NC}"
else
    echo -e "${RED}[FAIL] Root endpoint failed${NC}"
fi

# Test inventory endpoint
echo -e "\n${YELLOW}4. Testing /api/inventory endpoint...${NC}"
response=$(curl -s "http://localhost:8000/api/inventory?location=san_jose")
if echo "$response" | grep -q "success"; then
    item_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_items', 0))" 2>/dev/null)
    echo -e "${GREEN}[PASS] Inventory endpoint working${NC}"
    echo "Found $item_count items for san_jose location"
else
    echo -e "${RED}[FAIL] Inventory endpoint failed${NC}"
    echo "Response: $response"
fi

# Test search endpoint
echo -e "\n${YELLOW}5. Testing /api/inventory/search endpoint...${NC}"
response=$(curl -s "http://localhost:8000/api/inventory/search?q=drill&location=san_jose")
if echo "$response" | grep -q "success"; then
    echo -e "${GREEN}[PASS] Search endpoint working${NC}"
else
    echo -e "${RED}[FAIL] Search endpoint failed${NC}"
fi

# Test active checkouts endpoint
echo -e "\n${YELLOW}6. Testing /api/checkout/active endpoint...${NC}"
response=$(curl -s "http://localhost:8000/api/checkout/active")
if echo "$response" | grep -q "success"; then
    checkout_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_active_checkouts', 0))" 2>/dev/null)
    echo -e "${GREEN}[PASS] Active checkouts endpoint working${NC}"
    echo "Found $checkout_count active checkouts"
else
    echo -e "${RED}[FAIL] Active checkouts endpoint failed${NC}"
fi

# Test CORS headers
echo -e "\n${YELLOW}7. Testing CORS headers...${NC}"
cors_headers=$(curl -s -I -X OPTIONS http://localhost:8000/api/inventory \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: GET")
if echo "$cors_headers" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}[PASS] CORS headers present${NC}"
else
    echo -e "${YELLOW}[WARN] CORS headers not found (may need to check CORS configuration)${NC}"
fi

echo -e "\n========================================"
echo -e "${GREEN}Backend API Tests Complete!${NC}"
echo "========================================"
echo -e "\nNext step: Start the frontend with:"
echo "  cd frontend && npm run dev"
echo -e "\nThen open http://localhost:3000 in your browser"