from http.server import ThreadingHTTPServer
import threading
import time
import urllib.request
import json
import socket

from server.server import StuffRequestHandler


def start_test_server():
    # bind to port 0 to get an ephemeral port
    server = ThreadingHTTPServer(("127.0.0.1", 0), StuffRequestHandler)
    host, port = server.server_address

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # wait briefly for server to come up
    time.sleep(0.1)
    return server, port


def stop_test_server(server):
    server.shutdown()
    server.server_close()


def fetch(path, port):
    url = f"http://127.0.0.1:{port}{path}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.read().decode('utf-8'), resp.getcode(), resp.info().get_content_type()


def test_api_message_and_status():
    server, port = start_test_server()
    try:
        body, code, ctype = fetch('/api/status', port)
        assert code == 200
        data = json.loads(body)
        assert 'server_id' in data

        body, code, ctype = fetch('/api/message', port)
        assert code == 200
        m = json.loads(body)
        assert 'id' in m and 'message' in m

        body, code, ctype = fetch('/api/messages', port)
        assert code == 200
        d = json.loads(body)
        assert 'messages' in d
    finally:
        stop_test_server(server)
