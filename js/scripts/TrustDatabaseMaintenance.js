// lib/TrustDatabaseMaintenance.js
const Database = require('better-sqlite3');
const fs = require('fs');

class TrustDatabaseMaintenance {
    /**
     * @param {Database} dbInstance - Active better-sqlite3 instance
     * @param {Object} options
     * @param {number} options.journalSizeLimit - Max WAL size before auto-truncate (default 16MB)
     * @param {number} options.checkpointIntervalMs - Interval for periodic TRUNCATE checkpoints (default 30 min)
     */
    constructor(dbInstance, options = {}) {
        this.db = dbInstance;
        this.journalSizeLimit = options.journalSizeLimit || 16 * 1024 * 1024; // 16 MB
        this.checkpointIntervalMs = options.checkpointIntervalMs || 30 * 60 * 1000; // 30 mins
        this.timer = null;

        this._applyPragmas();
    }

    /**
     * Configure database storage limits at startup
     */
    _applyPragmas() {
        // Enforce maximum size for the WAL file before SQLite automatically truncates it
        this.db.pragma(`journal_size_limit = ${this.journalSizeLimit}`);
        
        // Auto-vacuum incremental mode to reclaim freed space gradually
        this.db.pragma('auto_vacuum = INCREMENTAL');
    }

    /**
     * Forces a TRUNCATE checkpoint: flushes WAL writes to main database file
     * and resets the -wal file back to 0 bytes on disk.
     */
    checkpointWal() {
        try {
            // WAL_CHECKPOINT_TRUNCATE (3): Flushes pages, waits for readers, and truncates WAL to 0 bytes
            const result = this.db.pragma('wal_checkpoint(TRUNCATE)');
            
            // result is an array: [{ busy: 0, log: 0, checkpointed: 0 }]
            if (result && result[0]) {
                const { busy, log, checkpointed } = result[0];
                if (busy === 1) {
                    console.warn('[DB MAINTENANCE] Checkpoint busy: Active transaction delayed full truncation.');
                } else {
                    console.log(`[DB MAINTENANCE] WAL truncated. Total pages in log: ${log}, checkpointed: ${checkpointed}`);
                }
            }
            
            // Reclaim empty database pages
            this.db.pragma('incremental_vacuum(100)');
        } catch (err) {
            console.error(`[DB MAINTENANCE ERROR] Checkpoint failed: ${err.message}`);
        }
    }

    /**
     * Periodic maintenance loop runner
     */
    startScheduledMaintenance() {
        if (this.timer) return;

        // Initial maintenance run on start
        this.checkpointWal();

        this.timer = setInterval(() => {
            this.checkpointWal();
        }, this.checkpointIntervalMs);

        // Allow process to exit cleanly if this timer is active
        if (this.timer.unref) {
            this.timer.unref();
        }
    }

    stopScheduledMaintenance() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
}

module.exports = TrustDatabaseMaintenance;
