#!/bin/bash

set -e

# Fix broken dpkg state if necessary
sudo dpkg --configure -a || true

# Function to detect the Ubuntu version
get_ubuntu_version() {
  . /etc/os-release
  echo "$VERSION_ID"
}

# Function to install Python and dependencies
install_python_and_dependencies() {
  echo "Installing dependencies for Ubuntu $1"
  sudo apt update -y
  sudo add-apt-repository universe -y
  sudo apt update -y

  if [ "$1" == "24.04" ]; then
    sudo apt install -y python3 python3-pip python3-requests libfuse2
  else
    sudo apt install -y python3 python3-pip libfuse2
    sudo pip3 install requests
  fi
}

# Function to install Validator Updater for Ubuntu 24.04 (extracted AppImage)
install_validator_updater_24_04() {
  echo "Installing Validator Updater for Ubuntu 24.04..."
  wget https://github.com/accidental-green/validator-updater/releases/download/v1.0.0/Validator_Updater-1.0.0.AppImage -O Validator_Updater-1.0.0.AppImage
  chmod +x Validator_Updater-1.0.0.AppImage
  ./Validator_Updater-1.0.0.AppImage --appimage-extract

  sudo rm -rf /opt/validator_updater
  sudo mv squashfs-root /opt/validator_updater

  sudo chown root:root /opt/validator_updater/chrome-sandbox
  sudo chmod 4755 /opt/validator_updater/chrome-sandbox

  sudo ln -sf /opt/validator_updater/validator_updater /usr/bin/validator_updater
}

# Function to install Validator Updater for Ubuntu 20.04 and 22.04
install_validator_updater_20_22() {
  echo "Installing Validator Updater for Ubuntu 20.04/22.04..."
  wget https://github.com/accidental-green/validator-updater/releases/download/v1.0.0/Validator_Updater-1.0.0.AppImage -O Validator_Updater-1.0.0.AppImage
  chmod +x Validator_Updater-1.0.0.AppImage
  sudo mv Validator_Updater-1.0.0.AppImage /usr/bin/validator_updater
}

# Main execution
ubuntu_version=$(get_ubuntu_version)

case "$ubuntu_version" in
  "24.04")
    install_python_and_dependencies "$ubuntu_version"
    install_validator_updater_24_04
    ;;
  "20.04"|"22.04")
    install_python_and_dependencies "$ubuntu_version"
    install_validator_updater_20_22
    ;;
  *)
    echo "Unsupported or unknown Ubuntu version. Attempting generic install..."
    install_python_and_dependencies "other"
    install_validator_updater_20_22
    ;;
esac

echo "Launching Validator Updater with --no-sandbox..."
validator_updater --no-sandbox &
