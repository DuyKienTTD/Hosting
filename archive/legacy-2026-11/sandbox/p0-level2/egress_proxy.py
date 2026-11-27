#!/usr/bin/env python3
"""Small CONNECT proxy that permits only the approved OpenAI API endpoint."""

from __future__ import annotations

import select
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOST = "0.0.0.0"
PORT = 8888
ALLOWED_TARGET = "api.openai.com:443"


class Handler(BaseHTTPRequestHandler):
    server_version = "ttd-p0-egress/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        # Never log tunneled payloads or headers.
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            body = b'{"status":"ok","allow":"api.openai.com:443"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(405)

    def do_CONNECT(self) -> None:  # noqa: N802
        if self.path.lower() != ALLOWED_TARGET:
            self.send_error(403, "target_not_allowed")
            return
        try:
            upstream = socket.create_connection(("api.openai.com", 443), timeout=10)
        except OSError:
            self.send_error(502, "upstream_unavailable")
            return
        self.send_response(200, "Connection Established")
        self.end_headers()
        sockets = [self.connection, upstream]
        try:
            while True:
                readable, _, exceptional = select.select(sockets, [], sockets, 30)
                if exceptional or not readable:
                    break
                for source in readable:
                    data = source.recv(65536)
                    if not data:
                        return
                    target = upstream if source is self.connection else self.connection
                    target.sendall(data)
        finally:
            upstream.close()


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
