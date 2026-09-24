import os
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class MultiLayerForensicVault:
    def __init__(self, master_passphrase: str, total_layers: int = 18):
        self.master_passphrase = master_passphrase.encode('utf-8')
        self.total_layers = max(1, total_layers)

    def _derive_layer_key(self, layer_index: int, salt: bytes) -> bytes:
        """Derives a unique, isolated cryptographic key for a specific encryption layer."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt + bytes([layer_index]),
            iterations=100_000 + (layer_index * 1000) # Escalating iteration depth per layer
        )
        return kdf.derive(self.master_passphrase)

    def encrypt_evidence_payload(self, raw_data: bytes) -> dict:
        """
        Passes the evidence through cascaded encryption layers, 
        generating randomized salts and unique nonces at each step.
        """
        current_payload = raw_data
        layer_metadata = []

        # Generate a master base salt for the session
        base_salt = os.urandom(16)
        
        # Sequentially wrap through the requested layers
        for layer in range(self.total_layers):
            # Generate unique layer salt and nonce
            layer_salt = hashlib.sha256(base_salt + bytes([layer])).digest()[:16]
            nonce = os.urandom(12)
            
            # Derive unique key for this specific layer
            layer_key = self._derive_layer_key(layer, layer_salt)
            
            # Encrypt payload using AES-GCM for authenticated encryption
            aesgcm = AESGCM(layer_key)
            # Bind layer index into associated data to prevent layer-swapping attacks
            associated_data = f"LAYER_{layer}_SECURE_VAULT".encode('utf-8')
            
            current_payload = aesgcm.encrypt(nonce, current_payload, associated_data)
            
            # Store nonces and salts required for decryption order reversal
            layer_metadata.append({
                "layer": layer,
                "nonce": nonce.hex(),
                "salt": layer_salt.hex()
            })

        return {
            "ciphertext": current_payload.hex(),
            "base_salt": base_salt.hex(),
            "layers": layer_metadata
        }

    def decrypt_evidence_payload(self, vault_package: dict) -> bytes:
        """Reverses the cascaded layers to recover the original raw evidence."""
        current_payload = bytes.fromhex(vault_package["ciphertext"])
        base_salt = bytes.fromhex(vault_package["base_salt"])
        layers = vault_package["layers"]

        # Reverse through layers from deepest back to surface
        for meta in reversed(layers):
            layer = meta["layer"]
            nonce = bytes.fromhex(meta["nonce"])
            layer_salt = bytes.fromhex(meta["salt"])

            layer_key = self._derive_layer_key(layer, layer_salt)
            aesgcm = AESGCM(layer_key)
            associated_data = f"LAYER_{layer}_SECURE_VAULT".encode('utf-8')

            current_payload = aesgcm.decrypt(nonce, current_payload, associated_data)

        return current_payload
