#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 path/to/app.apk" >&2
  exit 2
fi

apk_path=$1
if [[ ! -f "$apk_path" ]]; then
  echo "APK not found: $apk_path" >&2
  exit 2
fi

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
apk_name=$(basename "$apk_path")
report_name=${apk_name%.apk}
output_dir="$project_dir/artifacts/$report_name"
mkdir -p "$output_dir"
report="$output_dir/report.txt"

{
  echo "PowerX APK static inventory"
  echo "File: $apk_path"
  echo "Analyzed (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  sha256sum "$apk_path"
  sha1sum "$apk_path"
  echo
  echo "Archive inventory"
  unzip -l "$apk_path"
} > "$report"

aapt_path=$(command -v aapt || true)
if [[ -z "$aapt_path" ]]; then
  aapt_path=$(rg --files /home/john/.android-build/android-sdk/build-tools 2>/dev/null | grep '/aapt$' | sort -V | tail -1 || true)
fi

if [[ -n "$aapt_path" ]]; then
  {
    echo
    echo "Package metadata"
    "$aapt_path" dump badging "$apk_path"
    echo
    echo "Manifest"
    "$aapt_path" dump xmltree "$apk_path" AndroidManifest.xml
  } >> "$report"
else
  echo "aapt was not found; package/manifest metadata skipped" >> "$report"
fi

{
  echo
  echo "Embedded network indicators"
  unzip -p "$apk_path" 2>/dev/null \
    | strings \
    | grep -Eio '((https?|wss?|mqtt)://[^[:space:]"<>]+|([[:alnum:]_-]+\.)+(powerx\.co|amazonaws\.com|amazoncognito\.com|appsync-api\.[[:alnum:].-]+|execute-api\.[[:alnum:].-]+))' \
    | sed 's/[),;]*$//' \
    | sort -u \
    || true
} >> "$report"

if command -v jadx >/dev/null 2>&1; then
  jadx --output-dir "$output_dir/jadx" "$apk_path"
else
  {
    echo
    echo "JADX not found; decompilation skipped."
  } >> "$report"
fi

echo "Wrote $report"
