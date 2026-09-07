# PowerX

Community preservation project for the discontinued **PowerX Terra** Android
application and PowerX residential utility-monitoring hardware.

## Target

- Android app: **PowerX Terra**
- Package: `com.powerx.consumer.userapp`
- Last known version: `2.6.17` (February 27, 2023)
- Hardware path: Water/Electricity/Water-Heater sensor -> LoRa -> PowerX Hub -> cloud

## Goal

Restore owner-controlled access to personally owned hardware without depending
on the discontinued consumer login service. The first implementation decision
will be based on evidence from the APK:

1. patch an obsolete API base URL if the compatible backend still exists;
2. emulate the minimum legacy API locally and redirect the app to it; or
3. replace the app/cloud path with a local collector if telemetry never reaches
   the phone directly.

An offline login bypass by itself is unlikely to restore readings: public
descriptions and former-user reports say the hub uploaded LoRa sensor data to
AWS for processing.

## Current findings

- No public repository for the Android package or its exact package identifier
  was found in GitHub code/repository search.
- The old `api.live.powerx.co` and `app.powerx.co` hosts no longer resolve.
- `api-v2.live.powerx.co` still responds and exposes a FastAPI OpenAPI document.
  This may be successor infrastructure, so compatibility must be verified from
  the APK before sending any account information.
- The app was removed from Google Play in August 2023. Public catalog records
  identify version `2.6.17` and a roughly 58.7 MB APK.
- Community reports say the residential AWS service was shut down in 2023 and
  the sensors communicate with the hub via LoRa.
- The genuine Play-distributed APK has now been retrieved and verified locally.
  Its SHA-256 is
  `92cccab56cef03f5c5f1188decfc06840e2f58152dfb562fe8d168cdaccb96c3`.
- Flutter AOT recovery identified the dead discovery URL, the authentication
  envelope, and 52 legacy API paths. The recovered login chain is documented in
  [Local recovery](docs/local-recovery.md).
- A gateway-hosted compatibility service and a patched, locally signed APK now
  bypass the dead login service. The build was installed and exercised on an
  Android 15 x86-64 emulator; login and cold-restart session persistence passed.

See [Research](docs/research.md) and the [APK analysis runbook](docs/apk-analysis.md).

## Run the local compatibility service

The checked-in defaults match this gateway's current LAN address
(`192.168.0.250`). Start the service before opening the patched app:

```bash
python3 server/powerx_local.py \
  --bind 0.0.0.0 \
  --port 8080 \
  --advertise-url http://192.168.0.250:8080
```

The service accepts any syntactically valid email/password pair and does not
store or log the submitted password. Keep it on a trusted LAN.

## Rebuild the patched APK

With the original verified APK and local Apktool already present on the gateway:

```bash
./scripts/build-local-apk.sh
```

The output is `output/PowerX-Local-2.6.17.apk`. Because it has an owner-controlled
signature instead of PowerX/Google Play's signature, Android requires the old
PowerX Terra app to be uninstalled before this build can be installed. Preserve
any app-local data first.

## Project layout

```text
PowerX/
  input/       local APKs (ignored by git)
  artifacts/   generated reports/decompilation (ignored by git)
  docs/        research and runbooks
  scripts/     repeatable analysis tools
  server/      local discovery/auth compatibility service
  tests/       compatibility-service tests
  output/      locally signed APKs (ignored by git)
  work/        future hardware/telemetry recovery work
```

## Scope and safety

This project is for interoperability and preservation of hardware the operator
owns. Do not publish original APKs, extracted proprietary assets, signing keys,
or personal account/device data. Preserve the original APK and its hashes before
making any changes.
