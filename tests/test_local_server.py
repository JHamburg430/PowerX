import json
import threading
import time
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from server.powerx_local import PowerXHandler, envelope


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), PowerXHandler)
        cls.server.advertise_url = "http://192.0.2.1:8080"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request_json(self, path, method="GET", data=None):
        url = f"http://127.0.0.1:{self.server.server_port}{path}"
        request = Request(url, method=method)
        if data is not None:
            request.data = json.dumps(data).encode()
            request.add_header("Content-Type", "application/json")
        with urlopen(request) as response:
            return json.load(response)

    def test_success_envelope(self):
        self.assertEqual(
            envelope({"value": 1}),
            {
                "code": "success",
                "message": "Local compatibility service",
                "data": {"value": 1},
            },
        )

    def test_discovery_response(self):
        self.assertEqual(
            self.request_json("/x?actor=owner%40powerx.local"),
            {"url": "http://192.0.2.1:8080"},
        )

    def test_local_login_response(self):
        response = self.request_json(
            "/api/v4/auth/login",
            method="POST",
            data={"username": "owner@example.test", "password": "not-retained"},
        )
        self.assertEqual(response["code"], "success")
        self.assertEqual(response["data"]["access_token"], "powerx-local-access")

    def test_local_hub_list(self):
        started = time.monotonic()
        hubs = self.request_json("/api/v6/hubs")["data"]
        elapsed = time.monotonic() - started
        self.assertEqual(hubs, [])
        self.assertGreaterEqual(elapsed, 0.20)

    def test_no_current_hub_before_physical_discovery(self):
        customer = self.request_json("/api/v6/customers")["data"]
        current = self.request_json("/api/v6/hubs/current")["data"]
        self.assertIsNone(customer["selected_hub_id"])
        self.assertIsNone(current)

    def test_identify_hub(self):
        device = self.request_json("/api/v6/devices/identify/e1a687")["data"]
        self.assertEqual(device["device_type"], "hub")

    def test_register_and_poll_hub(self):
        registered = self.request_json(
            "/api/v6/hubs", method="POST", data={"hub_id": "e1a687"}
        )
        self.assertEqual(registered["code"], "success")
        self.assertEqual(registered["data"]["id"], "e1a687")
        hub = self.request_json("/api/v6/hubs/e1a687")["data"]
        self.assertEqual(hub["connection_status"], "connected")

    def test_hub_firmware_is_current(self):
        response = self.request_json(
            "/api/v5/firmware/hubs/e1a687/ota/check"
        )
        self.assertEqual(response["code"], "success")
        self.assertFalse(response["data"]["hub-ota-required"])


if __name__ == "__main__":
    unittest.main()
