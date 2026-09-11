# PowerX `v2.6.17-local.3`

This release packages a new Obtainium-installable build alongside local
compatibility-service fixes for the PowerX app's startup loading flow.

Changes:

- Return a selected local hub from login and current-hub requests.
- Implement local hub identification, registration, lookup, and firmware-check
  responses used by the original setup flow.
- Delay the initial hub-list response briefly to avoid the app's startup
  listener race that could leave the loading screen visible indefinitely.
- Raise Android `versionCode` from 67 to 68 for an in-place Obtainium update.
- Set `versionName` to `2.6.17-local.3`.

The APK continues to use the private Tailscale endpoint
`http://100.76.133.101:8080/`. Tailscale must be connected on the Android
device. The physical hub's telemetry and discontinued cloud protocol remain a
separate recovery task.

APK SHA-256:

```text
d58669a5abcefd4d5824bb955b2841c439d2d8712de59bd544ceb3eea4044ab3
```

## Server-side loading correction

The initial release server fabricated a connected hub so the app would enter
Dashboard. Because no physical hub or telemetry stream was available, the
Dashboard loaders could not complete. The compatibility service now returns an
empty hub list and no selected/current hub until hardware discovery succeeds.
The recovered splash state machine treats that as **Setup Hub**. This correction
does not change the APK and therefore does not require a new Obtainium build.
