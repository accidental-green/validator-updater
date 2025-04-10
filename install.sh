#!/bin/bash

set -e

# Function to detect the Ubuntu version
get_ubuntu_version() {
  . /etc/os-release
  echo "$VERSION_ID"
}

# Function to install Python and dependencies
install_python_and_dependencies() {
  echo "Installing dependencies for Ubuntu $1"
  sudo apt update -y
  # Enable universe repository for Ubuntu
  sudo add-apt-repository universe -y
  sudo apt update -y
  
  if [ "$1" == "24.04" ]; then
    # Special handling for Ubuntu 24.04
    sudo apt install -y python3 python3-pip python3-requests libfuse2
  else
    sudo apt install -y python3 python3-pip libfuse2
    sudo pip3 install requests
  fi
}

# Function to install Validator Updater for Ubuntu 24.04 (extracting the AppImage)
install_validator_updater_24_04() {
  echo "Downloading and extracting Validator Updater for Ubuntu 24.04..."
  wget https://github.com/accidental-green/Validator_Updater/releases/download/v1.0.0-alpha/Validator_Updater-1.0.0.AppImage -O Validator_Updater-1.0.0.AppImage
  chmod +x Validator_Updater-1.0.0.AppImage
  ./Validator_Updater-1.0.0.AppImage --appimage-extract

  # Remove existing /opt/validator_updater directory if it exists
  if [ -d "/opt/validator_updater" ]; then
    echo "/opt/validator_updater already exists. Removing it..."
    sudo rm -rf /opt/validator_updater
  fi

  # Move extracted files to /opt/validator_updater
  sudo mv squashfs-root /opt/validator_updater

  # Set the correct permissions for chrome-sandbox
  sudo chown root:root /opt/validator_updater/chrome-sandbox
  sudo chmod 4755 /opt/validator_updater/chrome-sandbox

  # Create a symlink to the executable in /usr/bin for easy access
  sudo ln -sf /opt/validator_updater/validator_updater /usr/bin/validator_updater

  echo "Validator Updater has been successfully installed. You can run it by typing 'validator_updater'"
}

# Function to install Validator Updater for Ubuntu 20.04 and 22.04 (direct AppImage usage)
install_validator_updater_20_22() {
  echo "Downloading and installing Validator Updater for Ubuntu 20.04/22.04..."
  wget https://github.com/accidental-green/Validator_Updater/releases/download/v1.0.0-alpha/Validator_Updater-1.0.0.AppImage -O Validator_Updater-1.0.0.AppImage
  chmod +x Validator_Updater-1.0.0.AppImage
  sudo mv Validator_Updater-1.0.0.AppImage /usr/bin/validator_updater

  echo "Validator Updater has been successfully installed. You can run it by typing 'validator_updater'"
}

# Function to create desktop icon for Validator Updater
create_desktop_icon() {
  echo "Creating desktop entry for Validator Updater..."
  cat <<EOF | sudo tee /usr/share/applications/validator-updater.desktop > /dev/null
[Desktop Entry]
Version=1.0
Name=Validator Updater
Exec=/usr/bin/validator_updater
Icon=/opt/validator_updater/resources/app/assets/logo.png
Terminal=false
Type=Application
Categories=Utility;
EOF
  echo "Desktop entry for Validator Updater has been created."
}

# Main script execution
ubuntu_version=$(get_ubuntu_version)

case "$ubuntu_version" in
  "20.04"|"22.04")
    install_python_and_dependencies "$ubuntu_version"
    install_validator_updater_20_22
    ;;
  "24.04")
    install_python_and_dependencies "$ubuntu_version"
    install_validator_updater_24_04
    ;;
  *)
    echo "Unsupported Ubuntu version or non-Ubuntu system detected. Attempting general installation."
    install_python_and_dependencies "other"
    install_validator_updater_20_22
    ;;
esac

create_desktop_icon

# Run the application
validator_updater &
