#!/bin/bash

# 🛠 Enhanced SCANTEX Setup Script v1.4 (with Auto-Go)
# GitHub: https://github.com/itpark/scantex

echo "=============================================="
echo " Installing SCANTEX with Auto-GO..."
echo "=============================================="

# 
apt update

# 
if ! dpkg -l | grep -q python3-venv; then
    echo "[] Installing python3-venv..."
    apt install -y python3-venv
fi

# 
if ! command -v wget &> /dev/null; then
    echo "[] Installing wget..."
    apt install -y wget
fi

# 
if [ -d "/usr/local/go" ]; then
    echo "[🗑] Removing old Go..."
    rm -rf /usr/local/go
fi

# 
echo "[] Installing latest Go..."
curl -sS https://raw.githubusercontent.com/udhos/update-golang/master/update-golang.sh | bash

# 
export PATH="/usr/local/go/bin:$PATH"
source /etc/profile.d/golang_path.sh

# 
if ! command -v go &> /dev/null; then
    echo "[] Failed to install Go"
    exit 1
fi

echo "[] Go version: $(go version)"

# 
echo "[🧳] Creating virtual environment..."
python3 -m venv scantex-env
source scantex-env/bin/activate

# 
echo "[] Updating pip..."
pip install --upgrade pip >/dev/null

# 
echo "[] Installing Python packages..."
pip install requests urllib3 colorama >/dev/null

# 
if ! command -v subfinder &> /dev/null; then
    echo "[] Installing SubFinder..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
fi

# 
if ! command -v httpx &> /dev/null; then
    echo "[📡] Installing httpx..."
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
fi

# 
if ! command -v subfinder &> /dev/null || ! command -v httpx &> /dev/null; then
    echo "[] Failed to install tools. Check Go setup."
    exit 1
fi

echo "[] All dependencies installed."

# 
if [ ! -f "scantex.py" ]; then
    echo "[] scantex.py not found! Place it in this folder."
    exit 1
fi

chmod +x scantex.py

# 
echo "=============================================="
echo " SCANTEX setup done!"
echo ""
echo "To run:"
echo " source scantex-env/bin/activate"
echo " ./scantex.py"
echo "=============================================="
