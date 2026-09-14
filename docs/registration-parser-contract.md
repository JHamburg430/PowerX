# Original app registration contract and verified failure

## Evidence, not a replacement application

The recovered ARM64 Dart AOT in the original Terra 2.6.17 APK establishes:

- `data/hub/model/response/hub_information_response.dart`, parser
  `_$HubInformationResponseFromJson` at `0x9a507c`, reads `powerx_status`
  at `0x9a567c` and checks it as **bool?** at `0x9a56bc`/`0x9a56c8`.
  Our previous response supplied the string `"online"`, violating this type.
- `presentation/hub_connection/bloc/provisioning_bloc.dart`,
  `checkHubStatus` at `0xbb8674`, emits `HubConnectSuccessfullyState`
  when the hub-details response has a successful envelope. It does not
  independently verify `connection_status` or physical reachability.
- `configuration/data/common/base_response.dart`, `isOk` at `0x77b318`,
  compares the lowercased envelope code to `success`.
- The provisioning POST is `/api/v6/hubs`. Subsequent hub-details parsing and
  firmware coordination are separate from the hardware's `/api/hub/.../cert_key`.

### Hub information field types

| Type | Fields |
| --- | --- |
| `String?` | id, qr_code, area, city, connection_status, country, created_at, downtime, hub_name, signal_strength, state, updated_at, uptime, wifi_id |
| `int?` | connected_users |
| `num?` | lat, lng |
| `bool?` | powerx_status, shared |
| `List?` | devices |

## End-to-end emulator comparison

Used the existing `powerx_test` Android emulator, not John's phone.

1. Original patched app against the previous live backend: Ethernet setup,
   manual QR entry, Hub Info, Done, firmware screen, Continue ->
   **WARNING / Can't register Hub**. This reproduced the reported failure.
2. Same original app logic, changing only the discovery address to an isolated
   loopback fixture: the corrected nullable boolean and a success envelope ->
   **Hub Connected Successfully / Next, connect your PowerX Sensor / Add Sensor**.

The fixture deliberately exercises the success parser. It is **not** evidence
that the physical hub is connected. It binds only `127.0.0.1:18080`, reached by
the emulator through `10.0.2.2`. Its APK and screenshot remain ignored test
artifacts; the test APK is not a release for the user's phone.

## Live behavior

The deployed service now sends `powerx_status: null`, not an invented online
status. Hub-details polling returns `code: pending` while physical certificate
provisioning is incomplete. Otherwise the original app would falsely announce
connection solely because of `code: success`.

The registration POST still only acknowledges receipt and does not persist
registration; this remains unfinished. The OTA flag disables unavailable cloud
updates, not a verified firmware-freshness check. The app's original firmware
screen wording therefore must not be interpreted as a device measurement.

All eight server tests pass. Live loopback and Tailscale hub-details responses
were checked after restarting **only** `powerx-local.service`; the first
immediate readiness probe raced startup, then both endpoints returned the
expected typed pending response. Internet HTTPS, physical hub ping, and the
unchanged PC default route were verified.

## Remaining boundary

Real registration/readings require the physical hub's certificate response
contract and subsequent protocol. No such parser or bundled firmware image was
found in the inspected APK assets and application methods. A read-only request
for our known hub's certificate route on the surviving successor API returned
HTTP 404; no response contents or credentials were retained/published.

Do not repeat synthetic app success or empty certificate responses as evidence
of hardware recovery. Next useful evidence is a firmware image, a read-only
device log, or the historical hardware provisioning schema.
