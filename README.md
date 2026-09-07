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

See [Research](docs/research.md) and the [APK analysis runbook](docs/apk-analysis.md).

## Next step

Place a legally obtained APK in `input/`, then run:

```bash
./scripts/analyze-apk.sh input/PowerX-Terra.apk
```

The script records hashes, package metadata, archive contents, and embedded
hostnames without modifying the APK. If JADX is installed, it also produces a
decompiled source tree for inspection.

## Project layout

```text
PowerX/
  input/       local APKs (ignored by git)
  artifacts/   generated reports/decompilation (ignored by git)
  docs/        research and runbooks
  scripts/     repeatable analysis tools
  work/        future patch or local-service implementation
```

## Scope and safety

This project is for interoperability and preservation of hardware the operator
owns. Do not publish original APKs, extracted proprietary assets, signing keys,
or personal account/device data. Preserve the original APK and its hashes before
making any changes.

