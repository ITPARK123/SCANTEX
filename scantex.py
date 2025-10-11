#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  █████████    █████████    █████████   ██████   █████ ███████████ ██████████ █████ █████
 ███▒▒▒▒▒███  ███▒▒▒▒▒███  ███▒▒▒▒▒███ ▒▒██████ ▒▒███ ▒█▒▒▒███▒▒▒█▒▒███▒▒▒▒▒█▒▒███ ▒▒███ 
▒███    ▒▒▒  ███     ▒▒▒  ▒███    ▒███  ▒███▒███ ▒███ ▒   ▒███  ▒  ▒███  █ ▒  ▒▒███ ███  
▒▒█████████ ▒███          ▒███████████  ▒███▒▒███▒███     ▒███     ▒██████     ▒▒█████   
 ▒▒▒▒▒▒▒▒███▒███          ▒███▒▒▒▒▒███  ▒███ ▒▒██████     ▒███     ▒███▒▒█      ███▒███  
 ███    ▒███▒▒███     ███ ▒███    ▒███  ▒███  ▒▒█████     ▒███     ▒███ ▒   █  ███ ▒▒███ 
▒▒█████████  ▒▒█████████  █████   █████ █████  ▒▒█████    █████    ██████████ █████ █████
 ▒▒▒▒▒▒▒▒▒    ▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒   ▒▒▒▒▒ ▒▒▒▒▒    ▒▒▒▒▒    ▒▒▒▒▒    ▒▒▒▒▒▒▒▒▒▒ ▒▒▒▒▒ ▒▒▒▒▒

 [💀 SCANTEX v2.9.3 - Terminal Edition]
 github.com/itpark/scantex
