#!/usr/bin/env python3
import time
import json
from ems_service import EMSService
from fire_service import FireService
from police_service import PoliceService

class AgencyResponseHub:
    def __init__(self):
        # Instantiate decoupled client service handlers
        self.ems_client = EMSService()
        self.fire_client = FireService()
        self.police_client = PoliceService()

    def broadcast_ping(self) -> dict:
        """Polls EMS, Fire, and Police independent microservices over IPC."""
        now = time.time()
        return {
            "timestamp": now,
            "agencies": {
                "EMS": self.ems_client.process_cycle(),
                "FIRE": self.fire_client.process_cycle(),
                "POLICE": self.police_client.process_cycle()
            }
        }

if __name__ == "__main__":
    hub = AgencyResponseHub()
    print("[TRUST_SHELL] Polling decoupled microservices...")
    print(json.dumps(hub.broadcast_ping(), indent=2))
