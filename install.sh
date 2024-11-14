#!/bin/bash

# Constants
SCRIPT_URL="https://your-script-url-here.com/pingsploit.py"  # Replace with your actual script URL
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="pingsploit"

# Function to download PingSploit
download_script() {
    echo "Downloading PingSploit..."
    curl -L "$SCRIPT_URL" -o "$SCRIPT_NAME.py"  # Download the script (adjust URL as needed)
    if [ $? -ne 0 ]; then
        echo "Failed to download PingSploit. Please check the URL and try again."
        exit 1
    fi
}

# Function to make the script executable
make_executable() {
    echo "Making PingSploit executable..."
    chmod +x "$SCRIPT_NAME.py"
}

# Function to install the script
install_script() {
    echo "Installing PingSploit to $INSTALL_DIR..."
    mv "$SCRIPT_NAME.py" "$INSTALL_DIR/$SCRIPT_NAME"  # Move script to the install directory
    if [ $? -ne 0 ]; then
        echo "Failed to move the script to $INSTALL_DIR. Please check permissions."
        exit 1
    fi

    echo "PingSploit installed successfully. You can now run it as $SCRIPT_NAME from anywhere."
}

# Check if the script already exists in the install directory
if command -v "$SCRIPT_NAME" &>/dev/null; then
    echo "$SCRIPT_NAME already installed. Updating..."
    rm -f "$INSTALL_DIR/$SCRIPT_NAME"  # Remove existing script
fi

# Download, make executable, and install
download_script
make_executable
install_script

echo "Installation complete."
