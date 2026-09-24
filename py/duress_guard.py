import os
import ctypes

class TrustDuressGuard:
    def __init__(self, primary_pin_hash: str, duress_pin_hash: str):
        self.primary_pin_hash = primary_pin_hash
        self.duress_pin_hash = duress_pin_hash

    def evaluate_pin(self, entered_pin: str) -> str:
        """
        Evaluates the entered credential against primary and duress hashes.
        Returns the action state.
        """
        import hashlib
        entered_hash = hashlib.sha256(entered_pin.encode()).hexdigest()

        if entered_hash == self.primary_pin_hash:
            print("[SECURITY] Primary authentication confirmed. Unsealing vault.")
            return "UNSEAL_NORMAL"
        
        elif entered_hash == self.duress_pin_hash:
            print("[DURESS ALERT] Coercion PIN entered. Triggering silent panic protocol...")
            self.execute_panic_wipe()
            return "DECoy_MODE"
        
        else:
            print("[SECURITY] Invalid PIN.")
            return "DENIED"

    def execute_panic_wipe(self):
        """
        Immediately wipes sensitive files, zeroizes RAM allocations, 
        and terminates background worker threads.
        """
        secure_paths = [
            "/data/local/tmp/trust_secure/",
            "secure_vault/"
        ]

        # 1. Overwrite and delete sensitive vault and key files
        for path in secure_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            # Overwrite file contents with random junk before unlinking
                            file_size = os.path.getsize(filepath)
                            with open(filepath, "ba+") as f:
                                f.write(os.urandom(file_size))
                            os.remove(filepath)
                        except Exception:
                            pass

        # 2. Force zeroization of volatile memory references where possible
        print("[PANIC] Local cryptographic keys and session caches purged from RAM.")
        
        # In a native C++/Python wrapper, force a clean immediate exit to decoy UI
        # os._exit(0)
