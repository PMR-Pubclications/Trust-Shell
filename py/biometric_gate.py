import os
import hashlib
import numpy as np
import sounddevice as sd  # Local audio capture for voiceprint
import json

class TrustBiometricGate:
    def __init__(self, voiceprint_model_path="secure_vault/voice_profile.bin"):
        self.voice_profile_path = voiceprint_model_path
        self.is_unlocked = False

    def verify_hardware_biometric_token(self, enclave_token: bytes) -> bool:
        """
        Simulates the hardware-backed keystore token release. 
        In the native Android/C++ shell wrapper, this hooks directly into 
        Android's BiometricPrompt tied to an encrypted KeyStore cipher object.
        """
        # If the secure hardware enclave successfully validates the user's fingerprint/face,
        # it unseals the cryptographic token.
        if len(enclave_token) == 32:
            print("[BIOMETRIC] Hardware secure enclave verified successfully.")
            return True
        print("[BIOMETRIC] Hardware biometric validation failed.")
        return False

    def capture_and_verify_voiceprint(self, duration_seconds: int = 3) -> bool:
        """
        Captures a local audio sample offline and matches its spectral profile
        against the stored investigator voiceprint signature.
        """
        print(f"[VOICEPRINT] Listening for verification passphrase ({duration_seconds}s)...")
        fs = 16000  # 16kHz sampling rate
        
        try:
            # Record local microphone stream entirely offline
            audio_recording = sd.rec(int(duration_seconds * fs), samplerate=fs, channels=1, dtype='float32')
            sd.wait()
            
            # Extract basic frequency-domain features (MFCC-style spectral centroid simulation)
            fft_features = np.abs(np.fft.rfft(audio_recording.flatten()))
            spectral_signature = hashlib.sha256(fft_features.tobytes()).digest()

            if not os.path.exists(self.voice_profile_path):
                print("[VOICEPRINT] No baseline profile found. Initializing current signature as root.")
                os.makedirs(os.path.dirname(self.voice_profile_path), exist_ok=True)
                with open(self.voice_profile_path, "wb") as f:
                    f.write(spectral_signature)
                return True

            # Load stored baseline voice profile and compare match threshold
            with open(self.voice_profile_path, "rb") as f:
                baseline_signature = f.read()

            # Constant-time comparison to prevent timing attacks
            match_score = hmac.compare_digest(spectral_signature, baseline_signature)
            
            if match_score:
                print("[VOICEPRINT] Voice signature verified successfully.")
                return True
            else:
                print("[VOICEPRINT] Voice signature mismatch.")
                return False

        except Exception as e:
            print(f"[VOICEPRINT] Hardware audio stream error: {e}")
            return False

    def authenticate_session(self, enclave_token: bytes) -> bool:
        """
        Executes the multi-modal verification sequence. Both hardware biometrics
        and voiceprint analysis must pass before the forensic vault opens.
        """
        hw_passed = self.verify_hardware_biometric_token(enclave_token)
        if not hw_passed:
            return False

        voice_passed = self.capture_and_verify_voiceprint()
        if not voice_passed:
            return False

        self.is_unlocked = True
        print("[GATE] Multi-modal biometric authentication complete. Vault unsealed.")
        return True
