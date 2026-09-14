# Physical hub protocol observations — 2026-09-14

These observations are from the Ethernet hub itself, not inferred from the app
or compatibility-server test responses.

## Confirmed startup sequence

1. The hub repeatedly queries DNS for `discovery.powerx.co`. The name currently
   returns NXDOMAIN through the working LAN resolver.
2. A temporary, hub-only DNS answer directed it to a local HTTPS listener.
3. The hub completed TLS 1.2 with a newly generated self-signed certificate for
   `discovery.powerx.co`, and sent `GET /?actor=...`.
4. Given `{"url":"https://<local-server-address>"}`, it connected to that
   address over TLS 1.2 and requested:
   `GET /api/hub/<PHUB_identifier>/cert_key`.
5. The diagnostic returned HTTP 503 at that point. No certificate/key payload,
   registration success, firmware response, or telemetry was fabricated.

This demonstrates that local discovery is feasible on this unit without
reflashing. It does **not** establish the `cert_key` response schema, whether
later connections validate certificates, or the sensor/upload protocol.
The phone registration API and this hardware provisioning API are distinct.

## Diagnostic scope and cleanup

- Confirmed the physical target by the earlier unplug/reconnect experiment and
  checked hub/router MAC identities before each relay test.
- Used bounded, one-way layer-2 relaying for this hub only. Other traffic,
  default routes, forwarding sysctls, firewall and router settings were untouched.
- Temporary discovery DNS answers used TTL zero. Each relay sent corrective
  router ARP mappings on completion. This records packets sent, not proof of
  the hub's internal ARP cache contents.
- Logged destination metadata and HTTP method/path/query-key names, not
  credentials, query values, headers, or bodies.
- Stopped both diagnostic containers. Verified hub ping replies, unchanged PC
  default route, working Internet HTTPS, and removal of the LAN TLS listener.
- Raw local diagnostic scripts/logs remain under ignored `work/hub-diagnostic/`.

## Next implementation boundary

Establish the actual `cert_key` schema and subsequent device connection protocol
before implementing provisioning. Preserve the original app and hub logic;
do not treat a synthetic registration success as restored hardware operation.
Physical registration and readings remain unrecovered.
