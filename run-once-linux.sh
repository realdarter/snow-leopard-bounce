#!/usr/bin/env bash
set -euo pipefail

if [[ $(uname -s) != Linux || $(uname -m) != x86_64 ]]; then
    echo 'This download needs 64-bit Linux.' >&2
    exit 1
fi
if [[ -z ${DISPLAY:-} ]]; then
    echo 'This app needs an X11 or XWayland desktop.' >&2
    exit 1
fi

run_dir=$(mktemp -d "${TMPDIR:-/tmp}/SnowLeopardBounce-XXXXXXXX")
cleanup() {
    if [[ -d $run_dir && ! -L $run_dir ]]; then
        rm -rf -- "$run_dir"
    fi
}
trap cleanup EXIT

archive="$run_dir/app.tar.gz"
curl --fail --location --silent --show-error \
    'https://github.com/realdarter/snow-leopard-bounce/releases/latest/download/SnowLeopardBounce-Linux-x86_64.tar.gz' \
    --output "$archive"
tar -xzf "$archive" -C "$run_dir"
app="$run_dir/SnowLeopardBounce/SnowLeopardBounce"
if [[ ! -x $app ]]; then
    echo 'The Linux download did not contain SnowLeopardBounce.' >&2
    exit 1
fi
"$app"
