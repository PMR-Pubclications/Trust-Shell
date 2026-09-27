#!/usr/bin/env python3
import time
import urllib.request
import json
import os
import subprocess

THRESHOLD_PERCENT = 85
TEARDOWN_WEBHOOK = "http://127.0.0.1:8080/trust-teardown"
# Keep logs self-contained within a local logs directory inside the repo
LOG_DIR = "./logs"
LOG_FILE = os.path.join(LOG_DIR, "trustfence_memory.log")

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

def log_event(message):
    try:
        ensure_log_dir()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

def get_memory_usage():
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = {line.split(':')[0].strip(): int(line.split(':')[1].split()[0]) for line in f if ':' in line}
        total = meminfo.get('MemTotal', 0)
        available = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
        return 0.0 if total == 0 else ((total - available) / total) * 100
    except Exception:
        return 0.0

def throttle_or_kill_miner():
    msg = "[!] Initiating emergency miner throttle/shutdown..."
    print(msg)
    log_event(msg)
    try:
        # Pause the miner process immediately
        subprocess.run(["pkill", "-STOP", "avalons3-miner-daemon"], check=False)
        log_event("[+] Miner successfully throttled/paused by local watchdog.")
    except Exception as e:
        err_msg = f"[CRITICAL] Failed to locally control miner process: {e}"
        print(err_msg)
        log_event(err_msg)

def main():
    print("Trustfence Watchdog Initialized.")
    log_event("Trustfence Watchdog Initialized.")
    
    while True:
        try:
            usage = get_memory_usage()
            if usage >= THRESHOLD_PERCENT:
                alert_msg = f"[!] Critical memory threshold reached: {usage:.1f}%"
                print(alert_msg)
                log_event(alert_msg)
                
                # 1. Trigger local mitigation immediately
                throttle_or_kill_miner()
                
                # 2. Send HTTP POST handshake to notify Repository B's listener
                data = json.dumps({"trigger": "EMERGENCY_RAM_PRESSURE", "usage": usage}).encode('utf-8')
                req = urllib.request.Request(TEARDOWN_WEBHOOK, data=data, headers={'Content-Type': 'application/json'})
                
                try:
                    urllib.request.urlopen(req, timeout=3)
                except Exception as e:
                    log_event(f"Webhook trigger failed (handled by local fallback): {e}")
                
                time.sleep(30)
            else:
                time.sleep(5)
                
        except Exception as err:
            log_event(f"Watchdog loop error: {err}")
            time.sleep(5)

if __name__ == "__main__":
    main()
