#!/usr/bin/env python3
"""
/opt/annonos/core/security/handshake_enforcer.py
AnnonOS Application Gatekeeper & Handshake Enforcer.
Intercepts all application installation and execution requests. Automatically authorizes 
official signed modules (such as Trust-Shell) while instantly rejecting unauthorized 
binaries missing a valid hardware-rooted cryptographic handshake.
"""

import os
import sys
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional

# Add ledger path to log security violations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../chain_of_custody")))
from merkle_builder import MerkleLedger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [AnnonOS-Gatekeeper]: %(message)s'
)
logger = logging.getLogger(__name__)

class AnnonOSAppGatekeeper:
    def __init__(self, ledger_db_path: str = "/opt/annonos/data/ledger.db"):
        self.ledger = MerkleLedger(db_path=ledger_db_path)
        
        # Hardcoded authorized cryptographic public identity for Trust-Shell
        # In production, this matches the hardware root-of-trust certificate authority
        self.AUTHORIZED_APPS = {
            "Trust-Shell": {
                "expected_publisher_id": "ANNONOS_OFFICIAL_TRUST_ROOT_2026",
            }
        }

    @staticmethod
    def _shared_secret() -> Optional[bytes]:
        secret = os.environ.get("REPO_SHARED_SECRET")
        return secret.encode("utf-8") if secret else None

    def _expected_token(self, app_name: str, publisher_id: str, binary_path: str) -> Optional[str]:
        secret = self._shared_secret()
        if secret is None:
            return None
        message = f"{app_name}:{publisher_id}:{binary_path}".encode("utf-8")
        return hmac.new(secret, message, hashlib.sha256).hexdigest()

    def verify_and_authorize_app(self, app_name: str, publisher_id: str, handshake_token: str, binary_path: str) -> bool:
        """
        Validates an incoming application's handshake token against the hardware root-of-trust.
        Rejects any application that fails verification or is not explicitly recognized (like Trust-Shell).
        """
        logger.info(f"Intercepted installation request for application: [{app_name}]")

        # Check 1: Is the application recognized in the sovereign whitelist?
        if app_name not in self.AUTHORIZED_APPS:
            reason = f"Unauthorized application '{app_name}' rejected. Not recognized by AnnonOS registry."
            self._reject_and_log(app_name, binary_path, reason)
            return False

        app_profile = self.AUTHORIZED_APPS[app_name]

        # Check 2: Verify publisher identity cryptographic signature
        if publisher_id != app_profile["expected_publisher_id"]:
            reason = f"Cryptographic publisher mismatch for '{app_name}'. Expected root identity, got '{publisher_id}'."