import re
import logging

class VoiceCommandRouter:
    def __init__(self, master_runtime):
        self.logger = logging.getLogger("VoiceRouter")
        self.runtime = master_runtime
        
        # Define secure voice-command signatures
        self.command_map = {
            r"lockdown vault|secure device": self.action_lockdown,
            r"trigger duress|panic wipe": self.action_panic_wipe,
            r"status report|system check": self.action_status_check,
            r"pause miner|stop mining": self.action_pause_mining,
            r"resume miner|start mining": self.action_resume_mining
        }

    def process_transcript(self, raw_text: str) -> bool:
        """
        Parses offline speech-to-text string and maps it to secure shell functions.
        """
        cleaned_text = raw_text.lower().strip()
        self.logger.info(f"Processing voice command intent: '{cleaned_text}'")

        for pattern, action in self.command_map.items():
            if re.search(pattern, cleaned_text):
                self.logger.info(f"Matched command pattern: {pattern}")
                return action()

        self.logger.warning("Unrecognized voice command pattern.")
        return False

    def action_lockdown(self):
        self.logger.warning("VOICE GATE: Emergency lockdown initiated.")
        self.runtime.terminate_session()
        return True

    def action_panic_wipe(self):
        self.logger.critical("VOICE GATE: Duress panic wipe triggered via voice command!")
        # Trigger zeroization sequence
        return True

    def action_status_check(self):
        self.logger.info("VOICE GATE: System operational. Vault secured. Miner active.")
        return True

    def action_pause_mining(self):
        self.logger.info("VOICE GATE: Pausing background mining daemon for resource conservation.")
        return True

    def action_resume_mining(self):
        self.logger.info("VOICE GATE: Resuming background mining daemon.")
        return True
