#!/bin/bash

# === CHECKING FOR PYTHON 3 AVAILABILITY ===
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed on this MacBook."
    exit 1
else
    echo "✅ Python3 is already installed."
fi

# === CHECKING FOR PIP FOR PYTHON 3 ===
if ! command -v pip3 &> /dev/null
then
    echo "🚀 Installing pip for Python 3..."
    python3 -m ensurepip
    python3 -m pip install --upgrade pip
else
    echo "✅ pip is already installed."
fi

# === INSTALLING DEPENDENCIES FROM requirements.txt (if it exists) ===
if [ -f "requirements.txt" ]; then
    echo "🚀 Installing dependencies from requirements.txt..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    echo "⚠️  The requirements.txt file was not found. Skipping dependency installation."
fi

# === RUNNING THE PYTHON SCRIPT ===
if [ -f "main.py" ]; then
    echo "🚀 Running the Python script main.py..."
    python3 main.py
else
    echo "⚠️  The file main.py was not found. Make sure it is located in the same directory as this script."
fi

echo "✅ Installation complete. The Python script has run successfully!"
