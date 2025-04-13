#!/bin/bash

set -e

APP_URL="https://github.com/accidental-green/validator-updater/releases/download/v1.0.0/Validator_Updater-1.0.0.AppImage"
APP_IMAGE="Validator_Updater-1.0.0.AppImage"
APP_DEST="/usr/bin/validator_updater"

# Fix broken dpkg state if needed
sudo dpkg --configure -a || true

# Get Ubuntu version
. /etc/os-release
ubuntu_version="$VERSION_ID"

# Install dependencies
echo "Installing Python and required packages for Ubuntu $ubuntu_version..."
sudo apt update -y
sudo add-apt-repository universe -y
sudo apt update -y

if [[ "$ubuntu_version" == "24.04" ]]; then
  sudo apt install -y python3 python3-pip python3-requests libfuse2
else
  sudo apt install -y python3 python3-pip libfuse2
  sudo pip3 install requests
fi

# Download and install Validator Updater
echo "Downloading Validator Updater..."
wget -q "$APP_URL" -O /tmp/$APP_IMAGE
chmod +x /tmp/$APP_IMAGE

if [[ "$ubuntu_version" == "24.04" ]]; then
  echo "Extracting AppImage for 24.04..."
  /tmp/$APP_IMAGE --appimage-extract

  sudo rm -rf /opt/validator_updater
  sudo mv squashfs-root /opt/validator_updater
  sudo chown root:root /opt/validator_updater/chrome-sandbox
  sudo chmod 4755 /opt/validator_updater/chrome-sandbox
  sudo ln -sf /opt/validator_updater/validator_updater $APP_DEST
else
  echo "Moving AppImage to $APP_DEST..."
  sudo mv /tmp/$APP_IMAGE $APP_DEST
fi

# Launch app
echo "Launching Validator Updater..."
validator_updater --no-sandbox &
