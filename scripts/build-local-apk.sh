#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APKTOOL_JAR="$ROOT_DIR/.tools/apktool/apktool.jar"
BUILD_TOOLS="${ANDROID_BUILD_TOOLS:-/home/john/.android-build/android-sdk/build-tools/35.0.0}"
INPUT_APK="${1:-$ROOT_DIR/input/com.powerx.consumer.userapp@2.6.17.apk}"
DISCOVERY_URL="${2:-http://100.76.133.101:8080/}"
OLD_URL="https://discovery.powerx.co"
VERSION_CODE="${3:-67}"
VERSION_NAME="${4:-2.6.17-local.2}"
OUTPUT_DIR="$ROOT_DIR/output"
SIGNING_DIR="$ROOT_DIR/signing"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TMP_DIR"' EXIT

if [[ ! -f "$INPUT_APK" ]]; then
  echo "APK not found: $INPUT_APK" >&2
  exit 1
fi
if [[ ! -f "$APKTOOL_JAR" ]]; then
  echo "Apktool not found: $APKTOOL_JAR" >&2
  exit 1
fi
if [[ ${#DISCOVERY_URL} -ne ${#OLD_URL} ]]; then
  echo "Patched discovery URL must be exactly ${#OLD_URL} characters." >&2
  echo "Received ${#DISCOVERY_URL}: $DISCOVERY_URL" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR" "$SIGNING_DIR"
java -jar "$APKTOOL_JAR" d -f -o "$TMP_DIR/decoded" "$INPUT_APK"

python3 - "$TMP_DIR/decoded" "$OLD_URL" "$DISCOVERY_URL" "$VERSION_CODE" "$VERSION_NAME" <<'PY'
from pathlib import Path
import re
import sys

root, old, new = Path(sys.argv[1]), sys.argv[2].encode(), sys.argv[3].encode()
version_code, version_name = sys.argv[4], sys.argv[5]
if len(old) != len(new):
    raise SystemExit("replacement length mismatch")
patched = 0
for target in sorted((root / "lib").glob("*/libapp.so")):
    blob = target.read_bytes()
    count = blob.count(old)
    if count != 1:
        raise SystemExit(f"expected one discovery URL in {target}, found {count}")
    target.write_bytes(blob.replace(old, new))
    patched += 1
if not patched:
    raise SystemExit("no Flutter libapp.so files found")

manifest = root / "AndroidManifest.xml"
text = manifest.read_text()
needle = "<application "
if needle not in text:
    raise SystemExit("application element not found")
text = text.replace(needle, '<application android:usesCleartextTraffic="true" ', 1)
manifest.write_text(text)

apktool_yml = root / "apktool.yml"
yml = apktool_yml.read_text()
yml, code_count = re.subn(r"(?m)^(\s*versionCode:\s*)[^\n]+", rf"\g<1>{version_code}", yml)
yml, name_count = re.subn(r"(?m)^(\s*versionName:\s*)[^\n]+", rf"\g<1>{version_name}", yml)
if code_count != 1 or name_count != 1:
    raise SystemExit("could not update versionCode/versionName in apktool.yml")
apktool_yml.write_text(yml)
print(f"patched {patched} ABIs to {new.decode()}; version {version_name} ({version_code})")
PY

java -jar "$APKTOOL_JAR" b "$TMP_DIR/decoded" -o "$TMP_DIR/unsigned.apk"
"$BUILD_TOOLS/zipalign" -f -p 4 "$TMP_DIR/unsigned.apk" "$TMP_DIR/aligned.apk"

if [[ ! -f "$SIGNING_DIR/powerx-local-key.pem" ]]; then
  openssl genpkey -quiet -algorithm RSA -pkeyopt rsa_keygen_bits:2048 \
    -out "$SIGNING_DIR/powerx-local-key.pem"
  openssl req -new -x509 -key "$SIGNING_DIR/powerx-local-key.pem" \
    -out "$SIGNING_DIR/powerx-local-cert.pem" -days 3650 \
    -subj "/CN=PowerX Local/O=Owner-controlled interoperability build/"
fi
if [[ ! -f "$SIGNING_DIR/powerx-local-key.pk8" ]]; then
  openssl pkcs8 -topk8 -nocrypt -outform DER \
    -in "$SIGNING_DIR/powerx-local-key.pem" \
    -out "$SIGNING_DIR/powerx-local-key.pk8"
fi

OUTPUT_APK="$OUTPUT_DIR/PowerX-Tailscale-$VERSION_NAME.apk"
"$BUILD_TOOLS/apksigner" sign \
  --key "$SIGNING_DIR/powerx-local-key.pk8" \
  --cert "$SIGNING_DIR/powerx-local-cert.pem" \
  --out "$OUTPUT_APK" "$TMP_DIR/aligned.apk"
"$BUILD_TOOLS/apksigner" verify --verbose --print-certs "$OUTPUT_APK"
sha256sum "$OUTPUT_APK"
echo "Built: $OUTPUT_APK"