"""

import urllib3
import requests
import json
import os
import subprocess
import time
import csv
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from colorama import Fore, Style, init
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# ========================
# FILES & DIRS
# ========================
CONFIG_FILE = "config.json"
SCANNED_FILE = "scanned.json"
PROXY_FILE = "proxy.json"
TARGETS_FILE = "target.txt"
OUTPUT_DIR = "Target"
LOG_DIR = "logs"
HTTPX_PATH = "~/go/bin/httpx"

Path(LOG_DIR).mkdir(exist_ok=True)
Path(OUTPUT_DIR).mkdir(exist_ok=True)

def load_config():
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_proxy():
    if Path(PROXY_FILE).exists():
        with open(PROXY_FILE) as f:
            return json.load(f)
    return {"enabled": False}

def save_proxy(proxy_config):
    with open(PROXY_FILE, "w") as f:
        json.dump(proxy_config, f, indent=2)

def load_scanned():
    if Path(SCANNED_FILE).exists():
        with open(SCANNED_FILE) as f:
            data = json.load(f)
            return set(data.get("scanned", []))
    return set()

def save_scanned(scanned):
    with open(SCANNED_FILE, "w") as f:
        json.dump({"scanned": list(scanned)}, f, indent=2)

def setup_proxy():
    print("[⚙] Proxy setup...")
    use_proxy = input("Use proxy? (y/N): ").strip().lower() == "y"
    if not use_proxy:
        save_proxy({"enabled": False})
        print("[✔] Proxy disabled")
        return

    address = input("Proxy IP (127.0.0.1): ").strip() or "127.0.0.1"
    port = input("Port (8080): ").strip() or "8080"
    protocol = input("Protocol (http/https) [http]: ").strip() or "http"
    use_auth = input("Auth required? (y/N): ").strip().lower() == "y"
    username = ""
    password = ""
    if use_auth:
        username = input("Username: ").strip()
        password = input("Password: ").strip()

    proxy = {
        "enabled": True,
        "address": address,
        "port": int(port),
        "protocol": protocol
    }
    if use_auth:
        proxy["username"] = username
        proxy["password"] = password

    save_proxy(proxy)
    print("[✔] Proxy saved")

def setup_config():
    print("[⚙] Acunetix setup...")
    ip = input("Acunetix IP: ").strip()
    port = input("Port [3443]: ").strip() or "3443"
    api_key = input("API key: ").strip()

    print("\nScan profile:")
    print("[1] Full Scan")
    print("[2] High Risk Only")
    print("[3] SQL Injection")
    print("[4] XSS Only")
    print("[5] Crawl Only")
    print("[0] Back")

    choice = input("Choose (0–5): ").strip()
    if choice == "0": return

    profiles = {
        "1": ("Full Scan", "11111111-1111-1111-1111-111111111111"),
        "2": ("High Risk Only", "11111111-1111-1111-1111-111111111112"),
        "3": ("SQL Injection", "11111111-1111-1111-1111-111111111114"),
        "4": ("XSS Only", "11111111-1111-1111-1111-111111111113"),
        "5": ("Crawl Only", "11111111-1111-1111-1111-111111111115"),
    }

    name, pid = profiles.get(choice, profiles["1"])

    delay = input("Delay between domains (hours) [1]: ").strip() or "1"
    delay = int(delay)

    config = {
        "acunetix_ip": ip,
        "acunetix_port": port,
        "api_key": api_key,
        "profile_id": pid,
        "profile_name": name,
        "delay_hours": delay
    }

    save_config(config)
    print(f"[✔] Config saved: {name} | Delay: {delay}h")

# ========================
# ACUNETIX API
# ========================
def get_api_config():
    c = load_config()
    if not c:
        print("[✘] Config not found. Run --setup")
        exit(1)
    return c

def get_headers():
    config = get_api_config()
    return {
        "X-Auth": config["api_key"],
        "Content-Type": "application/json"
    }

def get_acunetix_url():
    config = get_api_config()
    return f"https://{config['acunetix_ip']}:{config['acunetix_port']}"

def target_exists(url):
    try:
        res = requests.get(
            f"{get_acunetix_url()}/api/v1/targets?q={url}",
            headers=get_headers(),
            verify=False,
            timeout=10
        )
        if res.status_code == 200:
            targets = res.json().get("targets", [])
            return len(targets) > 0
    except:
        pass
    return False

# ========================
# LOGGING
# ========================
def log_write(log_path, msg, color=None):
    timestamp = time.strftime('%H:%M:%S')
    color = color or ""
    reset = Style.RESET_ALL
    formatted = f"[{timestamp}] {color}{msg}{reset}"
    print(formatted)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

def append_csv(csv_path, data):
    file_exists = csv_path.exists()
    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "url", "target_id", "scan_id", "status"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def generate_html_report(html_path, domain, urls_count, start_time, end_time):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>SCANTEX Report</title>
    </head>
    <body>
        <h1>SCANTEX Report</h1>
        <p><b>Domain:</b> {domain}</p>
        <p><b>Targets:</b> {urls_count}</p>
        <p><b>Start:</b> {start_time}</p>
        <p><b>Finish:</b> {end_time}</p>
    </body>
    </html>
    """
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

# ========================
# SCAN LOGIC
# ========================
def create_target(url, description, log_path):
    if target_exists(url):
        log_write(log_path, f"[🔁] Skipped (already exists): {url}")
        return None

    proxy = load_proxy()
    payload = {
        "address": url,
        "description": description,
        "proxy": proxy
    }
    res = requests.post(f"{get_acunetix_url()}/api/v1/targets", headers=get_headers(), json=payload, verify=False)
    if res.status_code == 201:
        target_id = res.json()["target_id"]
        log_write(log_path, f"[📡] Target created: {url} → {target_id}")
        return target_id
    else:
        log_write(log_path, f"[✘] Create failed {url}: {res.status_code}")
        return None

def start_scan(target_id, log_path):
    config = get_api_config()
    profile_id = config["profile_id"]
    payload = {
        "target_id": target_id,
        "profile_id": profile_id,
        "schedule": {"disable": False}
    }
    res = requests.post(f"{get_acunetix_url()}/api/v1/scans", headers=get_headers(), json=payload, verify=False)
    if res.status_code == 201:
        scan_id = res.headers.get("Location", "").split("/")[-1]
        log_write(log_path, f"[⚡] Scan started: {scan_id} for {target_id}")
        return scan_id
    elif res.status_code == 409:
        log_write(log_path, f"[🔁] Scan already running: {target_id}")
        return None
    else:
        log_write(log_path, f"[✘] Scan failed: {res.status_code} @ {target_id}")
        return None

