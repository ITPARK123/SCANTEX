# SCANTEX
Auto scanner for Acunetix

SCANTEX automates subdomain scanning via Acunetix:

<img width="736" height="393" alt="scantex" src="https://github.com/user-attachments/assets/2f3b0678-df84-451f-9d6d-6f10029a41e9" />

- Discovers subdomains using `SubFinder`
- Checks live hosts with `httpx`
- Auto-creates targets and starts scans in Acunetix
- Supports proxy and scheduled delays

---

###  How It Works

1. Put domains in `target.txt`
2. Format Domain test.com  *no http/https
3. Run `./scantex.py`
4. It handles everything:
   - Scans for subdomains
   - Checks live hosts
   - Adds to Acunetix
   - Starts scans with optional delay

---

###  Requirements

- Python 3.7+
- Go 1.21+
- Access to Acunetix API

---

###  Setup

```bash
chmod +x setup.sh
./setup.sh

source scantex-env/bin/activate
./scantex.py
