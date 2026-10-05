import sys
import os
import time

# Point Trust-Shell to Trust-Main modules path
TRUST_MAIN_MODULES = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Trust-Main/modules"))
if os.path.exists(TRUST_MAIN_MODULES) and TRUST_MAIN_MODULES not in sys.path:
    sys.path.insert(0, TRUST_MAIN_MODULES)

class AgencyResponseHub:
    def __init__(self):
        self._handlers = {}
        self._load_module_adapters()

    def _load_module_adapters(self):
        # 1. EMS Module Adapter
        try:
            from ems.ems_ai_module import EMSAIResponder
            ems_node = EMSAIResponder()
            self._handlers["EMS"] = lambda: ems_node.run_live_cycle()
        except ImportError:
            self._handlers["EMS"] = lambda: {"status": "OFFLINE", "reason": "modules/ems unlinked"}

        # 2. Fire Module Adapter Placeholder
        self._handlers["FIRE"] = lambda: {"status": "ONLINE", "hazmat": "NOMINAL", "timestamp": time.time()}

        # 3. Police Module Adapter Placeholder
        self._handlers["POLICE"] = lambda: {"status": "ONLINE", "ballistics": "STANDBY", "timestamp": time.time()}

    def poll_all_agencies(self) -> dict:
        results = {}
        for agency, handler in self._handlers.items():
            results[agency] = handler()
        return results
