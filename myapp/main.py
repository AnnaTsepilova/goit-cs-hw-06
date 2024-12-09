import os
import socket
import json
import multiprocessing
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pymongo import MongoClient
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "message_db")
WEBSOCKET_PORT = 5000

# HTTP server setup
class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/message':
            self.path = './message.html'
        elif self.path.endswith('.css') or self.path.endswith('.png'):
            self.path = self.path
        else:
            self.path = './error.html'
            self.send_response(404)
        return super().do_GET()

    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))
            message = {
                "date": str(datetime.now()),
                "username": data["username"][0],
                "message": data["message"][0]
            }

            # Send data to the socket server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(('localhost', 5000))
                sock.sendall(json.dumps(message).encode('utf-8'))

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b'Message submitted')

def run_http_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, CustomHandler)
    print("HTTP Server running on port 3000...")
    httpd.serve_forever()

def run_socket_server():
    # MongoDB setup
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    messages_collection = db['messages']

    print(f"Socket Server running on port {WEBSOCKET_PORT}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', WEBSOCKET_PORT))
        server_socket.listen()

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print('Connected by', addr)
                data = conn.recv(1024)
                if data:
                    message = json.loads(data.decode('utf-8'))
                    messages_collection.insert_one(message)
                    print(f"Message saved: {message}")

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=run_http_server)
    p2 = multiprocessing.Process(target=run_socket_server)
    p1.start()
    p2.start()
    p1.join()
    p2.join()