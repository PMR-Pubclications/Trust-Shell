import time
from enum import Enum
from typing import Dict, Any, Callable

class ResponseStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESPONDING = "RESPONDING"
    ON_SCENE = "ON_SCENE"
    BUSY = "BUSY"
    OFF_DUTY = "OFF_DUTY"

class AgencyResponseHub:
    def __init__(self):
        # Register response generators for each module
        self._agency_handlers: Dict[str, Callable[[], Dict[str, Any]]] = {}

    def register_module(self, agency_name: str, status_callback: Callable[[], Dict[str, Any]]):
        self._agency_handlers[agency_name.upper()] = status_callback

    def broadcast_ping(self, incident_id: str = None) -> Dict[str, Any]:
        """Queries EMS, Fire, and Police modules for status and telemetry summaries."""
        now = time.time()
        responses = {}

        for agency, callback in self._agency_handlers.items():
            try:
                responses[agency] = callback()
            except Exception as ex:
                responses[agency] = {
                    "status": ResponseStatus.OFF_DUTY.value,
                    "error": f"Module unreachable: {str(ex)}",
                    "timestamp": now
                }

        return {
            "dispatch_timestamp": now,
            "incident_id": incident_id or "ROUTINE_PULSE",
            "agencies": responses
        }
