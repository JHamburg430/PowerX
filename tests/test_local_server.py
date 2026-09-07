import json
import threading
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

    def test_empty_hub_list(self):
        self.assertEqual(self.request_json("/api/v6/hubs")["data"], [])


if __name__ == "__main__":
    unittest.main()
