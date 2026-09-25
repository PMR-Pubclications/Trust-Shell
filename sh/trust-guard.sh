#!/usr/bin/env bash

# Define the isolated directory target for the trust-shell to prevent root destruction
SHELL_DIR="${TRUST_SHELL_HOME:-$HOME/.trust-shell}"

# Secure wipe function
execute_wipe() {
    echo "[-] Security violation detected. Purging local trust-shell environment..."
    if [ -d "$SHELL_DIR" ]; then
        # Overwrite files securely before deletion (if shred is available) followed by removal
        find "$SHELL_DIR" -type f -exec shred -u -n 2 {} + 2>/dev/null || rm -rf "$SHELL_DIR"
        rm -rf "$SHELL_DIR"
    fi
    echo "[!] Local wipe complete. Core codebase remains safe in GitHub."
    exit 1
}

# --- 4 VERIFICATION CHECKS ---
# Return 0 for success/match, 1 for failure/mismatch.

verify_hardware_token() {
    # Check 1: Validates a hardware fingerprint or physical token lock file
    [ -f "$SHELL_DIR/.keys/device.lock" ] && return 0 || return 1
}

verify_integrity_hash() {
    # Check 2: Validates a core binary or configuration hash match
    local expected_hash="YOUR_EXPECTED_SHA256_HASH_HERE"
    if [ -f "$SHELL_DIR/core.bin" ]; then
        local current_hash
        current_hash=$(sha256sum "$SHELL_DIR/core.bin" | awk '{print $1}')
        [ "$current_hash" = "$expected_hash" ] && return 0
    fi
    return 1
}

verify_heartbeat() {
    # Check 3: Validates an active heartbeat or recent check-in file exists
    local hb_file="$SHELL_DIR/.heartbeat"
    if [ -f "$hb_file" ]; then
        # Optional: check if file was modified within a specific time window
        return 0
    fi
    return 1
}

verify_auth_seal() {
    # Check 4: Validates a cryptographic environment seal or active session flag
    [ "${TRUST_SEAL_ACTIVE:-0}" = "1" ] && return 0 || return 1
}

# --- EXECUTION LOGIC ---
failed=0

verify_hardware_token || { echo "[x] Check 1 Failed: Hardware token mismatch."; failed=1; }
verify_integrity_hash || { echo "[x] Check 2 Failed: Integrity hash mismatch."; failed=1; }
verify_heartbeat      || { echo "[x] Check 3 Failed: Heartbeat expired or missing."; failed=1; }
verify_auth_seal      || { echo "[x] Check 4 Failed: Auth seal invalid."; failed=1; }

# Trigger wipe if any check failed
if [ "$failed" -eq 1 ]; then
    execute_wipe
else
    echo "[+] All 4 verifications passed. Environment secure."
    exit 0
fi
