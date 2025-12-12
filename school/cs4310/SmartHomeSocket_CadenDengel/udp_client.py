import socket
import time
from datetime import datetime
import random

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6060

DEVICE_ID = "Sensor01"
SENSOR_TYPE = "temperature"
CYCLE_SIZE = 10
SEND_INTERVAL_SECONDS = 1.0
ACK_TIMEOUT_SECONDS = 5.0
MAX_ACK_RETRIES = 2  # just to demonstrate retry


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (SERVER_HOST, SERVER_PORT)
    sock.settimeout(ACK_TIMEOUT_SECONDS)

    try:
        # Send one cycle of packets
        base_temp = 24.0

        for seq in range(1, CYCLE_SIZE + 1):
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Add some random variation to the temperature
            value = base_temp + random.uniform(-0.5, 0.5)
            msg = f"{DEVICE_ID},{timestamp_str},{SENSOR_TYPE},{value:.1f},SEQ:{seq}"

            print(f"[{DEVICE_ID}] Sending packet SEQ:{seq} — Temp={value:.1f}°C")
            sock.sendto(msg.encode("utf-8"), server_addr)

            time.sleep(SEND_INTERVAL_SECONDS)

        # Wait for status acknowledgment from server, with simple retry
        for attempt in range(MAX_ACK_RETRIES + 1):
            try:
                data, addr = sock.recvfrom(4096)
                ack_msg = data.decode("utf-8").strip()
                print(f"[{DEVICE_ID}] Received status from server: {ack_msg}")
                break
            except socket.timeout:
                if attempt < MAX_ACK_RETRIES:
                    print(f"[{DEVICE_ID}] No status ACK received (timeout). Retrying...")
                    # Optionally re-send last packet to trigger status
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    value = base_temp + random.uniform(-0.5, 0.5)
                    seq = CYCLE_SIZE  # last sequence
                    msg = f"{DEVICE_ID},{timestamp_str},{SENSOR_TYPE},{value:.1f},SEQ:{seq}"
                    print(f"[{DEVICE_ID}] Re-sending last packet SEQ:{seq}")
                    sock.sendto(msg.encode("utf-8"), server_addr)
                else:
                    print(f"[{DEVICE_ID}] No status ACK received after retries. Giving up.")

    finally:
        sock.close()
        print(f"[{DEVICE_ID}] UDP socket closed")


if __name__ == "__main__":
    main()
