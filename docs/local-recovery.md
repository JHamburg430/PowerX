# Local recovery implementation

## What was recovered

PowerX Terra 2.6.17 is a Flutter AOT application built with Dart 2.18.4. JADX
exposes the Android wrapper but not the Dart application logic, so the ARM64
`libapp.so` snapshot was recovered with Blutter.

The production login sequence is:

1. `GET https://discovery.powerx.co/?actor=<email>`
2. Read `{ "url": "<tenant origin>" }` and append `/api`.
3. `POST <tenant origin>/api/v4/auth/login` with JSON keys `username` and
   `password`.
4. Accept a base envelope whose `code`, case-insensitively, equals `success`.
5. Save `access_token`, `refresh_token`, and `discovery_url` in preferences.

The login data object contains:

- `access_token` (required string)
- `refresh_token` (required string)
- `full_name` (optional string)
- `discourse_username` (optional string)

The APK includes 52 distinct legacy API route literals. Important follow-on
routes include `/v6/hubs`, `/v6/hubs/current`, `/v6/sensors`,
`/v6/consumptions/pipes/`, and `/v6/live/`.

## Patch method

The 27-byte AOT string `https://discovery.powerx.co` is replaced in each
`libapp.so` with the equal-length gateway URL
`http://192.168.0.250:8080/x`. Equal length avoids corrupting Dart's compiled
string metadata. The manifest is rebuilt with `usesCleartextTraffic=true`, the
APK is zip-aligned, and it is signed with a locally generated owner key.

The local service returns its advertised root from `/x`; the app itself appends
`/api`. The service currently implements discovery, login, token refresh,
customer defaults, empty hub/sensor lists, and notification defaults. It logs
method/path for unknown routes but intentionally discards bodies without
logging them.

## Verification performed

- Original APK package/version/certificate and v1/v2/v3 signatures verified.
- Patched URL found in ARM32, ARM64, and x86-64 libraries.
- Patched APK package remains `com.powerx.consumer.userapp`, version code 66,
  version name 2.6.17.
- Patched APK zip alignment and v1/v2/v3 signatures verified.
- Installed and cold-launched on an Android 15 Google APIs x86-64 emulator.
- Entered a dummy email/password; gateway observed discovery, login, and hub
  requests.
- App navigated to **Setup Your Hub** and remained authenticated after a forced
  stop and cold restart.

## Current boundary

This restores local authentication and reaches the hub-setup workflow. It does
not yet restore historical or live readings. The original architecture sent
sensor data over LoRa to the PowerX Hub and then to PowerX's discontinued cloud
service. The next recovery phase requires a real hub and sensor on the LAN to
observe provisioning and upload behavior, then either redirect the hub or
replace its cloud ingestion endpoint with a local collector.
