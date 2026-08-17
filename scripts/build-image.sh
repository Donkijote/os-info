#!/bin/sh
set -eu

if [ "$(uname -s)" != "Linux" ]; then
  echo "Image building requires an amd64 Debian/Linux environment." >&2
  echo "The application and fixtures can still be developed and tested on macOS." >&2
  exit 2
fi

if ! command -v lb >/dev/null 2>&1; then
  echo "live-build is required (Debian package: live-build)." >&2
  exit 2
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)
cd "$project_dir/image"

./auto/config
lb build

