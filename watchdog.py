#!/usr/bin/env python3
import time
import subprocess
import sys
import os

THRESHOLD_PERCENT = 85
TEARDOWN_SCRIPT = "/opt/trustfence/bin/trust_teardown.py"
LOG_FILE = "/var/log/trustfence_memory.log"

def get_memory_usage():
    """Reads /proc/meminfo natively to calculate RAM usage percentage."""
    meminfo = {}
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                parts = line.split(':')
                if len(parts) == 2:
                    # Values are in kB by default
                    meminfo[parts[0].strip()] = int(parts[1].split()[0])
        
        total = meminfo.get('MemTotal', 0)
        available = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
        if total == 0:
            return 0.0
        
        used_percent = ((total - available) / total) * 100
        return used_percent
    except Exception:
        return 0.0

def log_message(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [WATCHDOG] {msg}\n"
    print(entry.strip())
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(entry)
    except Exception:
        pass

def main():
    log_message("Trustfence Python RAM Watchdog initialized.")
    while True:
        try:
            usage = get_memory_usage()
            if usage >= THRESHOLD_PERCENT:
                log_message(f"CRITICAL RAM PRESSURE: {usage:.1f}%. Initiating handshake trigger.")
                
                if os.path.exists(TEARDOWN_SCRIPT):
                    # Handshake execution: Call the second Python script with argument
                    subprocess.run([sys.executable, TEARDOWN_SCRIPT, "EMERGENCY_RAM_PRESSURE"], check=False)
                else:
                    log_message(f"ERROR: Teardown script missing at {TEARDOWN_SCRIPT}")
                
                # Cooldown period to prevent rapid trigger loops
                time.sleep(30)
        except Exception as e:
            log_message(f"Error in watchdog loop: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
