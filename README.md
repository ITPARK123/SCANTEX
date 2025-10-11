# SCANTEX
Auto scanner for Acunetix

SCANTEX automates subdomain scanning via Acunetix:

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
