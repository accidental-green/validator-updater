#!/bin/bash

APP_URL="https://github.com/accidental-green/validator-updater/releases/download/v1.0.0/Validator_Updater-1.0.0.AppImage"
APP_IMAGE="Validator_Updater-1.0.0.AppImage"
APP_TMP="/tmp/$APP_IMAGE"
APP_DEST="/usr/bin/validator_updater"

# Fix broken dpkg state if needed
sudo dpkg --configure -a || true

# Detect Ubuntu version
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
  sudo apt install -y python3 python3-pip libfuse2 libnss3 libxss1 libatk1.0-0 libgtk-3-0 libasound2
  sudo pip3 install requests || true
fi

# Download AppImage
echo "Downloading Validator Updater..."
wget -q "$APP_URL" -O "$APP_TMP"
chmod +x "$APP_TMP"

# Install depending on Ubuntu version
if [[ "$ubuntu_version" == "24.04" ]]; then
  echo "Extracting AppImage for Ubuntu 24.04..."
  "$APP_TMP" --appimage-extract

  sudo rm -rf /opt/validator_updater
  sudo mv squashfs-root /opt/validator_updater
  sudo chown root:root /opt/validator_updater/chrome-sandbox
  sudo chmod 4755 /opt/validator_updater/chrome-sandbox
  sudo ln -sf /opt/validator_updater/validator_updater "$APP_DEST"

  echo "AppImage extracted and installed in /opt."
else
  echo "Moving AppImage to $APP_DEST..."
  sudo mv "$APP_TMP" "$APP_DEST"
fi

# Launch the app
echo "Launching Validator Updater..."

if [[ "$ubuntu_version" == "24.04" ]]; then
  validator_updater --no-sandbox
else
  validator_updater
fi
