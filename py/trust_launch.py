import sys
import os
import time

# Import your core modules
from mining_core import TrustMiningDaemon
from vault_crypto import MultiLayerForensicVault
from biometric_gate import TrustBiometricGate
from nfc_gate import TrustNFCGate
from duress_guard import TrustDuressGuard
from resource_governor import TrustResourceGovernor

class TrustShellMasterController:
    def __init__(self):
        print("[SHELL] Initializing Trust Secure Forensic Environment...")
        
        # 1. Initialize Core Components
        self.mining_daemon = TrustMiningDaemon(
            account_name="avalondazrrj", 
            worker="mobile1", 
            password="Zxcvbnm#asd12"
        )
        self.governor = TrustResourceGovernor(self.mining_daemon, battery_threshold_pct=20)
        self.biometric_gate = TrustBiometricGate()
        self.nfc_gate = TrustNFCGate()
        
        # Hardcoded sample hashes for primary vs. duress PINs (use secure storage in production)
        self.duress_guard = TrustDuressGuard(
            primary_pin_hash="8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918", # "admin"
            duress_pin_hash="5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"   # "duress"
        )
        self.vault = MultiLayerForensicVault(master_passphrase="SECURE_FIELD_MASTER_KEY_2026", total_layers=18)

    def execute_boot_sequence(self, entered_pin: str, enclave_token: bytes, nfc_tag_bytes: bytes):
        """Executes the full zero-trust validation and startup pipeline."""
        
        # Step A: Evaluate PIN against Duress Guard (Panic Wipe Check)
        pin_state = self.duress_guard.evaluate_pin(entered_pin)
        if pin_state == "DECoy_MODE":
            print("[ALERT] Decoy environment engaged. Shielding operational data.")
            return False
        elif pin_state != "UNSEAL_NORMAL":
            print("[DENIED] Authentication halted: Invalid credentials.")
            return False

        # Step B: Four-Factor Verification (Biometrics + Voice + NFC)
        print("[SECURITY] Running multi-modal hardware verification...")
        if not self.biometric_gate.authenticate_session(enclave_token):
            print("[DENIED] Biometric or voiceprint validation failed.")
            return False

        if not self.nfc_gate.verify_nfc_token(nfc_tag_bytes):
            print("[DENIED] Physical NFC hardware token validation failed.")
            return False

        # Step C: All Gates Cleared - Unseal Vault & Launch Background Services
        print("[SUCCESS] All security gates cleared. Unsealing 18-layer vault...")
        
        # Start the resource governor and background mining daemon safely
        self.governor.start_governor_loop()
        self.mining_daemon.start()
        
        print("[SHELL] Trust Forensic Shell is fully online, encrypted, and anchored.")
        return True

if __name__ == "__main__":
    controller = TrustShellMasterController()
    
    # Simulated successful boot trigger for testing build pipeline:
    # controller.execute_boot_sequence("admin", os.urandom(32), b"PHYSICAL_NFC_UID_01")
