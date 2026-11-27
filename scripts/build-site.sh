#!/bin/sh
# Assembles brand-studio's web pages into one folder. The catalog repo (zepedrosilva/plugins) runs this
# to publish them at zepedro.com/plugins/brand-studio/.
# Usage: sh scripts/build-site.sh <out-dir>
set -eu
out="${1:?usage: build-site.sh <out-dir>}"
cd "$(dirname "$0")/.."
mkdir -p "$out"
cp -R site/. "$out/"
cp -R examples/brand-studio/brand "$out/example"
cp -R examples/brand-studio/screenshots "$out/screenshots"
rm -f "$out/example/live/server.json"
echo "build-site: wrote $out"
