#!/usr/bin/env python3
import sys, subprocess, json, pandas as pd, time, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class WalletTrackerTool(QMainWindow):
    def __init__(self, target_ip, interface):
        super().__init__()
        self.target_ip = target_ip
        self.interface = interface
        self.detections = []
        self.init_ui()
        self.start_capture()
        
    def init_ui(self):
        self.setWindowTitle("WalletTracker Pro v1.0")
        self.setGeometry(50, 50, 1400, 900)
        self.setStyleSheet("background-color: #1e1e1e; color: #00ff88;")
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel(f"🎯 TARGET: {self.target_ip} | Interface: {self.interface}")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; background: #333;")
        layout.addWidget(header)
        
        # Control Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ START CAPTURE")
        self.stop_btn = QPushButton("⏹ STOP")
        self.scan_btn = QPushButton("🔍 SCAN NETWORK")
        self.export_btn = QPushButton("💾 EXPORT CSV")
        
        for btn in [self.start_btn, self.stop_btn, self.scan_btn, self.export_btn]:
            btn.setStyleSheet("padding: 10px; font-size: 14px; background: #00ff88; border: none;")
            btn.clicked.connect(self.handle_button)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.export_btn)
        layout.addLayout(btn_layout)
        
        # Main Table
        self.table = QTableWidget(0, 8)
        headers = ["🕒 Time", "📡 SRC→DST", "🔌 Port", "💰 Wallet", "📦 Size", "📱 Device", "🚩 Risk", "🔗 Action"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Status
        self.status = QLabel("Ready to capture wallet traffic...")
        layout.addWidget(self.status)
        
        self.populate_table()
        
    def handle_button(self):
        btn = self.sender()
        if btn.text() == "🔍 SCAN NETWORK":
            self.scan_network()
        elif btn.text() == "💾 EXPORT CSV":
            self.export_csv()
            
    def scan_network(self):
        result = subprocess.run(["nmap", "-sn", "192.168.1.0/24"], 
                              capture_output=True, text=True)
        ips = [line.split()[-1] for line in result.stdout.split('\n') if 'Nmap' not in line]
        self.status.setText(f"Found {len(ips)} devices. Pick target!")
        
    def export_csv(self):
        df = pd.DataFrame(self.detections)
        filename = f"/opt/wallet-tracker/logs/{self.target_ip}_{int(time.time())}.csv"
        df.to_csv(filename, index=False)
        self.status.setText(f"✅ Exported to {filename}")
        
    def populate_table(self):
        # Live update logic (same as before but enhanced UI)
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    target = sys.argv[1] if len(sys.argv) > 1 else input("Target IP: ")
    iface = sys.argv[2] if len(sys.argv) > 2 else None
    window = WalletTrackerTool(target, iface)
    window.show()
    sys.exit(app.exec_())
