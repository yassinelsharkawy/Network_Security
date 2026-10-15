# NetworkSecurity

NetworkSecurity is a Python-based toolkit for network analysis, security testing, and web application assessment. It brings together a set of command-line tools for reconnaissance, traffic inspection, vulnerability checks, and remote access testing in a single interface.

This project is intended for authorized testing and controlled environments only. Use it only on systems and networks you own or have explicit permission to evaluate.

## Overview

The toolkit includes utilities for:

- MAC address management
- network scanning
- ARP spoofing detection and traffic interception
- packet sniffing
- DNS manipulation
- web crawling and form extraction
- vulnerability scanning
- remote access and command execution tools

## Requirements

- Linux-based environment such as Kali Linux or Debian
- Python 3.8 or newer
- Root or administrator privileges for network-level modules
- Dependencies listed in requirements.txt

For Linux packages commonly required by networking modules, install:

```bash
sudo apt update
sudo apt install -y build-essential libnetfilter-queue-dev python3-dev
```

## Installation

```bash
git clone <repository-url>
cd Network_Security
pip install -r requirements.txt
```

To run the project from the repository root:

```bash
python networksecurity.py --help
```

Or, if installed as a package:

```bash
networksecurity --help
```

## Basic Usage

List available tools:

```bash
networksecurity --list
```

Display the main help menu:

```bash
networksecurity --help
```

Example network scan:

```bash
sudo networksecurity --scan -t 192.168.1.0/24
```

Example ARP spoof check:

```bash
sudo networksecurity --arp-spoof -t 192.168.1.15 -s 192.168.1.1
```

Example packet sniffing:

```bash
sudo networksecurity --sniff -i eth0
```

## Project Structure

- `networksecurity.py` - main entry point
- `modules/` - individual security tools
- `core/` - shared utilities and checks
- `tests/` - project test files
- `README.md` - project documentation

## Legal Notice

This software is provided for authorized security testing and educational use only. It must not be used against any system without explicit permission from the owner.
The authors are not responsible for misuse, damage, or legal issues resulting from improper use of this project.

