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

## Valid local certificate format experiments — 2026-09-15 UTC

Two bounded runs tested a newly generated RSA-2048 self-signed certificate with
clientAuth extended usage and its matching PKCS#8 PEM private key. Public-key
comparison confirmed the pair matches. Key files remain private in ignored
local diagnostic storage and were not printed or committed.

These were explicitly experimental layouts, not recovered PowerX contracts:

| Response layout | Certificate responses |
| --- | ---: |
| cert / key | 14 |
| certificate / private_key | 14 |
| certificatePem / keyPair.PrivateKey | 14 |
| certificatePem / privateKey | 13 |
| data.cert / data.key | 14 |
| cert_key.cert / cert_key.key | 15 |
| certificate / key | 10 |
| cert / private_key | 10 |
| cert_pem / key_pem | 11 |
| client_cert / client_key | 12 |
| data.certificate / data.key, code=success | 11 |
| certificatePem / privateKey / ca / url | 11 |
| Raw PEM certificate followed by key | 11 |
| Raw PEM key followed by certificate | 13 |

Total: **173 certificate responses**. Every observed sequence returned to
startup discovery/cert_key; no new HTTPS endpoint or telemetry was observed.
The relay saw one ICMP packet to the router in the first run and no forwarded
IPv4 packets in the second. This does not identify the firmware's failure
branch or establish that manufacturer-signed credentials are necessary.

Limitations: all responses used HTTP 200, Content-Length, Connection: close and
application/json (including the two raw PEM probes). The tested certificate is
self-signed, starts at the experiment date, and uses one key encoding. Unknown
field names, content type, chain requirements, clock validation, additional
configuration, encoding, or signature checks remain possible. No claim is made
that these tests exhaust valid local provisioning. Do not repeat them as new
progress without changing a specific evidence-backed variable.

Both runs retained the hub-only relay through cleanup and sent corrective ARP.
The active diagnostic container was then stopped. Hub ping passed 2/2; Internet
HTTPS and PowerX Tailscale health returned HTTP 200. The original PC default
route remained unchanged and the temporary LAN HTTPS listener was gone.
Existing passive capture and DNS services were preserved. No router settings,
PC routes, application code or firmware image were modified. Whether the hub
persisted any supplied certificate material is not observable from these tests.

A documentation-only request to the documented engineering partner, Very, is
prepared locally at work/hub-diagnostic/legacy-protocol-request.txt. It asks for
the response schema, validation requirements, downstream protocol and publicly
releasable firmware/diagnostics, without private identifiers or credentials.
No outreach was sent; permission was requested separately. Physical registration
and real readings remain unresolved.
