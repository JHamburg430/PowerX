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

## Certificate-contract investigation

- A subsequent bounded test observed `User-Agent: ESP32 HTTP Client/1.0`
  on both discovery and `cert_key` requests. This identifies the HTTP client,
  not the exact firmware version or board model.
- Returning HTTP 200 with an empty JSON object at `cert_key` produced no further
  request to the diagnostic HTTPS listener during the observation window.
  No key material was sent. This does not establish whether the hub rejected
  the object, retried elsewhere, or attempted another protocol: the temporary
  DNS relay had already restored the normal router mapping.
- TCP connection checks on 22, 23, 80, 443, 1883, 3232, 8080 and 8883 found
  no reachable listener. This is not an exhaustive port/service inventory.
- The publicly available `https://api-v2.live.powerx.co/openapi.json` was
  downloaded and inspected. It contains no `cert_key` or hub certificate
  contract; no actual device credential endpoint was queried.
- Targeted public searches and recovered app text did not reveal that contract.
  A hub firmware image, source, or device-side diagnostic output remains the
  best evidence for identifying the expected field names and downstream host.
  Do not infer an MQTT implementation merely from the certificate endpoint name.

Both temporary diagnostic containers were stopped afterward. The LAN HTTPS
listener was removed; Tailscale listeners remained. Hub ping, PowerX HTTP,
Internet HTTPS and the unchanged PC default route were checked successfully.

## Continuous post-certificate observation

A follow-up retained the identity-checked hub-only relay throughout a nominal
150-second observation (last HTTPS request at 152.9 seconds during cleanup).
The HTTPS listener and relay ran together; discovery did not terminate capture.
There were **86 discovery requests and 86 cert_key requests**, each pair using
TLS 1.2. The certificate endpoint returned HTTP 200 with `{}`, as before.

The hub repeatedly restarted discovery instead of advancing. No other routed
IPv4 destination was observed by this one-way relay (`forwarded: 0`); discovery
DNS queries were answered locally. This is bounded evidence, not an exhaustive
claim about every packet or protocol. It closes the earlier observation gap and
strongly identifies the empty certificate response as insufficient to progress;
it does not reveal required fields or prove MQTT usage.

The relay completed normally and sent corrective router ARP mappings. Temporary
diagnostic containers were stopped. No certificate/key provisioning payload,
firmware, router configuration, PC route, firewall or forwarding-sysctl changes
were applied. Local diagnostic TLS keys remained private and were not published.
The original app and login compatibility service were unchanged.

Next evidence must identify the real certificate contract (firmware/parser,
redacted historical response, or device-side diagnostics). Repeating empty JSON
or falsely marking the hub registered is not a recovery implementation.
