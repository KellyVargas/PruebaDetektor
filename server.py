#!/usr/bin/env python3
"""Servicio QA ficticio. Python 3.9+, biblioteca estandar. NO usar en produccion.
El comportamiento debe ser evaluado contra el contrato funcional del ejercicio.
"""
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import json, os

_EVENTS = []

def parse_utc(raw):
    try:
        d = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo is not None else None
    except (ValueError, TypeError):
        return None

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def reply(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def client(self):
        return self.headers.get("X-Client-ID", "").strip()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/health":
            return self.reply(200, {"status":"ok","service":"qa-telemetria-lab"})
        if url.path != "/v1/events":
            return self.reply(404, {"error":"not_found"})
        if not self.client():
            return self.reply(401, {"error":"missing_client"})
        device = parse_qs(url.query).get("device_id", [""])[0]
        if not device:
            return self.reply(400, {"error":"missing_device_id"})
        # El comportamiento de esta funcion debe contrastarse con el contrato.
        items = [
        e for e in _EVENTS
        if e["device_id"] == device
        and e["client_id"] == self.client()
        ]
        return self.reply(200, {"items":items})

    def do_POST(self):
        if urlparse(self.path).path != "/v1/events":
            return self.reply(404, {"error":"not_found"})
        client = self.client()
        if not client:
            return self.reply(401, {"error":"missing_client"})
        try:
            length = int(self.headers.get("Content-Length","0"))
            if length < 1 or length > 65536:
                return self.reply(400, {"error":"invalid_body"})
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                return self.reply(400, {"error":"invalid_json"})
        except (ValueError, json.JSONDecodeError):
            return self.reply(400, {"error":"invalid_json"})
        needed = ["client_id","event_id","device_id","occurred_at","lat","lon"]
        if any(k not in body for k in needed):
            return self.reply(422, {"error":"missing_fields"})
        if body["client_id"] != client:
            return self.reply(403, {"error":"client_mismatch"})
        if not all(isinstance(body[k],str) and body[k].strip() for k in ["event_id","device_id"]):
            return self.reply(422, {"error":"invalid_identity"})
        dt = parse_utc(body["occurred_at"])
        if dt is None:
            return self.reply(422, {"error":"invalid_timestamp"})
        if type(body["lat"]) not in (int,float) or type(body["lon"]) not in (int,float):
            return self.reply(422, {"error":"invalid_coordinate"})
        if not -90 <= body["lat"] <= 90 or not -180 <= body["lon"] <= 180:
            return self.reply(422, {"error":"invalid_coordinate"})
        # Contrastar efectos e invariantes del endpoint con el contrato.
        _EVENTS.append({key:body[key] for key in needed})
        return self.reply(201, {"status":"created","event_id":body["event_id"]})

    def do_DELETE(self):
        if urlparse(self.path).path == "/_test/reset":
            _EVENTS.clear()
            return self.reply(200, {"status":"reset"})
        return self.reply(404, {"error":"not_found"})

if __name__ == "__main__":
    host, port = "127.0.0.1", int(os.getenv("QA_LAB_PORT","8765"))
    print(f"QA Lab: http://{host}:{port} (solo localhost)",flush=True)
    ThreadingHTTPServer((host,port),Handler).serve_forever()
