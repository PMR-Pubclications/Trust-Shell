import os


class TrustSecureShellRuntime:
    def __init__(self, storage_root: str = "trust_shell_data"):
        self.storage_root = storage_root
        self.running = False

    def initialize_secure_environment(self):
        """Create a private local storage directory for app data."""
        os.makedirs(self.storage_root, exist_ok=True)
        os.chmod(self.storage_root, 0o700)
        print("[SHELL] Secure local storage initialized.")

    def create_session_snapshot(self, title: str, payload: dict) -> dict:
        """Save an offline browser or vault snapshot to disk."""
        self.running = True
        session_file = os.path.join(self.storage_root, f"{title.replace(' ', '_').lower()}.json")
        with open(session_file, "w", encoding="utf-8") as handle:
            handle.write(str(payload))
        print(f"[SHELL] Snapshot saved to {session_file}.")
        return {"status": "saved", "path": session_file}

    def shutdown(self):
        self.running = False
        print("[SHELL] Secure shell terminated.")