def process_domain(domain):
    domain_dir = Path(OUTPUT_DIR) / domain
    domain_dir.mkdir(exist_ok=True)

    sub_out = domain_dir / "sub.txt"
    checked_out = domain_dir / "checked.txt"
    log_path = domain_dir / f"{domain}.log"
    csv_path = domain_dir / "results.csv"
    html_path = domain_dir / "report.html"

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_write(log_path, "=" * 50)
    log_write(log_path, f"[🏁] Starting: {domain}")
    log_write(log_path, "=" * 50)

    if not sub_out.exists() or sub_out.stat().st_size == 0:
        log_write(log_path, "[🔍] Discovering subdomains...")
        subprocess.run(f"subfinder -d {domain} -o {sub_out}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not checked_out.exists() or checked_out.stat().st_size == 0:
        log_write(log_path, "[📡] Checking live hosts...")
        subprocess.run(f"cat {sub_out} | {HTTPX_PATH} -silent -status-code -o {checked_out}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not Path(checked_out).exists():
        log_write(log_path, "[⚠] checked.txt not found!")
        return

    seen = set()
    urls = []
    with open(checked_out, encoding="utf-8") as f:
        for line in f:
            url = line.strip().split()[0]
            if url.startswith("http") and url not in seen:
                seen.add(url)
                urls.append(url)

    log_write(log_path, f"[📂] Found {len(urls)} URLs")

    for url in urls:
        target_id = create_target(url, domain, log_path)
        if target_id:
            scan_id = start_scan(target_id, log_path)
            append_csv(csv_path, {
                "domain": domain,
                "url": url,
                "target_id": target_id,
                "scan_id": scan_id or "skipped",
                "status": "started" if scan_id else "skipped"
            })

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    generate_html_report(html_path, domain, len(urls), start_time, end_time)
    log_write(log_path, "=" * 50)
    log_write(log_path, f"[🏁] Done: {domain}")
    log_write(log_path, "=" * 50)

# ========================
# CLI
# ========================
def cli():
    parser = argparse.ArgumentParser(description="SCANTEX v2.9.3")
    parser.add_argument("--setup", action="store_true", help="Setup connection")
    parser.add_argument("--run", action="store_true", help="Run scan")
    parser.add_argument("--clean", action="store_true", help="Clear scan data")
    parser.add_argument("--target", type=str, help="Scan one domain")
    return parser.parse_args()

# ========================
# MENU
# ========================
def print_banner():
    banner = r"""
  █████████    █████████    █████████   ██████   █████ ███████████ ██████████ █████ █████
 ███▒▒▒▒▒███  ███▒▒▒▒▒███  ███▒▒▒▒▒███ ▒▒██████ ▒▒███ ▒█▒▒▒███▒▒▒█▒▒███▒▒▒▒▒█▒▒███ ▒▒███ 
▒███    ▒▒▒  ███     ▒▒▒  ▒███    ▒███  ▒███▒███ ▒███ ▒   ▒███  ▒  ▒███  █ ▒  ▒▒███ ███  
▒▒█████████ ▒███          ▒███████████  ▒███▒▒███▒███     ▒███     ▒██████     ▒▒█████   
 ▒▒▒▒▒▒▒▒███▒███          ▒███▒▒▒▒▒███  ▒███ ▒▒██████     ▒███     ▒███▒▒█      ███▒███  
 ███    ▒███▒▒███     ███ ▒███    ▒███  ▒███  ▒▒█████     ▒███     ▒███ ▒   █  ███ ▒▒███ 
▒▒█████████  ▒▒█████████  █████   █████ █████  ▒▒█████    █████    ██████████ █████ █████
 ▒▒▒▒▒▒▒▒▒    ▒▒▒▒▒▒▒▒▒  ▒▒▒▒▒   ▒▒▒▒▒ ▒▒▒▒▒    ▒▒▒▒▒    ▒▒▒▒▒    ▒▒▒▒▒▒▒▒▒▒ ▒▒▒▒▒ ▒▒▒▒▒

 [💀 SCANTEX v2.9.3 - Terminal Edition]
 github.com/itpark/scantex
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)

def main_menu():
    while True:
        print("\n[💀] SCANTEX v2.9.3")
        print("[1] Start scan")
        print("[2] Setup Acunetix")
        print("[3] Show config")
        print("[4] Show scanned domains")
        print("[5] Clean output")
        print("[6] Setup proxy")
        print("[0] Exit")

        choice = input("\nSelect: ").strip()

        if choice == "0":
            print("[👋] Goodbye!")
            break
        elif choice == "1":
            if not Path(TARGETS_FILE).exists():
                print("[⚠] target.txt not found.")
                continue
            with open(TARGETS_FILE, encoding="utf-8") as f:
                domains = [line.strip() for line in f if line.strip()]
            if not domains:
                print("[⚠] target.txt is empty")
                continue
            scanned = load_scanned()
            config = get_api_config()
            delay = config["delay_hours"]

            for i, domain in enumerate(domains, 1):
                if domain in scanned:
                    print(f"[🔁] Skipped: {domain}")
                    continue

                print(f"\n[{i}/{len(domains)}] Scanning: {domain}")
                process_domain(domain)
                scanned.add(domain)
                save_scanned(scanned)

                if i < len(domains):
                    print(f"[⏳] Waiting {delay} hour(s)...")
                    future = datetime.now() + timedelta(hours=delay)
                    while datetime.now() < future:
                        time.sleep(10)
            print("\n[✔] All domains scanned!")
        elif choice == "2":
            setup_config()
        elif choice == "3":
            c = load_config()
            if c:
                print(json.dumps(c, indent=2, ensure_ascii=False))
            else:
                print("[⚠] No config found")
        elif choice == "4":
            scanned = load_scanned()
            if not scanned:
                print("[⚠] No scanned domains.")
            else:
                print("\nScanned domains:")
                for d in sorted(scanned):
                    print(" -", d)
        elif choice == "5":
            from shutil import rmtree
            dirs = [d for d in Path(OUTPUT_DIR).iterdir() if d.is_dir()]
            for d in dirs:
                rmtree(d)
            print("[🗑] Output cleaned")
        elif choice == "6":
            setup_proxy()
        else:
            print("[⚠] Invalid option")

# ========================
# ENTRY
# ========================
def main():
    args = cli()

    if args.setup:
        setup_config()
        return
    elif args.clean:
        from shutil import rmtree
        dirs = [d for d in Path(OUTPUT_DIR).iterdir() if d.is_dir()]
        for d in dirs:
            rmtree(d)
        print("[🗑] Output cleaned")
        return
    elif args.target:
        scanned = load_scanned()
        if args.target in scanned:
            print(f"[🔁] Skipped: {args.target}")
            return
        process_domain(args.target)
        scanned.add(args.target)
        save_scanned(scanned)
        return
    elif args.run:
        if not Path(TARGETS_FILE).exists():
            print("[⚠] target.txt not found.")
            return
        with open(TARGETS_FILE, encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
        if not domains:
            print("[⚠] target.txt is empty")
            return
        scanned = load_scanned()
        config = get_api_config()
        delay = config["delay_hours"]

        for i, domain in enumerate(domains, 1):
            if domain in scanned:
                print(f"[🔁] Skipped: {domain}")
                continue

            print(f"\n[{i}/{len(domains)}] Scanning: {domain}")
            process_domain(domain)
            scanned.add(domain)
            save_scanned(scanned)

            if i < len(domains):
                print(f"[⏳] Waiting {delay} hour(s)...")
                future = datetime.now() + timedelta(hours=delay)
                while datetime.now() < future:
                    time.sleep(10)
        print("\n[✔] All domains scanned!")
        return

    print_banner()
    main_menu()

if __name__ == "__main__":
    main()
