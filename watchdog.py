#!/usr/init/env python3
import time
import urllib.request
import json
import sys

THRESHOLD_PERCENT = 85
# Points to your live server endpoint where Repository 2's webhook/listener is hosted
TEARDOWN_WEBHOOK = "http://127.0.0.1:8080/trust-teardown"
LOG_FILE = "/var/log/trustfence_memory.log"

def get_memory_usage():
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = {line.split(':')[0].strip(): int(line.split(':')[1].split()[0]) for line in f if ':' in line}
        total = meminfo.get('MemTotal', 0)
        available = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
        return 0.0 if total == 0 else ((total - available) / total) * 100
    except Exception:
        return 0.0

def main():
    print("Trustfence Cloud Watchdog Initialized.")
    while True:
        try:
            usage = get_memory_usage()
            if usage >= THRESHOLD_PERCENT:
                print(f"Critical memory threshold reached: {usage:.1f}%")
                
                # Send HTTP POST handshake to trigger teardown remotely
                data = json.dumps({"trigger": "EMERGENCY_RAM_PRESSURE"}).encode('utf-8')
                req = urllib.request.Request(TEARDOWN_WEBHOOK, data=data, headers={'Content-Type': 'application/json'})
                
                try:
                    urllib.request.urlopen(req, timeout=5)
                except Exception as e:
                    print(f"Webhook trigger failed: {e}")
                
                time.sleep(30)
        except Exception:
            pass
        time.sleep(5)

if __name__ == "__main__":
    main()
