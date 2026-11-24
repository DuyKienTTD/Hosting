#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
archive=$(realpath "${1:?path to the pinned win32 x64 archive required}")
printf '%s  %s\n' 6665772ce7a3cec17925f6a8fbdb5f678d758fcbe7b86dca818d12832e084771 "$archive" | sha256sum -c
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
unzip -q "$archive" -d "$stage"
mv "$stage/electron.exe" "$stage/TTD-Zalo-Assistant.exe"
rm -f "$stage/resources/default_app.asar"
mkdir -p "$stage/resources/app" artifacts
cp -r dist "$stage/resources/app/dist"
printf '%s\n' '{"name":"ttd-zalo-assistant","version":"0.1.0","type":"module","main":"dist/main.js"}' > "$stage/resources/app/package.json"
bundle="$PWD/artifacts/TTD-Zalo-Assistant-MVP01-win-x64.zip"
(
  cd "$stage"
  zip -q -r "$bundle" .
)
unzip -tq "$bundle"
sha256sum "$bundle"
