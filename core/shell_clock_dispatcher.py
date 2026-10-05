import time
import json
from shift_punch_clock import ShiftPunchClock, AgencyType, PunchType
from agency_response_hub import AgencyResponseHub, ResponseStatus

class TrustShellClockEngine:
    def __init__(self, tick_interval_sec: float = 1.0):
        self.tick_interval = tick_interval_sec
        self.punch_clock = ShiftPunchClock()
        self.hub = AgencyResponseHub()
        self._is_running = False

        # Register default dummy handlers (replaced by live submodule connections)
        self._setup_default_agency_handlers()

    def _setup_default_agency_handlers(self):
        # EMS Module Handler (Integrates with thermal/voice telemetry)
        def ems_status():
            roster = self.punch_clock.get_active_duty_roster()
            active_count = len(roster.get(AgencyType.EMS.value, []))
            return {
                "status": ResponseStatus.AVAILABLE.value if active_count > 0 else ResponseStatus.BUSY.value,
                "active_units": active_count,
                "thermal_camera_online": True,
                "timestamp": time.time()
            }

        # Fire Module Handler
        def fire_status():
            roster = self.punch_clock.get_active_duty_roster()
            active_count = len(roster.get(AgencyType.FIRE.value, []))
            return {
                "status": ResponseStatus.AVAILABLE.value if active_count > 0 else ResponseStatus.OFF_DUTY.value,
                "active_units": active_count,
                "hazmat_sensors": "NOMINAL",
                "timestamp": time.time()
            }

        # Police Module Handler
        def police_status():
            roster = self.punch_clock.get_active_duty_roster()
            active_count = len(roster.get(AgencyType.POLICE.value, []))
            return {
                "status": ResponseStatus.AVAILABLE.value if active_count > 0 else ResponseStatus.OFF_DUTY.value,
                "active_units": active_count,
                "ballistic_engine": "ACTIVE",
                "timestamp": time.time()
            }

        self.hub.register_module("EMS", ems_status)
        self.hub.register_module("FIRE", fire_status)
        self.hub.register_module("POLICE", police_status)

    def execute_clock_tick(self):
        """Called every second by the Trust Shell UI/Terminal loop."""
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # Broadcast ping to all registered modules
        agency_states = self.hub.broadcast_ping()
        
        # Render shell telemetry line
        print(f"\n[TRUST_SHELL CLOCK {timestamp_str}]")
        print(f"  ├─ EMS:    {agency_states['agencies']['EMS']['status']} (Units: {agency_states['agencies']['EMS']['active_units']})")
        print(f"  ├─ FIRE:   {agency_states['agencies']['FIRE']['status']} (Units: {agency_states['agencies']['FIRE']['active_units']})")
        print(f"  └─ POLICE: {agency_states['agencies']['POLICE']['status']} (Units: {agency_states['agencies']['POLICE']['active_units']})")

if __name__ == "__main__":
    engine = TrustShellClockEngine()

    print("--- 1. SIMULATING PUNCH IN ACTIONS ---")
    p1 = engine.punch_clock.record_punch("MEDIC_101", AgencyType.EMS, PunchType.PUNCH_IN)
    p2 = engine.punch_clock.record_punch("ENG_202", AgencyType.FIRE, PunchType.PUNCH_IN)
    p3 = engine.punch_clock.record_punch("OFFICER_303", AgencyType.POLICE, PunchType.PUNCH_IN)

    print(f"Recorded Punch In: {p1.user_id} ({p1.agency}) | Hash: {p1.record_hash[:16]}...")

    print("\n--- 2. EXECUTE SHELL CLOCK TICK ---")
    engine.execute_clock_tick()

    print("\n--- 3. SIMULATING PUNCH OUT (EMS UNIT) ---")
    p4 = engine.punch_clock.record_punch("MEDIC_101", AgencyType.EMS, PunchType.PUNCH_OUT)

    print("\n--- 4. EXECUTE SUBSEQUENT CLOCK TICK ---")
    engine.execute_clock_tick()
