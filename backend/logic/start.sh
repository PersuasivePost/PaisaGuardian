#!/bin/bash

# Quick Start Script for Fraud Detection API
# This script sets up and runs the FastAPI server

set -e

echo "🚀 Fraud Detection API - Quick Start"
echo "===================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Run requirements checker
echo ""
echo "🔍 Checking requirements..."
python3 check_requirements.py

# Check if .env exists, if not it was created by check_requirements.py
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Creating .env file..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created from template"
    fi
fi

# Start the server
echo ""
echo "🌟 Starting FastAPI server..."
echo ""
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API documentation: http://localhost:8000/docs"
echo "📘 ReDoc: http://localhost:8000/redoc"
echo ""
echo "🎯 New Features:"
echo "   • QR code fraud detection"
echo "   • Domain analysis (age, SSL)"
echo "   • HTML threat detection"
echo "   • UPI intent analysis"
echo "   • SIM swap detection"
echo "   • Screen sharing app detection"
echo ""
echo "📡 API Endpoints (no /api prefix):"
echo "   POST /analyze/url         - URL analysis (Chrome)"
echo "   POST /analyze/sms         - SMS analysis (Mobile)"
echo "   POST /analyze/transaction - Transaction analysis"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "===================================="
echo ""

# Run the server
python3 main.py
