import math
import logging

class SpatialPacingEngine:
    def __init__(self, audit_ledger):
        self.logger = logging.getLogger("SpatialPacer")
        self.ledger = audit_ledger
        self.current_origin = (0.0, 0.0, 0.0)
        self.active_track = []

    def process_pacing_command(self, text_command: str) -> dict:
        """
        Parses hands-free voice commands for crime scene mapping.
        Example: "Mark baseline origin" or "Vector 10 paces north, evidence marker 3"
        """
        cleaned = text_command.lower().strip()
        self.logger.info(f"Processing spatial pacing command: '{cleaned}'")

        if "set origin" in cleaned or "mark baseline origin" in cleaned:
            self.current_origin = (0.0, 0.0, 0.0)
            self.active_track = []
            self.logger.info("Spatial origin reset to (0,0,0).")
            return {"status": "origin_set", "coordinates": self.current_origin}

        # Parse directional strides/paces via voice regex
        # e.g., "5 paces north"
        import re
        match = re.search(r"(\d+)\s+paces\s+(north|south|east|west|forward|back)", cleaned)
        if match:
            paces = int(match.group(1))
            direction = match.group(2)
            
            # Standard average investigator stride estimation (~2.5 feet per pace)
            distance_feet = paces * 2.5 
            
            vector_data = {
                "paces": paces,
                "estimated_feet": distance_feet,
                "direction": direction,
                "prev_position": self.current_origin
            }
            
            self.logger.info(f"Mapped vector: {paces} paces ({distance_feet} ft) towards {direction}.")
            self.active_track.append(vector_data)
            return {"status": "vector_recorded", "data": vector_data}

        return {"status": "unrecognized_spatial_command"}
