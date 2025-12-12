import socket
from datetime import datetime

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5050

DEVICE_NAME = "Sensor01"
DEVICE_TYPE = "temperature"


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


def recv_line(sock: socket.socket) -> str | None:
    """
    Receive a newline-terminated string from a socket connection.

    Returns the received string decoded from bytes to UTF-8 and stripped of
    leading/trailing whitespace, or None if the connection was closed by
    the peer during the receive operation.

    :param sock: socket.socket
    :return: str | None
    """
    
    data = b""
    try:
        while True:
            chunk = sock.recv(1)
            if not chunk:
                return None
            if chunk == b"\n":
                break
            data += chunk
        return data.decode("utf-8").strip()
    except (ConnectionResetError, OSError):
        return None


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_HOST, SERVER_PORT))
        log(f"Connected to Smart Hub at {SERVER_HOST}:{SERVER_PORT}")

        # Send registration
        reg_msg = f"DEVICE {DEVICE_NAME} TYPE {DEVICE_TYPE}"
        sock.sendall((reg_msg + "\n").encode("utf-8"))
        log(f"Sent registration: {reg_msg}")

        # Wait for commands
        while True:
            cmd = recv_line(sock)
            if cmd is None:
                log("Disconnected from server")
                break

            log(f"Received command: {cmd}")

            # Simulate executing the command
            if cmd.startswith("SET_INTERVAL "):
                interval = cmd.split(maxsplit=1)[1]
                log(f"{DEVICE_NAME}: Changing reporting interval to {interval} seconds (simulated)")
            elif cmd == "ACTIVATE_ALARM":
                log(f"{DEVICE_NAME}: Alarm activated (simulated)")
            else:
                log(f"{DEVICE_NAME}: Unknown command, but executing (simulated)")

            # Send ACK
            ack = "ACK Command Executed"
            sock.sendall((ack + "\n").encode("utf-8"))
            log(f"Sent ACK: {ack}")

    except ConnectionRefusedError:
        log("Unable to connect to Smart Hub (connection refused)")
    finally:
        sock.close()
        log("Socket closed")


if __name__ == "__main__":
    main()
