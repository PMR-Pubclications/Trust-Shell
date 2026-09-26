#!/bin/bash
set -e

echo "=== [1/5] Updating system and installing dependencies ==="
sudo apt-get update -y
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    zip \
    unzip \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    libffi-dev \
    libssl-dev \
    openjdk-17-jdk \
    ant \
    gradle

echo "=== [2/5] Installing Buildozer and Cython ==="
pip3 install --user --upgrade buildozer cython

# Ensure user local bin is in PATH
export PATH="$HOME/.local/bin:$PATH"

echo "=== [3/5] Creating project workspace & main.py ==="
mkdir -p miner_app
cd miner_app

# Write the daemon and an entrypoint loop to main.py
cat << 'EOF' > main.py
import os
import time
import socket
import ssl
import threading
import json
import logging
from urllib.parse import urlparse

# Configure isolated internal logging for the miner daemon
logging.basicConfig(level=logging.INFO, format='[MINER_DAEMON] %(asctime)s - %(levelname)s - %(message)s')

class TrustMiningDaemon:
    def __init__(self, account_name="m1ph0n3", worker="mobile1", password="Zxcvbnm#asd12"):
        self.worker_id = f"{account_name}.{worker}"
        self.password = password
        self.pool_endpoints = [
            "stratum+tcp://btc.f2pool.com:1314",
            "stratum+tcp://btc.f2pool.com:25",
            "stratum+tcp://btc.f2pool.com:3333",
            "stratum+ssl://btcssl.f2pool.com:1300",
            "stratum+ssl://btcssl.f2pool.com:1301"
        ]
        self.current_endpoint_index = 0
        self.running = False
        self.socket_connection = None
        self._thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._connection_loop, daemon=True)
        self._thread.start()
        logging.info(f"Background mining thread initialized for worker: {self.worker_id}")

    def _parse_pool_url(self, url_string):
        parsed = urlparse(url_string)
        scheme = parsed.scheme.lower()
        host = parsed.hostname
        port = parsed.port
        if "ssl" in scheme:
            port = port or 1300
        else:
            port = port or 3333
        return scheme, host, port

    def _connection_loop(self):
        while self.running:
            target_url = self.pool_endpoints[self.current_endpoint_index]
            scheme, host, port = self._parse_pool_url(target_url)
            try:
                logging.info(f"Connecting to target pool -> {host}:{port} ({scheme})...")
                base_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                base_sock.settimeout(30)
                base_sock.connect((host, port))
                
                if "ssl" in scheme:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    self.socket_connection = context.wrap_socket(base_sock)
                else:
                    self.socket_connection = base_sock

                auth_message = {
                    "id": 1,
                    "method": "mining.authorize",
                    "params": [self.worker_id, self.password]
                }
                self.socket_connection.sendall((json.dumps(auth_message) + "\n").encode('utf-8'))
                logging.info(f"Authorization packet sent to {host}.")

                self.socket_connection.settimeout(60)
                while self.running:
                    try:
                        response_data = self.socket_connection.recv(4096)
                        if not response_data:
                            break
                        lines = response_data.decode('utf-8', errors='ignore').split('\n')
                        for line in lines:
                            if line.strip():
                                message = json.loads(line)
                                if "method" in message and message["method"] == "mining.notify":
                                    logging.debug("New job target received.")
                    except socket.timeout:
                        keepalive = json.dumps({"id": 2, "method": "mining.extranonce.subscribe", "params": []}) + "\n"
                        self.socket_connection.sendall(keepalive.encode('utf-8'))
            except Exception as e:
                logging.error(f"Network error on {target_url}: {e}. Rotating pool...")
                self._close_socket()
                self.current_endpoint_index = (self.current_endpoint_index + 1) % len(self.pool_endpoints)
                time.sleep(15)

    def _close_socket(self):
        if self.socket_connection:
            try:
                self.socket_connection.close()
            except Exception:
                pass
            self.socket_connection = None

    def stop(self):
        self.running = False
        self._close_socket()

if __name__ == '__main__':
    daemon = TrustMiningDaemon()
    daemon.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()
EOF

echo "=== [4/5] Initializing and configuring Buildozer spec ==="
if [ ! -f "buildozer.spec" ]; then
    buildozer init
fi

# Adjust buildozer.spec parameters for background execution & network access
sed -i 's/^# title =.*/title = TrustMiner/' buildozer.spec
sed -i 's/^# package.name =.*/package.name = trustminer/' buildozer.spec
sed -i 's/^# package.domain =.*/package.domain = org.m1ph0n3/' buildozer.spec
sed -i 's/^# requirements =.*/requirements = python3,requests,urllib3/' buildozer.spec
sed -i 's/^# android.permissions =.*/android.permissions = INTERNET,ACCESS_NETWORK_STATE/' buildozer.spec
sed -i 's/^# orientation =.*/orientation = portrait/' buildozer.spec

echo "=== [5/5] Compiling APK (This may take 10-20 minutes on the first run) ==="
buildozer -v android debug

echo "=== Build Complete! Check the 'bin/' folder for your APK. ==="
ls -lah bin/
