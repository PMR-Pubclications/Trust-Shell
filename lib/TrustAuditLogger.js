// lib/TrustAuditLogger.js

/**
 * Minimal syslog / systemd-journald audit logger.
 * Uses systemd priority prefixes (<6> = LOG_INFO, <3> = LOG_ERR) over stdout.
 */
class TrustAuditLogger {
    /**
     * Records a validated delivery receipt to systemd journald
     * @param {Object} receipt - Ephemeral server receipt object
     */
    static logDeliveryReceipt(receipt) {
        if (!receipt || !receipt.queue_id) return;

        const auditRecord = {
            event: 'AUDIT_REPORT_DELIVERED_AND_PURGED',
            queue_id: receipt.queue_id,
            server_transaction_id: receipt.server_transaction_id || 'UNKNOWN',
            received_hmac_prefix: receipt.received_hmac ? receipt.received_hmac.substring(0, 16) : 'N/A',
            server_timestamp: receipt.timestamp,
            client_logged_at: new Date().toISOString()
        };

        // Prefix <6> sets systemd log priority to LOG_INFO
        process.stdout.write(`<6>[TRUST-AUDIT] ${JSON.stringify(auditRecord)}\n`);
    }

    /**
     * Log delivery failure or receipt tampering attempt
     */
    static logDeliveryFailure(queueId, reason) {
        const failureRecord = {
            event: 'AUDIT_DELIVERY_FAILED',
            queue_id: queueId,
            reason: reason,
            client_logged_at: new Date().toISOString()
        };

        // Prefix <3> sets systemd log priority to LOG_ERR
        process.stderr.write(`<3>[TRUST-AUDIT-ERROR] ${JSON.stringify(failureRecord)}\n`);
    }
}

module.exports = TrustAuditLogger;
