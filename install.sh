#!/bin/bash

# ReconAI Installation Script
# This script helps set up ReconAI and its dependencies

set -e

echo "=== ReconAI Installation Script ==="

# Check if Python 3.8+ is available
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "Found Python $PYTHON_VERSION"
    
    # Check if version is 3.8+
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        echo "✓ Python version is compatible"
    else
        echo "✗ Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    echo "✗ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✓ Python dependencies installed"
else
    echo "✗ requirements.txt not found"
    exit 1
fi

# Install Bbot
echo ""
echo "Installing Bbot..."
if command -v bbot &> /dev/null; then
    echo "✓ Bbot already installed"
else
    echo "Installing Bbot via pip..."
    pip3 install bbot
    echo "✓ Bbot installed"
fi

# Create .env file if it doesn't exist
echo ""
echo "Setting up configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env file from template"
        echo "⚠ Please edit .env file and add your OpenAI API key"
    else
        echo "✗ .env.example not found"
    fi
else
    echo "✓ .env file already exists"
fi

# Create output directories
echo ""
echo "Creating directories..."
mkdir -p output logs config
echo "✓ Created output, logs, and config directories"

# Make scripts executable
echo ""
echo "Setting up permissions..."
chmod +x main.py test_installation.py
echo "✓ Made scripts executable"

# Run installation test
echo ""
echo "Running installation test..."
python3 test_installation.py

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Test the installation: python3 test_installation.py"
echo "3. Run your first scan: python3 main.py -t example.com"
echo ""
echo "For help: python3 main.py --help"