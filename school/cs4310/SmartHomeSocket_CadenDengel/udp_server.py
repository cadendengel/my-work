import socket
from datetime import datetime

HOST = "127.0.0.1"
PORT = 6060

LOG_FILE = "sensor_data_log.txt"
CYCLE_SIZE = 10  # number of packets per cycle, e.g., 10

# For each device, track which sequence numbers we've received for the current cycle
device_state = {}  # device_id -> {"seqs": set[int]}


def log(msg: str):
    """
    Log a message to the console and append it to a file.

    The message will be prefixed with a timestamp in the format
    "YYYY-MM-DD HH:MM:SS" and will be written to the file specified by
    the LOG_FILE constant.

    The log file will be locked while writing to ensure thread safety.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_packet(packet: str):
    """
    Parse a UDP packet received from a device.

    The packet is expected to be in the format:
    <device_id>,<timestamp>,<sensor_type>,<value>,SEQ:<seq_num>

    Returns a tuple of (device_id, timestamp_str, sensor_type, value_str, seq_num)

    :raises ValueError: if the packet format is invalid
    """
    
    parts = packet.split(",")
    if len(parts) < 5:
        raise ValueError("Invalid packet format")

    device_id = parts[0]
    timestamp_str = parts[1]
    sensor_type = parts[2]
    value_str = parts[3]
    seq_part = parts[4]

    if "SEQ:" not in seq_part:
        raise ValueError("Missing SEQ in packet")

    seq_num = int(seq_part.split("SEQ:")[1])
    return device_id, timestamp_str, sensor_type, value_str, seq_num


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    log(f"[UDP] Smart Hub UDP Server listening on {HOST}:{PORT}")

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            msg = data.decode("utf-8").strip()
            log(f"[UDP] From {addr}: {msg}")

            try:
                device_id, tstamp, sensor_type, value_str, seq_num = parse_packet(msg)
            except Exception as e:
                log(f"[UDP] Failed to parse packet: {e}")
                continue

            # Update state
            state = device_state.setdefault(device_id, {"seqs": set()})
            state["seqs"].add(seq_num)

            # Check for missing packets and cycle completion
            received_seqs = state["seqs"]
            max_seq = max(received_seqs)
            missing = [s for s in range(1, max_seq + 1) if s not in received_seqs]

            # If we've collected at least CYCLE_SIZE unique packets, we treat it as a full cycle
            if len(received_seqs) >= CYCLE_SIZE:
                # Determine how many of 1..CYCLE_SIZE we got
                got = len([s for s in range(1, CYCLE_SIZE + 1) if s in received_seqs])
                missing_cycle = [s for s in range(1, CYCLE_SIZE + 1) if s not in received_seqs]

                status_msg = f"STATUS RECEIVED {got}/{CYCLE_SIZE} PACKETS"
                if missing_cycle:
                    status_msg += f" (MISSING: {missing_cycle})"

                sock.sendto(status_msg.encode("utf-8"), addr)
                log(f"[UDP] Sent status to {device_id} at {addr}: {status_msg}")

                # Reset for next cycle
                device_state[device_id] = {"seqs": set()}

    except KeyboardInterrupt:
        log("[UDP] Server shutting down (KeyboardInterrupt)")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
