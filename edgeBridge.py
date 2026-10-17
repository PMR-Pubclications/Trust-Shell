import json
import zstd  # pip install zstd
import trust_packet_pb2 as pb  # compiled from your .proto file

def serialize_legacy_json(device_id: str, schema_type: str, json_data: dict) -> bytes:
    """
    Takes an existing JSON dict, compresses it, and wraps it in a Protobuf packet.
    """
    # 1. Convert existing dict to standard JSON string/bytes
    raw_json = json.dumps(json_data).encode('utf-8')
    
    # 2. Compress the JSON payload to save bandwidth
    compressed_payload = zstd.compress(raw_json)
    
    # 3. Pack into the Protobuf envelope
    packet = pb.TrustPacket(
        device_id=device_id,
        timestamp=int(time.time()),
        schema_type=schema_type,
        payload_json=compressed_payload
    )
    
    return packet.SerializeToString()
