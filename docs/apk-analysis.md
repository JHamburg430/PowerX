# APK analysis runbook

> Status: the APK was acquired and analyzed. See
> [Local recovery](local-recovery.md) for recovered protocol details and the
> emulator-verified patch.

## 1. Preserve the original

Copy the APK from a device backup or a reputable archive into `input/`. Do not
rename or overwrite the only copy. The analysis script records SHA-256 and
SHA-1 hashes in its report.

If the app is still installed on an Android device, the preferred source is the
installed package because it preserves the exact version previously used with
the hardware:

```bash
adb shell pm path com.powerx.consumer.userapp
```

Use each returned path with `adb pull`. Modern apps may have a base APK plus
split APKs; preserve all of them.

## 2. Static inventory

```bash
./scripts/analyze-apk.sh input/PowerX-Terra.apk
```

Review `artifacts/<apk-name>/report.txt`, especially:

- package and version;
- embedded `powerx.co`, AWS, Cognito, AppSync, API Gateway, MQTT, and WebSocket
  hostnames;
- React Native bundles (`index.android.bundle`) or Flutter libraries;
- `networkSecurityConfig`, certificate-pinning libraries, and cleartext policy;
- login/session models and calls made immediately after login.

## 3. Decompile

Install JADX from its official release and ensure `jadx` is on `PATH`, then
rerun the script. Decompiled output will appear under the report directory.
For React Native, inspect the JavaScript bundle as well as Java/Kotlin wrappers.

## 4. Decide the least invasive recovery

### A. Base-URL compatibility patch

Use when the APK points at a dead host but the same endpoint contract survives
on an owned or verified successor host. Change only the base URL and any network
security policy required for the new hostname.

### B. Local compatibility service

Use when the app expects cloud-shaped JSON but the hub data can be acquired
locally. Implement only observed endpoints, starting with session creation,
current-user/bootstrap, location/device inventory, and water telemetry. Point a
debug build at a LAN hostname. This preserves more of the UI than rewriting it.

### C. New local client/collector

Use when the app is mostly a view over unavailable cloud-derived data. Capture
hub DNS and network traffic, identify its uplink, and determine whether the hub
offers a LAN service. If not, investigate the hub before modifying battery
sensors: it is the powered LoRa receiver and likely the lowest-risk interception
point.

## 5. Verification gates

Before calling a recovery successful, verify:

1. app launches on a currently supported Android version;
2. local identity persists across force-stop and reboot;
3. hub provisioning works without the former cloud;
4. live water flow updates while water is running;
5. totals survive app/service restart;
6. no request is made to an unverified third-party endpoint;
7. the rebuilt APK is signed with a project-owned development key and is clearly
   labeled as an unofficial preservation build.
