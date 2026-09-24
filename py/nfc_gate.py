import os
import hashlib
import hmac
import time

class TrustNFCGate:
    def __init__(self, authorized_keys_path="secure_vault/authorized_nfc.bin"):
        self.authorized_keys_path = authorized_keys_path

    def register_authorized_token(self, token_uid: bytes):
        """Administrative function to register a new physical NFC token."""
        token_hash = hashlib.sha256(token_uid).digest()
        os.makedirs(os.path.dirname(self.authorized_keys_path), exist_ok=True)
        
        # Append or write authorized cryptographic fingerprint of the NFC tag
        with open(self.authorized_keys_path, "ab") as f:
            f.write(token_hash + b"\n")
        print("[NFC] Physical hardware token successfully registered.")

    def verify_nfc_token(self, scanned_tag_bytes: bytes) -> bool:
        """
        Polls the NFC reader, extracts the hardware tag payload/UID, 
        and verifies it against the secure local whitelist.
        """
        print("[NFC] Awaiting physical hardware token tap...")
        
        if not os.path.exists(self.authorized_keys_path):
            print("[NFC] ERROR: No authorized NFC keys registered in secure vault. Initializing lockdown.")
            return False

        # Generate cryptographic fingerprint of the scanned tag
        scanned_hash = hashlib.sha256(scanned_tag_bytes).digest()

        try:
            with open(self.authorized_keys_path, "rb") as f:
                authorized_records = f.read().splitlines()

            # Constant-time comparison against all authorized tokens to prevent timing attacks
            for record in authorized_records:
                if hmac.compare_digest(scanned_hash, record):
                    print("[NFC] Physical hardware token verified. Key match confirmed.")
                    return True

            print("[NFC] ACCESS DENIED: Unrecognized physical hardware token.")
            return False

        except Exception as e:
            print(f"[NFC] Hardware reader exception: {e}")
            return False
