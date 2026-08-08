#!/bin/bash
# setup.sh — Quick setup for steel-monitor-v2
# Downloads fonts and installs dependencies

set -e

echo "🔧 Setting up steel-monitor-v2..."

# Create directories
mkdir -p fonts output

# Download Vazirmatn fonts
echo "📥 Downloading Vazirmatn fonts..."
curl -sL -o fonts/Vazirmatn.ttf "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Regular.ttf"
curl -sL -o fonts/Vazirmatn-Bold.ttf "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Bold.ttf"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install requests beautifulsoup4 Pillow jdatetime arabic-reshaper python-bidi

echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  python3 monitor.py saebsteelco    # Check single channel"
echo "  python3 monitor.py --all          # Check all channels"
echo "  python3 monitor.py --list         # List channels"
