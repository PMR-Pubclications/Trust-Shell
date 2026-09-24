import time
import threading
import logging

class TrustResourceGovernor:
    def __init__(self, mining_daemon, battery_threshold_pct=20):
        self.mining_daemon = mining_daemon
        self.battery_threshold = battery_threshold_pct
        self.is_evidence_capturing = False
        self._monitoring = False

    def start_governor_loop(self):
        """Starts the background resource monitoring loop."""
        self._monitoring = True
        governor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        governor_thread.start()
        print("[GOVERNOR] Hardware resource governor active.")

    def set_evidence_capture_state(self, active: bool):
        """
        Dynamically pauses background mining immediately when the officer 
        begins capturing a crime scene photo, audio clip, or thermal scan.
        """
        self.is_evidence_capturing = active
        if active:
            print("[GOVERNOR] Evidence capture initiated. Pausing background mining to prioritize CPU/Thermal budget.")
            if self.mining_daemon.running:
                self.mining_daemon.stop()
        else:
            print("[GOVERNOR] Evidence capture concluded. Resuming background mining daemon.")
            self.mining_daemon.start()

    def _monitor_loop(self):
        """Polls battery levels and thermal states."""
        while self._monitoring:
            try:
                # Simulated hardware telemetry checks (interfaces with native OS battery/thermal managers)
                current_battery = self._get_system_battery_level()
                is_overheated = self._check_thermal_throttle()

                if current_battery < self.battery_threshold:
                    print(f"[GOVERNOR WARNING] Battery critical ({current_battery}%). Suspending background mining to preserve field ops.")
                    if self.mining_daemon.running:
                        self.mining_daemon.stop()

                if is_overheated:
                    print("[GOVERNOR WARNING] Thermal threshold exceeded. Throttling background processes.")
                    if self.mining_daemon.running:
                        self.mining_daemon.stop()

            except Exception as e:
                logging.error(f"Governor error: {e}")

            time.sleep(30) # Check every 30 seconds

    def _get_system_battery_level(self) -> int:
        # Mock hook for Android/iOS battery API (returns percentage 0-100)
        return 85 

    def _check_thermal_throttle(self) -> bool:
        # Mock hook for system thermal throttling state
        return False

    def stop(self):
        self._monitoring = False
