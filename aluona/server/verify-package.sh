#!/usr/bin/env bash
set -euo pipefail
root="${1:-.}"
cd -- "$root"
test -f SHA256SUMS.txt
tr -d '\r' < SHA256SUMS.txt | sha256sum -c -
test -s addon/game/csgo_addons/cs2cm_aluona_localtest/characters/models/aluona/aluona.vmdl_c
test -s addon/game/csgo_addons/cs2cm_aluona_localtest/maps/scripts/aluona_test.vjs_c
printf '%s\n' 'File verification passed. This does not install or test the server.'
