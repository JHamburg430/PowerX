# Recovery research: actionable leads

Research date: 2026-09-14. Read-only source/documentation investigation; no
network, firmware, app, or running-service changes made.

## 1. BluFi is present in the original APK

The recovered Android native code includes Espressif BluFi, not merely generic
Bluetooth support. Evidence under
`artifacts/com.powerx.consumer.userapp@2.6.17/apktool/smali/`:

- `t8/b.smali:20`: service UUID `0000ffff-0000-1000-8000-00805f9b34fb`.
- `t8/b.smali:29`: write characteristic `0000ff01-0000-1000-8000-00805f9b34fb`.
- `t8/b.smali:38`: notify characteristic `0000ff02-0000-1000-8000-00805f9b34fb`.
- `s8/p.smali`: Flutter plugin dispatch includes `requestDeviceVersion`,
  `requestDeviceStatus`, `negotiateSecurity`, and `postCustomData`.
- `s8/p$c.smali`: callbacks include `device_version`, `device_status`,
  `receive_error_code`, and `receive_device_custom_data`.

Official open-source implementation and documentation:

- https://github.com/EspressifApp/EspBlufiForAndroid
- https://github.com/EspressifApp/EspBlufiForAndroid/blob/master/doc/Introduction_to_the_EspBlufi_API_Interface_for_Android__en.md

Next: inspect the hub's advertised GATT services if Bluetooth becomes available;
use the documented version/status requests before considering configuration.
The returned version must not automatically be called the PowerX firmware
version. Status can contain credentials: retain only explicit non-secret fields,
never dump whole responses. Library presence does not prove the hub currently
advertises BluFi, exposes logs, or accepts a particular custom command. Do not
send guessed custom payloads or overwrite Wi-Fi configuration.

This offers a software-only diagnostic lead, not a proven telemetry interface.

## 2. Identified an actual PowerX engineering partner

Very's first-party case study describes work on PowerX firmware, backend,
hardware certification preparation, and a custom LoRa module:

- https://www.verytechnology.com/case-studies/how-powerx-transformed-their-smart-home-product-line-for-scalability
- https://3440604.fs1.hubspotusercontent-na1.net/hubfs/3440604/Very-PowerX-How-PowerX-Transformed-Their-Smart-Home-Product-Line-for-Scalability.pdf

This is a credible source-request lead, not a public firmware download. A useful
request would ask for a redacted legacy `GET /api/hub/<id>/cert_key` response
schema, discovery contract, firmware image/release manifest, and upload-protocol
documentation. No contact was made and no paid service is proposed.

Public GitHub code searches for the exact discovery hostname and
`cert_key` with PowerX returned no matches. Listing Very's public repositories
and filtering names/descriptions for PowerX, ESP32, provisioning, and LoRa found
no named match. These are bounded negative searches, not proof of nonexistence.

## 3. Phone OTA flow is not a firmware download mechanism

Recovered Flutter assembly under
`blutter/asm/consumer_app/data/firmware_update/data_source/remote/hub_firmware_update_api.dart`
contains GET `/v5/firmware/hubs/<id>/ota/check` and GET/POST
`/v5/firmware/hubs/<id>/ota/manage`. The inspected methods coordinate backend
operations; they do not reveal a hub firmware binary URL or `cert_key` parser.
The original provisioning API POSTs to `/v6/hubs`.

The compatibility server still returns a synthetic registration object and a
hard-coded no-update flag. Those responses must not be treated as evidence of
hardware registration or firmware freshness.

## 4. Existing certificate experiment is inconclusive

`hub-protocol-observations.md` explicitly records that the temporary relay had
restored normal routing before the post-certificate observation was complete.
The ignored `work/hub-diagnostic/empty_cert_probe.py` only observes its HTTPS
listener. No subsequent HTTPS request there does not establish that the hub
rejected `{}` or that firmware extraction is the only remaining route.

Next network experiment, if undertaken: retain bounded hub-only destination
observation across the entire discovery/certificate/retry interval. Record DNS,
destination ports and TLS metadata, including attempts to other hosts. Preserve
the existing cleanup and connectivity checks; do not alter router settings or
PC default routes. Do not invent certificate fields or claim MQTT without
observing evidence.

## 5. Firmware backup remains a fallback, not a reset

Espressif documents serial flash readback using esptool `read-flash`:
https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-commands.html#read-flash-contents-read-flash

This would require identifying the actual board and accessible serial interface;
the hub's power-only USB port is not established as that interface. Security
configuration may restrict readback. No pinout, accessible UART, or readable
firmware has been verified. Do not erase, reflash, or change eFuses to investigate.

## Excluded false leads

- ArtisanCloud/PowerX is unrelated enterprise software.
- The ESP32 developer post at https://www.reddit.com/r/esp32/comments/ifofgr/
  links to Go Smart Blinds, not PowerX. It is not PowerX firmware evidence.
- PowerX telecom/Teltonika and Japanese battery products are not this Terra hub.

## Recommended order

1. Follow BluFi status/version and custom-data call-site evidence without changing
   network configuration; first establish whether the service is available.
2. Correct the post-certificate observation gap before declaring the software
   path exhausted.
3. Seek the legacy contract/firmware from the actual engineering organizations
   if authorized; no outreach has been sent.
4. Consider board-level readback only if software paths cannot supply the needed
   evidence. Preserve the original application and hardware firmware throughout.

No public certificate response schema or matching hub firmware image was found.
Physical registration and readings remain unverified/unrestored.
