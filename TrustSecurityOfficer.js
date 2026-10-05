// lib/TrustSecurityOfficer.js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');

class TrustSecurityOfficer {
    /**
     * @param {string} trustMainEmergencyEndpoint - Endpoint for high-priority tamper alerts
     * @param {string} dbPath - Path to the active SQLite database
     */
    constructor(trustMainEmergencyEndpoint, dbPath) {
        this.emergencyEndpoint = trustMainEmergencyEndpoint;
        this.dbPath = dbPath;
    }

    /**
     * Collect network and system telemetry to pinpoint the device/culprit location
     */
    async collectCulpritTelemetry() {
        const networkInterfaces = os.networkInterfaces();
        const localIps = [];

        for (const interfaceName of Object.keys(networkInterfaces)) {
            for (const iface of networkInterfaces[interfaceName]) {
                if (!iface.internal && iface.family === 'IPv4') {
                    localIps.push({ interface: interfaceName, ip: iface.address, mac: iface.mac });
                }
            }
        }

        let publicIpData = null;
        try {
            // Retrieve public IP and coarse geo-location pin
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000); // 2s timeout
            
            const res = await fetch('https://ipapi.co/json/', { signal: controller.signal });
            clearTimeout(timeoutId);
            if (res.ok) {
                publicIpData = await res.json();
            }
        } catch {
            publicIpData = { error: 'PUBLIC_IP_LOOKUP_FAILED_OR_OFFLINE' };
        }

        return {
            timestamp: new Date().toISOString(),
            hostname: os.hostname(),
            platform: os.platform(),
            arch: os.arch(),
            local_network: localIps,
            public_telemetry: publicIpData
        };
    }

    /**
     * Transmit high-priority emergency beacon to Trust-Main
     */
    async dispatchTamperBeacon(tamperedRecord, telemetry) {
        const beaconPayload = {
            event: "SECURITY_BREACH_TAMPER_DETECTED",
            severity: "CRITICAL",
            queue_id: tamperedRecord.queue_id,
            master_shift_hash: tamperedRecord.master_shift_hash,
            badge_id: tamperedRecord.badge_id,
            corrupted_hmac: tamperedRecord.hmac_signature,
            culprit_telemetry: telemetry
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3s emergency threshold

            const response = await fetch(this.emergencyEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Trust-Emergency-Alert': 'TRUE'
                },
                body: JSON.stringify(beaconPayload),
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            return response.ok;
        } catch (err) {
            console.error(`[SECURITY ALERT] Emergency beacon transmission failed: ${err.message}`);
            return false;
        }
    }

    /**
     * Overwrite SQLite file on disk with random bytes/zeroes before deletion (Secure Wipe)
     */
    secureWipeDatabase() {
        const filesToPurge = [
            this.dbPath,
            `${this.dbPath}-wal`, // Write-Ahead Log
            `${this.dbPath}-shm`  // Shared Memory file
        ];

        for (const filePath of filesToPurge) {
            if (fs.existsSync(filePath)) {
                try {
                    const stats = fs.statSync(filePath);
                    const fileSize = stats.size;

                    // Pass 1: Overwrite with zeros
                    const zeroBuffer = Buffer.alloc(fileSize, 0);
                    fs.writeFileSync(filePath, zeroBuffer);

                    // Pass 2: Overwrite with random bytes
                    const randomBuffer = crypto.randomBytes(fileSize);
                    fs.writeFileSync(filePath, randomBuffer);

                    // Unlink from filesystem
                    fs.unlinkSync(filePath);
                    console.warn(`[SECURITY PURGE] Sanitized and deleted file: ${filePath}`);
                } catch (err) {
                    console.error(`[SECURITY PURGE FAILED] Error wiping ${filePath}: ${err.message}`);
                }
            }
        }
    }

    /**
     * Execute full response sequence upon tamper detection
     */
    async handleTamperingEvent(tamperedRecord, dbConnection) {
        console.error(`[SECURITY OFFICER] Tamper detected on record ${tamperedRecord.queue_id}. Executing emergency workflow...`);

        // 1. Gather location and IP evidence
        const telemetry = await this.collectCulpritTelemetry();

        // 2. Dispatch alert beacon to Trust-Main
        await this.dispatchTamperBeacon(tamperedRecord, telemetry);

        // 3. Close SQLite handle safely before wiping disk contents
        if (dbConnection && dbConnection.open) {
            dbConnection.close();
        }

        // 4. Overwrite and zero out local database on disk
        this.secureWipeDatabase();

        // 5. Terminate process to halt unauthorized interaction
        process.exit(1);
    }
}

module.exports = TrustSecurityOfficer;
