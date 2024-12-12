#!/bin/bash

# === STEP 1: INSTALL XCODE COMMAND LINE TOOLS ===
echo "🚀 Checking for Xcode Command Line Tools..."

# Check if Xcode Command Line Tools are installed
if ! xcode-select -p &> /dev/null
then
    echo "🚀 Installing Xcode Command Line Tools..."
    xcode-select --install

    # Wait for the installation to complete
    echo "⌛ Waiting for the Xcode Command Line Tools installation to complete..."
    
    # Wait for up to 10 minutes for the installation to complete
    for i in {1..60}
    do
        if xcode-select -p &> /dev/null
        then
            echo "✅ Xcode Command Line Tools installed successfully!"
            break
        fi
        sleep 10  # Check every 10 seconds
    done

    # Verify the installation
    if ! xcode-select -p &> /dev/null
    then
        echo "❌ Failed to install Xcode Command Line Tools. Please install them manually by running 'xcode-select --install'."
        exit 1
    fi
else
    echo "✅ Xcode Command Line Tools are already installed."
fi

# === STEP 2: CHECK FOR PYTHON 3 AVAILABILITY ===
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed on this MacBook."
    exit 1
else
    echo "✅ Python3 is already installed."
fi

# === STEP 3: CHECK FOR PIP FOR PYTHON 3 ===
if ! command -v pip3 &> /dev/null
then
    echo "🚀 Installing pip for Python 3..."
    python3 -m ensurepip
    python3 -m pip install --upgrade pip
else
    echo "✅ pip is already installed."
fi

# === STEP 4: INSTALL DEPENDENCIES FROM requirements.txt (if it exists) ===
if [ -f "requirements.txt" ]; then
    echo "🚀 Installing dependencies from requirements.txt..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    echo "⚠️  The requirements.txt file was not found. Skipping dependency installation."
fi

# === STEP 5: RUN THE PYTHON SCRIPT ===
if [ -f "main.py" ]; then
    echo "🚀 Running the Python script main.py..."
    python3 main.py
else
    echo "⚠️  The file main.py was not found. Make sure it is located in the same directory as this script."
fi

echo "✅ Installation complete. The Python script has run successfully!"
