#!/bin/bash
# Script to set Railway environment variables from a local file
# This allows you to manage variables locally and push them to Railway

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Setting Railway Environment Variables"
echo "=========================================="
echo ""

# Add npm global bin to PATH if needed
if [ -d "$HOME/.npm-global/bin" ]; then
    export PATH="$PATH:$HOME/.npm-global/bin"
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI is not installed${NC}"
    echo ""
    echo "Install it with:"
    echo "  npm i -g @railway/cli"
    echo ""
    echo "If installed but not found, add to PATH:"
    echo "  export PATH=\"\$PATH:\$HOME/.npm-global/bin\""
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI is installed${NC}"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo ""
    echo "Creating .env file from template..."
    cp env_template.txt .env
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo ""
    echo "Please edit .env file with your actual values, then run this script again."
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ .env file found${NC}"
echo ""

# Check if logged in to Railway
echo "Checking Railway login status..."
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Railway${NC}"
    echo ""
    echo "Logging in..."
    railway login
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Login failed${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Logged in to Railway${NC}"
echo ""

# Check if project is linked
echo "Checking if project is linked..."
if ! railway status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Project not linked${NC}"
    echo ""
    echo "Linking project..."
    railway link
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Link failed${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Project is linked${NC}"
echo ""

# Read .env file and set variables
echo "Reading .env file and setting variables..."
echo ""

VARS_SET=0
VARS_SKIPPED=0

while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    
    # Remove leading/trailing whitespace
    line=$(echo "$line" | xargs)
    
    # Skip if line doesn't contain =
    [[ ! "$line" =~ = ]] && continue
    
    # Split on first = only (values may contain =)
    key="${line%%=*}"
    value="${line#*=}"
    
    # Remove leading/trailing whitespace from key and value
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    
    # Skip if key or value is empty
    [[ -z "$key" || -z "$value" ]] && continue
    
    # Skip if value is template placeholder
    if [[ "$value" == "your_email@gmail.com" || "$value" == "your_app_password" || "$value" == "your_email@example.com" ]]; then
        echo -e "${YELLOW}⚠️  Skipping $key (placeholder value)${NC}"
        VARS_SKIPPED=$((VARS_SKIPPED + 1))
        continue
    fi
    
    # Set variable in Railway
    echo "Setting $key..."
    export PATH="$PATH:$HOME/.npm-global/bin"
    
    # Set the variable using correct Railway CLI syntax
    OUTPUT=$(railway variables --set "$key=$value" 2>&1)
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ Set $key${NC}"
        VARS_SET=$((VARS_SET + 1))
    else
        echo -e "${RED}❌ Failed to set $key${NC}"
        if [ -n "$OUTPUT" ]; then
            echo "   Error: $(echo "$OUTPUT" | head -1)"
        fi
    fi
done < .env

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "${GREEN}✅ Variables set: $VARS_SET${NC}"
if [ $VARS_SKIPPED -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Variables skipped: $VARS_SKIPPED${NC}"
fi
echo ""
echo "Railway will automatically restart your service."
echo "Check Railway logs to verify variables are working."
echo ""

