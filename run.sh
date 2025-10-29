#!/bin/bash
# Run script for Champion Reverse Weave Monitor Bot

echo "🏆 Starting Champion Reverse Weave Monitor Bot..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please copy env_template.txt to .env and configure your email settings:"
    echo "cp env_template.txt .env"
    echo "nano .env"
    exit 1
fi

# Run the bot
echo "Starting bot..."
python3 main.py
