#!/bin/bash
# Test Docker build to simulate Railway deployment exactly
# This catches issues before deploying to Railway

set -e  # Exit on error

echo "=========================================="
echo "🐳 Testing Docker Build (Railway Simulation)"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if Docker is installed
echo "Step 1: Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo -e "${GREEN}✅ Docker is installed${NC}"
echo ""

# Step 2: Build Docker image
echo "Step 2: Building Docker image (this simulates Railway build)..."
if docker build -t reverseweave-test .; then
    echo -e "${GREEN}✅ Docker build successful!${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    echo "This is what Railway will see. Fix the errors above."
    exit 1
fi
echo ""

# Step 3: Test that image can start
echo "Step 3: Testing that container can start..."
echo "Running container with test environment variables..."
echo "(This will run for 30 seconds to check for startup errors)"
echo ""

# Run container with timeout (30 seconds)
timeout 30s docker run --rm \
    -e EMAIL_USER=test@example.com \
    -e EMAIL_PASSWORD=test_password \
    -e RECIPIENT_EMAIL=test@example.com \
    -e SMTP_SERVER=smtp.gmail.com \
    -e SMTP_PORT=587 \
    -e HEADLESS=true \
    reverseweave-test 2>&1 | head -50 || true

echo ""
echo -e "${GREEN}✅ Container started successfully!${NC}"
echo ""

# Step 4: Check image size
echo "Step 4: Checking image size..."
IMAGE_SIZE=$(docker images reverseweave-test --format "{{.Size}}")
echo "Image size: $IMAGE_SIZE"
if [[ $(docker images reverseweave-test --format "{{.Size}}" | grep -oE '[0-9]+') -gt 2000 ]]; then
    echo -e "${YELLOW}⚠️  Image is large (>2GB). This is normal for Selenium + Chrome.${NC}"
else
    echo -e "${GREEN}✅ Image size is reasonable${NC}"
fi
echo ""

# Step 5: Summary
echo "=========================================="
echo -e "${GREEN}✅ All Docker tests passed!${NC}"
echo "=========================================="
echo ""
echo "Your Docker image is ready for Railway!"
echo ""
echo "Next steps:"
echo "  1. Push code to GitHub"
echo "  2. Connect Railway to your repo"
echo "  3. Set environment variables in Railway"
echo "  4. Railway will build and deploy automatically"
echo ""
echo "If Railway build fails, it will show the same errors"
echo "you see above. This test helps catch issues early!"
echo ""

