#!/bin/bash
# WalletTracker v1.0 - Bitcoin Wallet IP Detection Tool
# GitHub: https://github.com/yourusername/wallet-tracker

echo "🚀 Installing WalletTracker..."

# Dependencies
sudo apt update
sudo apt install -y bettercap tshark wireshark-common nmap python3-pip git

# Python deps
pip3 install PyQt5 pandas scapy pyqt5-tools

# Clone & Setup
cd /opt
sudo rm -rf wallet-tracker
sudo git clone https://github.com/yourusername/wallet-tracker.git
cd wallet-tracker
sudo chmod +x *.sh
sudo mkdir -p logs

# Desktop shortcut
cat > ~/.local/share/applications/wallet-tracker.desktop << EOF
[Desktop Entry]
Name=WalletTracker
Comment=Bitcoin Wallet IP Tracker
Exec=sudo /opt/wallet-tracker/start.sh
Icon=/opt/wallet-tracker/assets/icon.png
Terminal=false
Type=Application
Categories=Network;Security;
EOF

echo "✅ Installed! Run: sudo start.sh TARGET_IP"
echo "Or search 'WalletTracker' in menu"
