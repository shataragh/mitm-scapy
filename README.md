# MITM Scapy Script

This script performs a Man-in-the-Middle (MITM) attack using ARP spoofing and Scapy's packet sniffing capabilities. It captures HTTP traffic, extracts sensitive information (e.g., URLs, credentials, cookies), and logs it for analysis.

## Features
- ARP spoofing to redirect traffic between the target and gateway.
- Packet sniffing to capture HTTP traffic on port 80.
- Extraction of:
  - URLs
  - Credentials (e.g., usernames, passwords)
  - Cookies
- Automatic restoration of network settings upon termination.

## Prerequisites
- Linux-based environment (tested on Ubuntu/WSL2).
- Python 3.x.
- Root privileges (required for ARP spoofing and packet sniffing).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mitm-scapy.git
   cd mitm-scapy
