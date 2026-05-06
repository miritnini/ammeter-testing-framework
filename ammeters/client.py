from socket import socket, AF_INET, SOCK_STREAM


def request_current_from_ammeter(port: int, command: bytes):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.sendall(command)
        data = s.recv(1024)
        if not data:
            print("No data received.")
            return None

        value = data.decode().strip()
        print(f"Received current measurement from port {port}: {value} A")
        return float(value) if value != "ERROR" else None

