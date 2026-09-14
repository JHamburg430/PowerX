#!/usr/bin/env python3
"""Small owner-controlled compatibility service for the PowerX Terra app."""

from __future__ import annotations

import argparse
import json
import logging
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


LOG = logging.getLogger("powerx-local")

LOCAL_HUB_ID = "e1a687"
HUB_LIST_COMPAT_DELAY_SECONDS = 0.25


def local_hub(hub_id=LOCAL_HUB_ID):
    """Return a schema-compatible placeholder, not evidence of hub connectivity."""
    return {
        "id": hub_id,
        "qr_code": hub_id,
        "hub_name": "Home",
        "connection_status": "disconnected",
        # Original Dart parser at 0x9a567c reads this as bool?, NOT String?.
        # Keep unknown until the physical device protocol establishes status.
        "powerx_status": None,
        "devices": [],
        "connected_users": 0,
        "shared": False,
    }


def envelope(data=None, message="Local compatibility service"):
    return {"code": "success", "message": message, "data": data}


class PowerXHandler(BaseHTTPRequestHandler):
    server_version = "PowerXLocal/0.1"

    def _send_json(self, value, status=HTTPStatus.OK):
        body = json.dumps(value, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _discard_body(self):
        # Deliberately do not log request bodies: login contains a password.
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length:
            self.rfile.read(length)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Allow", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.end_headers()

    def do_GET(self):
        self._route()

    def do_POST(self):
        self._discard_body()
        self._route()

    def do_PUT(self):
        self._discard_body()
        self._route()

    def do_PATCH(self):
        self._discard_body()
        self._route()

    def do_DELETE(self):
        self._discard_body()
        self._route()

    def _route(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        method = self.command
        LOG.info("%s %s", method, path)

        # The patched AOT literal points here. AuthRepoImpl then appends /api.
        if path in ("/", "/x"):
            self._send_json({"url": self.server.advertise_url})
            return

        if path == "/api/v4/auth/login" and method == "POST":
            self._send_json(
                envelope(
                    {
                        "access_token": "powerx-local-access",
                        "refresh_token": "powerx-local-refresh",
                        "full_name": "PowerX Local Owner",
                        "discourse_username": None,
                    },
                    "Signed in locally",
                )
            )
            return

        if path == "/api/v4/auth/token/refresh" and method == "POST":
            self._send_json(
                envelope(
                    {
                        "access_token": "powerx-local-access",
                        "refresh_token": "powerx-local-refresh",
                    }
                )
            )
            return

        if path == "/api/v6/customers" and method == "GET":
            self._send_json(
                envelope(
                    {
                        "id": 1,
                        "full_name": "PowerX Local Owner",
                        "email": "owner@powerx.local",
                        # Do not claim a selected hub until the physical hub is
                        # actually reachable. A synthetic selection sends the
                        # app into Dashboard, whose telemetry loaders never
                        # complete for a nonexistent local hub.
                        "selected_hub_id": None,
                        "preferences": {
                            "currency": "usd",
                            "volume_unit": "gallons",
                            "temperature_unit": "fahrenheit",
                            "number_format": "comma_dot",
                            "time_format": "12_hour",
                        },
                    }
                )
            )
            return

        if path == "/api/v6/hubs/current" and method == "GET":
            self._send_json(envelope(None, "No reachable local hub yet"))
            return

        if path == "/api/v6/hubs" and method == "GET":
            # Terra dispatches FetchHubList from initState before its
            # BlocListener is mounted. The original cloud was slow enough that
            # this race stayed hidden; a loopback response can complete first
            # and leave the splash screen spinning forever. Keep this single
            # response asynchronous from the app's point of view.
            time.sleep(HUB_LIST_COMPAT_DELAY_SECONDS)
            # An empty list is meaningful to Terra: the splash listener opens
            # Setup Hub. Returning a fabricated connected hub instead routes
            # into Dashboard and leaves its telemetry loading indefinitely.
            self._send_json(envelope([]))
            return

        if path == "/api/v6/hubs" and method == "POST":
            # Acknowledge the app request, not a completed hardware operation.
            # No registration is persisted yet. The subsequent status poll
            # must remain non-success until device provisioning is implemented.
            self._send_json(envelope(
                local_hub(),
                "Registration request received; physical provisioning incomplete",
            ))
            return

        firmware_prefix = "/api/v5/firmware/hubs/"
        firmware_suffix = "/ota/check"
        if (
            path.startswith(firmware_prefix)
            and path.endswith(firmware_suffix)
            and method == "GET"
        ):
            # Disable unavailable cloud OTA. This is NOT a firmware freshness
            # check and must never trigger a guessed firmware installation.
            self._send_json(envelope({"hub-ota-required": False}))
            return

        identify_prefix = "/api/v6/devices/identify/"
        if path.startswith(identify_prefix) and method == "GET":
            hub_id = path[len(identify_prefix):] or LOCAL_HUB_ID
            self._send_json(
                envelope(
                    {"qr_code": hub_id, "id": hub_id, "device_type": "hub"}
                )
            )
            return

        hub_prefix = "/api/v6/hubs/"
        if path.startswith(hub_prefix) and method == "GET":
            hub_id = path[len(hub_prefix):] or LOCAL_HUB_ID
            # ProvisioningBloc treats code=success alone as a connected hub,
            # regardless of connection_status. Do not fabricate that signal.
            self._send_json({
                "code": "pending",
                "message": "Physical hub certificate provisioning incomplete",
                "data": local_hub(hub_id),
            })
            return

        if path in ("/api/v6/sensors", "/api/v4/notifications") and method == "GET":
            self._send_json(envelope([]))
            return

        if path == "/api/v4/notifications/unread" and method == "GET":
            self._send_json(envelope({"unread_count": 0}))
            return

        # Keep the app moving while making missing protocol coverage visible.
        LOG.warning("unimplemented endpoint: %s %s", method, path)
        self._send_json(envelope(None, "Endpoint not implemented by PowerX Local"))

    def log_message(self, fmt, *args):
        # Use structured route logging above and suppress the default noisy log.
        return


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--advertise-url",
        default="http://100.76.133.101:8080",
        help="URL reachable by the Android device (without the /api suffix)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    parsed = urlparse(args.advertise_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise SystemExit("--advertise-url must be an absolute HTTP(S) URL")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server = ThreadingHTTPServer((args.bind, args.port), PowerXHandler)
    server.advertise_url = args.advertise_url.rstrip("/")
    LOG.info("listening on %s:%d; advertising %s", args.bind, args.port, server.advertise_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOG.info("stopping")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
