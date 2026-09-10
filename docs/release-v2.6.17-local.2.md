# PowerX `v2.6.17-local.2`

This release moves the compatibility endpoint from the gateway's LAN address to
its private Tailscale IPv4 address, `100.76.133.101:8080`. PowerX can therefore
log in while the phone is away from home, provided Tailscale is connected.

Changes:

- Patch discovery to `http://100.76.133.101:8080/`.
- Advertise the same Tailscale endpoint from the compatibility service.
- Raise Android `versionCode` from 66 to 67 for an in-place Obtainium update.
- Set `versionName` to `2.6.17-local.2`.

The service remains private to devices authorized on John's tailnet. It is not
published with Tailscale Funnel and is not exposed to the public internet.

APK SHA-256:

```text
eb658e2015bcc86910b9b69b60558064db8e13e0acaf30435eaa88a58e7aa5fb
```
