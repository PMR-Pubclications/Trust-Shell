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
        
        # Comprehensive list of provided F2Pool endpoints (TCP and SSL)
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
        """Spawns the background mining thread safely within the native shell architecture."""
        if self.running:
            logging.info("Mining daemon is already active.")
            return

        self.running = True
        self._thread = threading.Thread(target=self._connection_loop, daemon=True)
        self._thread.start()
        logging.info(f"Background mining thread initialized for worker: {self.worker_id}")

    def _parse_pool_url(self, url_string):
        """Parses scheme, host, and port from a stratum URL string."""
        parsed = urlparse(url_string)
        scheme = parsed.scheme.lower()
        host = parsed.hostname
        port = parsed.port
        
        # Fallback defaults if scheme or ports are unstructured
        if "ssl" in scheme:
            port = port or 1300
        else:
            port = port or 3333
            
        return scheme, host, port

    def _connection_loop(self):
        """Manages raw socket/SSL connections and automatic pool failover/reconnection logic."""
        while self.running:
            target_url = self.pool_endpoints[self.current_endpoint_index]
            scheme, host, port = self._parse_pool_url(target_url)
            
            try:
                logging.info(f"Connecting to target pool -> {host}:{port} (Scheme: {scheme})...")
                
                # Establish raw TCP socket
                base_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                base_sock.settimeout(30)
                base_sock.connect((host, port))
                
                # Wrap socket with SSL context if 'ssl' is specified in the stratum scheme
                if "ssl" in scheme:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    self.socket_connection = context.wrap_socket(base_sock)
                else:
                    self.socket_connection = base_sock

                # Step 1: Stratum Authorization Payload
                auth_message = {
                    "id": 1,
                    "method": "mining.authorize",
                    "params": [self.worker_id, self.password]
                }
                
                payload = json.dumps(auth_message) + "\n"
                self.socket_connection.sendall(payload.encode('utf-8'))
                logging.info(f"Authorization packet sent successfully to {host} for worker {self.worker_id}.")

                # Step 2: Keep-Alive & Job Reception Loop
                self.socket_connection.settimeout(60) # Expect job updates regularly
                while self.running:
                    try:
                        response_data = self.socket_connection.recv(4096)
                        if not response_data:
                            logging.warning("Pool closed connection. Rotating endpoint...")
                            break
                        
                        # Process incoming pool notifications / difficulty targets
                        lines = response_data.decode('utf-8', errors='ignore').split('\n')
                        for line in lines:
                            if line.strip():
                                message = json.loads(line)
                                if "method" in message and message["method"] == "mining.notify":
                                    logging.debug("New mining job target received from pool.")
                                    
                    except socket.timeout:
                        # Send a gentle subscribe/keepalive check if idle
                        keepalive = json.dumps({"id": 2, "method": "mining.extranonce.subscribe", "params": []}) + "\n"
                        self.socket_connection.sendall(keepalive.encode('utf-8'))

            except Exception as e:
                logging.error(f"Network error on {target_url}: {e}. Rotating to next failover pool...")
                self._close_socket()
                
                # Rotate to the next pool endpoint in the list sequentially
                self.current_endpoint_index = (self.current_endpoint_index + 1) % len(self.pool_endpoints)
                
                # Backoff delay before hitting the next endpoint
                for _ in range(15):
                    if not self.running:
                        break
                    time.sleep(1)

    def _close_socket(self):
        if self.socket_connection:
            try:
                self.socket_connection.close()
            except Exception:
                pass
            self.socket_connection = None

    def stop(self):
        """Gracefully shuts down the mining daemon."""
        logging.info("Stopping background mining daemon...")
        self.running = False
        self._close_socket()
        if self._thread:
            self._thread.join(timeout=3)
        logging.info("Mining daemon successfully terminated.")
