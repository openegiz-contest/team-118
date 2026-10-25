"""Local UI/control gateway. State responses ONLY come from Eclipse Ditto.

Creation uses the Ditto REST API; every runtime feature change uses MQTT.
There is intentionally no model-state fallback if the platform is unavailable.
"""

import base64
import json
import logging
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from .model import NAMESPACE, comparison, load_config, twin_definitions, twin_states, validate_integer

LOG = logging.getLogger("inkai")
WEB = Path(__file__).with_name("web")


class Platform:
    def __init__(self):
        self.url = os.environ.get("DITTO_URL", "http://localhost:8080").rstrip("/")
        password = os.environ["DITTO_PASSWORD"]
        self.auth = "Basic " + base64.b64encode(f"ditto:{password}".encode()).decode()
        self.config = load_config()
        self.definitions = twin_definitions(self.config)
        self.lock = threading.RLock()
        self.day, self.delay, self.counter = 0, 0, 0
        self.session = uuid.uuid4().hex[:12]
        self.revision = None
        self.connected = threading.Event()
        self.client = None

    def request(self, path, method="GET", body=None):
        request = Request(self.url + path, method=method,
                          headers={"Authorization": self.auth, "Content-Type": "application/json"},
                          data=json.dumps(body, allow_nan=False).encode() if body is not None else None)
        with urlopen(request, timeout=35) as response:
            raw = response.read()
            return json.loads(raw) if raw else None

    def initialize(self):
        import paho.mqtt.client as mqtt
        for tid, definition in self.definitions.items():
            for attempt in range(12):
                try:
                    self.request("/api/2/things/" + quote(tid, safe=":"), "PUT", definition)
                    break
                except (URLError, TimeoutError) as exc:
                    if attempt == 11:
                        raise
                    LOG.warning("Twin initialization retry %s: %s", tid, type(exc).__name__)
                    time.sleep(3)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="minemind-" + self.session)

        def connected(_client, _userdata, _flags, reason_code, _properties):
            if reason_code == 0:
                self.connected.set()

        def disconnected(_client, _userdata, _flags, _reason_code, _properties):
            self.connected.clear()

        self.client.on_connect = connected
        self.client.on_disconnect = disconnected
        self.client.connect(os.environ.get("MQTT_HOST", "localhost"), int(os.environ.get("MQTT_PORT", "1883")), 30)
        self.client.loop_start()
        if not self.connected.wait(30):
            raise RuntimeError("MQTT connection did not become ready")
        self.update("configure", {"day": self.config["demo_day"], "delay_days": 0})

    def read(self):
        ids = ",".join(self.definitions)
        things = self.request("/api/2/things?ids=" + quote(ids, safe=",:"))
        if not isinstance(things, list) or len(things) != len(self.definitions):
            raise RuntimeError("Incomplete platform snapshot")
        states = {}
        for thing in things:
            features = thing.get("features", {})
            revision = features.get("run", {}).get("properties", {}).get("revision")
            if revision != self.revision:
                raise RuntimeError("Platform is synchronizing; no mixed-revision snapshot is served")
            states[thing["thingId"]] = {"attributes": thing["attributes"], "state": features["state"]["properties"]}
        if set(states) != set(self.definitions):
            raise RuntimeError("Missing platform twins")
        return {"source": "Eclipse Ditto REST /api/2/things", "transport": "MQTT -> Ditto -> UI gateway",
                "revision": self.revision, "namespace": NAMESPACE, "twins": states}

    def update(self, action, values):
        with self.lock:
            if action == "reset":
                day, delay = 0, 0
            elif action == "configure":
                day, delay = values.get("day", self.day), values.get("delay_days", self.delay)
            elif action == "advance":
                days = values.get("days", 1)
                validate_integer(days, 1, self.config["horizon_days"], "days")
                day, delay = min(self.config["horizon_days"], self.day + days), self.delay
            else:
                raise ValueError("Unknown action")
            validate_integer(day, 0, self.config["horizon_days"], "day")
            validate_integer(delay, 0, self.config["max_delay_days"], "delay_days")
            if not self.connected.is_set():
                raise RuntimeError("MQTT is disconnected")
            state = comparison(delay, day, self.config)
            self.counter += 1
            revision = f"{self.session}-{self.counter}"
            for tid, payload in twin_states(state).items():
                name = tid.split(":", 1)[1]
                message = {"topic": f"{NAMESPACE}/{name}/things/twin/commands/modify", "path": "/features",
                           "value": {"run": {"properties": {"revision": revision}}, "state": {"properties": payload}}}
                info = self.client.publish(f"telemetry/{NAMESPACE}/{name}", json.dumps(message, allow_nan=False), qos=1)
                info.wait_for_publish(timeout=10)
                if not info.is_published():
                    raise RuntimeError("MQTT delivery was not acknowledged")
            self.revision = revision
            self.day, self.delay = day, delay
            # Broker acknowledgement is not proof of Ditto ingestion: read every twin.
            last = None
            for _ in range(30):
                try:
                    return self.read()
                except (URLError, TimeoutError, RuntimeError) as exc:
                    last = exc
                    time.sleep(0.5)
            raise RuntimeError("MQTT messages were sent but Ditto ingestion was not confirmed") from last


class Handler(BaseHTTPRequestHandler):
    server_version = "MineMind/1.0"

    def log_message(self, fmt, *args):
        LOG.info(fmt, *args)

    def send(self, code, body, content_type="application/json"):
        data = json.dumps(body, allow_nan=False).encode() if content_type == "application/json" else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path in ("/api/state", "/health"):
                with self.server.platform.lock:
                    state = self.server.platform.read()
                self.send(200, state if path == "/api/state" else {"status": "ok", "twins": len(state["twins"]), "source": state["source"]})
            elif path in ("/", "/app.js", "/style.css"):
                file = WEB / ("index.html" if path == "/" else path[1:])
                content_type = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}[file.suffix]
                self.send(200, file.read_bytes(), content_type)
            else:
                self.send(404, {"error": "Not found"})
        except (URLError, TimeoutError, RuntimeError, KeyError) as exc:
            LOG.warning("Platform read failed: %s", type(exc).__name__)
            self.send(503, {"error": "Platform state unavailable or synchronizing. Retry after checking Ditto/MQTT.", "detail": type(exc).__name__})

    def do_POST(self):
        if urlparse(self.path).path != "/api/control":
            self.send(404, {"error": "Not found"})
            return
        try:
            if self.headers.get_content_type() != "application/json":
                raise ValueError("Use application/json")
            origin = self.headers.get("Origin")
            if origin and urlparse(origin).netloc != self.headers.get("Host"):
                raise ValueError("Cross-origin controls are disabled")
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4096:
                raise ValueError("Invalid request size")
            values = json.loads(self.rfile.read(size))
            if not isinstance(values, dict):
                raise ValueError("Expected a JSON object")
            self.send(200, self.server.platform.update(values.get("action"), values))
        except (ValueError, TypeError) as exc:
            self.send(400, {"error": str(exc)})
        except (URLError, TimeoutError, RuntimeError) as exc:
            LOG.warning("Platform update failed: %s", type(exc).__name__)
            self.send(503, {"error": "Control not confirmed by the platform; retry or reset.", "detail": type(exc).__name__})


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    platform = Platform()
    platform.initialize()
    server = ThreadingHTTPServer(("0.0.0.0", 8088), Handler)
    server.platform = platform
    LOG.info("18 Inkai twins ready through MQTT -> Ditto; UI listening on :8088")
    try:
        server.serve_forever()
    finally:
        platform.client.disconnect()
        platform.client.loop_stop()


if __name__ == "__main__":
    main()
