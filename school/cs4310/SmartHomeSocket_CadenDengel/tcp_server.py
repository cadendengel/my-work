import socket
import threading
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5050

devices = {}
devices_lock = threading.Lock()
log_lock = threading.Lock()
LOG_FILE = "server_log.txt"


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
    with log_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def recv_line(conn: socket.socket) -> str | None:
    """
    Receive a newline-terminated string from a socket connection.

    Returns the received string decoded from bytes to UTF-8 and stripped of
    leading/trailing whitespace, or None if the connection was closed by
    the peer during the receive operation.

    :param conn: socket.socket
    :return: str | None
    """

    data = b""
    try:
        while True:
            chunk = conn.recv(1)
            if not chunk:
                # peer closed connection
                return None
            if chunk == b"\n":
                break
            data += chunk
        return data.decode("utf-8").strip()
    except (ConnectionResetError, OSError):
        return None


def handle_client(conn: socket.socket, addr):
    """
    Handle a single TCP client connection.

    Listens for registration (e.g. "DEVICE Sensor01 TYPE temperature")
    and stores the device information in a global dictionary.

    Afterwards, it just listens for messages from the device (e.g. ACKs)
    and logs them.

    Cleanup is done on disconnect: device information is removed from
    the global dictionary and the socket is closed.
    """

    log(f"[TCP] New connection from {addr[0]}:{addr[1]}")
    device_name = None

    try:
        # Expect registration, e.g. "DEVICE Sensor01 TYPE temperature"
        reg_msg = recv_line(conn)
        if not reg_msg:
            log(f"[TCP] {addr} disconnected before registration")
            conn.close()
            return

        log(f"[TCP] Received registration from {addr}: {reg_msg}")

        # Simple parsing: DEVICE <name> TYPE <type>
        parts = reg_msg.split()
        if len(parts) >= 4 and parts[0] == "DEVICE" and parts[2] == "TYPE":
            device_name = parts[1]
            device_type = parts[3]
        else:
            log(f"[TCP] Invalid registration format from {addr}: {reg_msg}")
            conn.close()
            return

        # Store in global devices dictionary
        with devices_lock:
            devices[device_name] = {
                "conn": conn,
                "addr": addr,
                "type": device_type
            }

        log(f"[TCP] Registered device: {device_name} TYPE={device_type} from {addr}")

        # Now just listen for messages from this device (e.g. ACKs)
        while True:
            msg = recv_line(conn)
            if msg is None:
                log(f"[TCP] Device {device_name} disconnected")
                break

            log(f"[TCP] From {device_name}: {msg}")

    finally:
        # Cleanup on disconnect
        if device_name:
            with devices_lock:
                devices.pop(device_name, None)
            log(f"[TCP] Device {device_name} removed from registry")
        conn.close()


def accept_loop(server_sock: socket.socket):
    """Accept clients in a loop and spawn handler threads."""

    while True:
        try:
            conn, addr = server_sock.accept()
        except OSError:
            break  # socket closed
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()


def send_command_to_device(device_name: str, command: str):
    """Send a command string to a registered device over TCP."""
    
    with devices_lock:
        info = devices.get(device_name)

    if not info:
        log(f"[TCP] Device {device_name} not found")
        return

    conn = info["conn"]
    try:
        conn.sendall((command + "\n").encode("utf-8"))
        log(f"[TCP] Sent command to {device_name}: {command}")
    except (BrokenPipeError, ConnectionResetError, OSError):
        log(f"[TCP] Failed to send command to {device_name} (connection issue)")


def main():
    # Create TCP server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    log(f"[TCP] Smart Hub TCP Server listening on {HOST}:{PORT}")

    # Start accept loop thread
    accepter = threading.Thread(target=accept_loop, args=(server_sock,), daemon=True)
    accepter.start()

    # Simple CLI loop to send commands
    try:
        while True:
            print("\nCommands:")
            print("  list                         - list connected devices")
            print("  send <dev> <COMMAND...>      - send command to device")
            print("  quit                         - stop server")
            user_input = input("smart-hub> ").strip()

            if not user_input:
                continue

            if user_input == "list":
                with devices_lock:
                    if not devices:
                        print("No devices registered")
                    else:
                        print("Registered devices:")
                        for name, info in devices.items():
                            print(f"  {name} ({info['type']}) @ {info['addr']}")
                continue

            if user_input == "quit":
                log("[TCP] Shutting down server")
                break

            if user_input.startswith("send "):
                parts = user_input.split(maxsplit=2)
                if len(parts) < 3:
                    print("Usage: send <device_name> <COMMAND...>")
                    continue
                device_name = parts[1]
                command = parts[2]
                send_command_to_device(device_name, command)
                continue

            print("Unknown command")
    except KeyboardInterrupt:
        log("[TCP] Keyboard interrupt, shutting down")
    finally:
        server_sock.close()


if __name__ == "__main__":
    main()
