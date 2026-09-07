# PowerX Local v2.6.17-local.1

First owner-controlled recovery release for PowerX Terra 2.6.17.

## Included

- Redirects the discontinued PowerX discovery service to the local gateway at
  `192.168.0.250:8080`.
- Restores local email/password login through the included compatibility server.
- Preserves the authenticated session across app restarts.
- Reaches the original **Setup Your Hub** workflow.
- Supports ARM32, ARM64, and x86-64 Android devices.

## Installation

The APK is signed with the PowerX Local owner key, not the former Play Store
key. Uninstall the Play Store version before the first PowerX Local install.
Subsequent PowerX Local releases can update in place as long as the gateway's
signing key is preserved.

Use a dummy syntactically valid email and password. The local service does not
retain or log submitted passwords.

## Verification

- Package: `com.powerx.consumer.userapp`
- Android version code: `66`
- Android version name: `2.6.17`
- APK SHA-256:
  `d7a2245969ef267d03b1c54e9fdf0582f02df5c9d1a688f067ea4d719390684a`
- APK signatures: v1, v2, and v3 verified
- Tested by install, login, navigation, and cold restart on Android 15 x86-64

This release restores authentication, not live sensor readings. Recovering
telemetry requires testing the physical PowerX Hub's provisioning and upload
behavior against a local collector.
