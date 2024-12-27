import socket
import threading
import base64
import hashlib

HOST = '127.0.0.1'  # localhost
PORT = 8080         # Port to listen on

# WebSocket Server Class
class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"WebSocket server running at ws://{self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New connection from {client_address}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            self.perform_handshake(client_socket)
            while True:
                message = self.receive_message(client_socket)
                if message:
                    print(f"Received message: {message}")
                    self.broadcast(message, client_socket)
                else:
                    break
        except Exception as e:
            print(f"Client disconnected: {e}")
        finally:
            client_socket.close()
            self.clients.remove(client_socket)

    def perform_handshake(self, client_socket):
        request = client_socket.recv(1024).decode('utf-8')
        headers = self.parse_headers(request)
        websocket_key = headers['Sec-WebSocket-Key']
        accept_key = self.generate_accept_key(websocket_key)

        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
        )
        client_socket.send(response.encode('utf-8'))

    def parse_headers(self, request):
        headers = {}
        lines = request.split("\r\n")
        for line in lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
        return headers

    def generate_accept_key(self, websocket_key):
        GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        key = websocket_key + GUID
        hashed = hashlib.sha1(key.encode('utf-8')).digest()
        return base64.b64encode(hashed).decode('utf-8')

    def receive_message(self, client_socket):
        try:
            data = client_socket.recv(1024)
            if not data:
                return None
            # Decode WebSocket message
            payload_length = data[1] & 127
            if payload_length == 126:
                mask = data[4:8]
                payload = data[8:]
            elif payload_length == 127:
                mask = data[10:14]
                payload = data[14:]
            else:
                mask = data[2:6]
                payload = data[6:]
            return ''.join(chr(payload[i] ^ mask[i % 4]) for i in range(len(payload)))
        except:
            return None

    def broadcast(self, message, sender_socket):
        encoded_message = self.encode_message(message)
        for client in self.clients:
            if client != sender_socket:
                client.send(encoded_message)

    def encode_message(self, message):
        encoded_message = message.encode('utf-8')
        header = bytearray()
        header.append(129)  # Text frame
        if len(encoded_message) <= 125:
            header.append(len(encoded_message))
        elif len(encoded_message) <= 65535:
            header.append(126)
            header.extend(len(encoded_message).to_bytes(2, 'big'))
        else:
            header.append(127)
            header.extend(len(encoded_message).to_bytes(8, 'big'))
        return header + encoded_message


# Start the WebSocket server
if __name__ == "__main__":
    server = WebSocketServer(HOST, PORT)
    server.start()
