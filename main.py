import mimetypes
import pathlib
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from jinja2 import Environment, FileSystemLoader


SERVER_PORT = 3000
ASSETS_PATH = "./assets"
MESSAGE_STORAGE = "storage/data.json"


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        print(data_dict)
        self.save_messages(data_dict)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.read_messages()
        else:
            if pathlib.Path().joinpath(ASSETS_PATH, pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200, variables={}):
        env = Environment(loader=FileSystemLoader(ASSETS_PATH))
        template = env.get_template(f"{filename}")

        output = template.render(variables)

        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(output.encode())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f"{ASSETS_PATH}{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def save_messages(self, data: dict) -> None:
        my_file = pathlib.Path(MESSAGE_STORAGE)

        storage = None

        if my_file.is_file():
            with open(MESSAGE_STORAGE, "r", encoding="utf-8") as json_data:
                try:
                    storage = json.load(json_data)
                except Exception as e:
                    print(f"\tError: {e}")
                json_data.close()

        messages = {}
        if storage:
            messages = storage

        messages.update({f"{datetime.now()}": data})

        with open(MESSAGE_STORAGE, "w", encoding="utf-8") as fh:
            json.dump(messages, fh, ensure_ascii=False, indent=4)

    def read_messages(self) -> None:
        my_file = pathlib.Path(MESSAGE_STORAGE)

        messages = {}

        if my_file.is_file():
            with open(MESSAGE_STORAGE, "r", encoding="utf-8") as json_data:
                try:
                    messages = json.load(json_data)
                except Exception as e:
                    print(f"\tError: {e}")
                json_data.close()

        self.send_html_file("read.html", variables={"messages": messages})


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", SERVER_PORT)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
