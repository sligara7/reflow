#!/bin/bash
# Reflow System Setup Script
# Installs required dependencies for the stand-alone reflow architecture workflow system

echo "🔧 Setting up Reflow Architecture Workflow System"
echo "================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install networkx matplotlib pygraphviz

# Check if system packages need to be installed (for pygraphviz)
echo ""
echo "🔧 Checking system dependencies..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get &> /dev/null; then
        echo "Detected Ubuntu/Debian system"
        echo "Installing graphviz system packages..."
        sudo apt-get update
        sudo apt-get install -y graphviz graphviz-dev
    elif command -v yum &> /dev/null; then
        echo "Detected RHEL/CentOS system"
        echo "Installing graphviz system packages..."
        sudo yum install -y graphviz graphviz-devel
    elif command -v dnf &> /dev/null; then
        echo "Detected Fedora system"
        echo "Installing graphviz system packages..."
        sudo dnf install -y graphviz graphviz-devel
    else
        echo "⚠️  Unknown Linux distribution. Please install graphviz and graphviz-dev manually."
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    if command -v brew &> /dev/null; then
        echo "Installing graphviz via Homebrew..."
        brew install graphviz
    else
        echo "⚠️  Homebrew not found. Please install graphviz manually or install Homebrew first."
    fi
else
    echo "⚠️  Unsupported OS: $OSTYPE"
    echo "Please install graphviz manually for your system."
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🧪 Running validation..."
python3 ./tools/validate_reflow_setup.py

echo ""
echo "🚀 Reflow system is ready to use!"
echo ""
echo "Quick start:"
echo "  1. Navigate to your project directory"
echo "  2. Use decision_flow.json to determine entry point"
echo "  3. Follow the rigorous workflow with automated validation"
echo ""
echo "For more information, see README_STANDALONE.md"