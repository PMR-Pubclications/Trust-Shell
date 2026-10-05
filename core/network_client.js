// Trust-Shell/core/network_client.js

// 1. Get local hardware UUID (from system info or device serial)
const HARDWARE_UUID = "DEV-8839-FLIR-001"; // Dynamically read from OS hardware
const TRUST_MAIN_URL = "https://your-trust-main-server.com/api/v1/device/handshake";

async function checkDeviceLockState() {
    try {
        console.log("[TRUST-SHELL] Initiating handshake with Trust-Main...");

        // Making this HTTP request exposes the device's IP to Trust-Main automatically
        const response = await fetch(TRUST_MAIN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hardware_uuid: HARDWARE_UUID
            })
        });

        const data = await response.json();

        if (!data.provisioned) {
            console.log("[TRUST-SHELL] Unprovisioned device. Showing initial Agency Sign-In screen.");
            // Render one-time Police/Fire/EMS setup UI
            return { locked: false };
        }

        console.log(`[TRUST-SHELL] Device locked to: ${data.agency}`);
        
        // Save the signed agency token locally
        localStorage.setItem('agency_jwt', data.token);

        // Lock UI permanently to the assigned agency
        return {
            locked: true,
            agency: data.agency // 'POLICE', 'FIRE', or 'EMS'
        };

    } catch (error) {
        console.error("[TRUST-SHELL] Offline or unable to reach Trust-Main:", error);
        // Fall back to hardware-backed local keystore for offline field operation
        return checkLocalHardwareKeystore();
    }
}

module.exports = { checkDeviceLockState };
