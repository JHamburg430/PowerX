# Research notes

Research date: 2026-09-07

## Identity

The discontinued residential app is **PowerX Terra**, Android package
`com.powerx.consumer.userapp`. AppBrain records the final Android release as
`2.6.17`, approximately 58.7 MB, updated February 27, 2023 and removed from
Google Play August 11, 2023.

Source: <https://www.appbrain.com/app/powerx-terra/com.powerx.consumer.userapp>

This is distinct from several unrelated current apps named PowerX.

## Architecture evidence

PowerX described the suite as sensors communicating with a central hub over
LoRa. Contemporary discussion with the founder described the hub forwarding
sensor data to the cloud for processing and inference.

Sources:

- <https://www.prnewswire.com/news-releases/save-money-save-the-planet-powerx-now-taking-pre-orders-for-energy-saving-and-carbon-slashing-iot-products-301319078.html>
- <https://www.reddit.com/r/homeassistant/comments/lrmqp1/just_got_off_the_phone_with_powerx_and_im_super/>
- <https://f.hubspotusercontent10.net/hubfs/678511/210701_-_PowerX_-_Manual_Water.pdf>

A 2025 owner report says AWS services were shut down in 2023 and confirms that
the hardware became unusable through the supported path. Another owner opened a
water sensor but did not report a working replacement firmware or integration.

Source: <https://www.reddit.com/r/homeassistant/comments/1j1gv5j/power_x_electric_and_water_sensors_flashed_into_ha/>

## Source-code search

GitHub repository and code searches were run for:

- `PowerX Terra`
- `com.powerx.consumer.userapp`
- `api-v2.live.powerx.co`
- the API operation identifier `post_auth_session_v3_auth_session_post`

No matching public app or backend source was found. A repository named PowerX
from ArtisanCloud is unrelated.

## Surviving infrastructure

Certificate-transparency history exposes several former `powerx.co` subdomains.
Direct checks on 2026-09-07 found:

| Host | Result |
| --- | --- |
| `app.powerx.co` | DNS failure |
| `api.live.powerx.co` | DNS failure |
| `pxapi.powerx.co` | DNS failure |
| `api-v2.live.powerx.co` | HTTPS responds; `/openapi.json` is available |

The surviving API identifies itself as `powerx-api` version `0.1.0`, served by
Uvicorn, with about 290 documented routes. It includes `/v3/auth/session`,
locations, gateways, electric sensors, and telemetry routes, but the current
schema appears enterprise-oriented and contains no obvious residential water
route. It may be successor infrastructure rather than a drop-in Terra backend.

Do not submit real credentials to this host until the APK confirms the hostname,
route contract, and certificate expectations.

## Existing-solution preflight

No maintained Home Assistant integration, custom firmware, source release, or
completed community recovery for this exact hardware was found. Generic ESPHome
meter projects are not drop-in compatible because the PowerX water sensor uses
an ultrasonic measurement design and proprietary LoRa/hub framing.

## Working conclusion

The APK is the missing primary artifact. It should reveal:

- framework (native, React Native, Flutter, etc.);
- production API hostname and route versions;
- authentication response shape and locally persisted session state;
- certificate pinning or network-security configuration;
- hub provisioning transport (LAN, BLE, Wi-Fi AP, or server-mediated);
- whether raw/local telemetry paths exist but were hidden from the UI.

Only after that inspection should the project choose between a small base-URL
patch, a local compatibility server, or a hardware-protocol recovery.

