import time
import hashlib
import json
import sqlite3
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

class AgencyType(str, Enum):
    EMS = "EMS"
    FIRE = "FIRE"
    POLICE = "POLICE"

class PunchType(str, Enum):
    PUNCH_IN = "PUNCH_IN"
    PUNCH_OUT = "PUNCH_OUT"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"

@dataclass
class PunchRecord:
    punch_id: str
    user_id: str
    agency: str
    action: str
    timestamp: float
    prev_hash: str
    record_hash: str

class ShiftPunchClock:
    def __init__(self, db_path: str = "trust_duty_logs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS punch_logs (
                    punch_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    agency TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    prev_hash TEXT NOT NULL,
                    record_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def _get_last_hash(self) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT record_hash FROM punch_logs ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else "GENESIS_PUNCH_SEED"

    def record_punch(self, user_id: str, agency: AgencyType, action: PunchType) -> PunchRecord:
        now = time.time()
        prev_hash = self._get_last_hash()
        punch_id = f"{user_id}_{int(now)}"

        # Compute tamper-evident hash for evidence integrity
        payload = f"{punch_id}:{user_id}:{agency.value}:{action.value}:{now}:{prev_hash}"
        record_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

        record = PunchRecord(
            punch_id=punch_id,
            user_id=user_id,
            agency=agency.value,
            action=action.value,
            timestamp=now,
            prev_hash=prev_hash,
            record_hash=record_hash
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO punch_logs VALUES (?, ?, ?, ?, ?, ?, ?)",
                (record.punch_id, record.user_id, record.agency, record.action, 
                 record.timestamp, record.prev_hash, record.record_hash)
            )
            conn.commit()

        return record

    def get_active_duty_roster(() -> Dict[str, List[Dict]]:
        """Returns currently punched-in personnel grouped by agency."""
        roster = {AgencyType.EMS.value: [], AgencyType.FIRE.value: [], AgencyType.POLICE.value: []}
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Fetch latest action per user
            cursor.execute("""
                SELECT user_id, agency, action, MAX(timestamp) as last_time
                FROM punch_logs
                GROUP BY user_id
            """)
            for row in cursor.fetchall():
                if row['action'] in (PunchType.PUNCH_IN.value, PunchType.BREAK_END.value):
                    roster[row['agency']].append({
                        "user_id": row['user_id'],
                        "status": "ON_DUTY",
                        "since": row['last_time'],
                        "active_seconds": round(time.time() - row['last_time'], 1)
                    })
        return roster
