#!/bin/bash
# install.sh - SnakeByte Installation Script

set -e

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="snakebyte"
GITHUB_URL="https://raw.githubusercontent.com/pjcigan/snakebyte/main/snakebyte.py"

echo "SnakeByte Installation Script"
echo "=============================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.6 or later and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

# Check if we need sudo for installation
if [ ! -w "$INSTALL_DIR" ]; then
    SUDO="sudo"
    echo "Note: Installation requires sudo privileges"
else
    SUDO=""
fi

# Download and install
if [ -f "./snakebyte.py" ]; then
    echo "Found local snakebyte.py - installing from current directory..."
    
    # Verify it's a valid Python script
    if head -1 "./snakebyte.py" | grep -q "python"; then
        $SUDO cp "./snakebyte.py" "$INSTALL_DIR/$SCRIPT_NAME"
        echo "✓ Installed from local file"
    else
        echo "✗ Local snakebyte.py doesn't appear to be a valid Python script"
        echo "First line: $(head -1 ./snakebyte.py)"
        exit 1
    fi
else
    echo "Local snakebyte.py not found - downloading from GitHub..."
    
    if command -v curl &> /dev/null; then
        HTTP_CODE=$(curl -sSL -w "%{http_code}" "$GITHUB_URL" -o "$INSTALL_DIR/$SCRIPT_NAME.tmp")
        if [ "$HTTP_CODE" -eq 200 ]; then
            $SUDO mv "$INSTALL_DIR/$SCRIPT_NAME.tmp" "$INSTALL_DIR/$SCRIPT_NAME"
            echo "✓ Downloaded from GitHub"
        else
            echo "✗ Failed to download SnakeByte (HTTP $HTTP_CODE)"
            echo "Please check the URL: $GITHUB_URL"
            rm -f "$INSTALL_DIR/$SCRIPT_NAME.tmp"
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        if wget -q --spider "$GITHUB_URL"; then
            wget -qO "$INSTALL_DIR/$SCRIPT_NAME.tmp" "$GITHUB_URL"
            $SUDO mv "$INSTALL_DIR/$SCRIPT_NAME.tmp" "$INSTALL_DIR/$SCRIPT_NAME"
            echo "✓ Downloaded from GitHub"
        else
            echo "✗ Failed to download SnakeByte"
            echo "Please check the URL: $GITHUB_URL"
            exit 1
        fi
    else
        echo "✗ Neither curl nor wget found, and no local snakebyte.py available"
        echo "Please install curl or wget, or download snakebyte.py manually"
        exit 1
    fi
fi

# Make executable and verify
$SUDO chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

# Verify installation worked
if head -1 "$INSTALL_DIR/$SCRIPT_NAME" | grep -q "python"; then
    echo "✓ SnakeByte installed successfully to $INSTALL_DIR/$SCRIPT_NAME!"
else
    echo "✗ Installation failed - installed file doesn't appear to be a Python script"
    echo "First line of installed file:"
    head -1 "$INSTALL_DIR/$SCRIPT_NAME"
    echo "Please check the source file and try again."
    exit 1
fi
echo ""
echo "Usage: $SCRIPT_NAME <binary_file>"
echo "Example: $SCRIPT_NAME /path/to/your/file.bin"
echo ""
echo "To uninstall: $SUDO rm $INSTALL_DIR/$SCRIPT_NAME"
