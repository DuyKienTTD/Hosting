#!/bin/sh
set -eu
cd "${1:?pinned source directory}"
test "$(git hash-object pnpm-lock.yaml)" = d625f6e977d222c3bbc540de9e7fd2215a4def17
tool=$(realpath "$2")
store=$(realpath "$3")
cache=$(realpath "$4")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir "$tmp/data"
unshare -Urn env -i PATH="$(dirname "$(command -v node)"):/usr/bin:/bin" HOME="$tmp" TMPDIR="$tmp" XDG_CACHE_HOME="$cache" OPENCLAW_STATE_DIR="$tmp/data" CI=1 NO_COLOR=1 sh -c '
python3 -c "import socket,errno; s=socket.socket(); s.settimeout(2); r=s.connect_ex((\"192.0.2.1\",443)); print(\"egress_probe\",r); assert r==errno.ENETUNREACH" || exit 90
node --version
"$1" --version
"$1" install --offline --frozen-lockfile --ignore-scripts --store-dir "$2" || exit 91
"$1" exec vitest run --maxWorkers=1 --config test/vitest/vitest.extension-zalo.config.ts extensions/zalouser/src/send.handoff.test.ts extensions/zalouser/src/send.media-handoff.test.ts
a=$?; echo send_exit=$a
"$1" exec vitest run --config test/vitest/vitest.extension-database-workers.config.ts extensions/zalouser/src/ingress.test.ts extensions/zalouser/src/monitor.group-gating.test.ts extensions/zalouser/src/monitor.account-scope.test.ts
b=$?; echo ingress_exit=$b
exit $((a || b))
' sh "$tool" "$store"
