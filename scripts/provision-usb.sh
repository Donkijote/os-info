#!/bin/sh
set -eu

usage() {
  echo "Usage: $0 --device /dev/WHOLE_DISK --dry-run" >&2
}

device=""
dry_run=false
while [ "$#" -gt 0 ]; do
  case "$1" in
    --device)
      [ "$#" -ge 2 ] || { usage; exit 2; }
      device=$2
      shift 2
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

if [ "$(uname -s)" != "Linux" ]; then
  echo "USB provisioning requires Linux." >&2
  exit 2
fi
if [ -z "$device" ] || [ ! -b "$device" ]; then
  echo "Provide an existing whole block device with --device." >&2
  exit 2
fi
if [ "$dry_run" != true ]; then
  echo "Destructive provisioning is intentionally disabled until physical USB safety tests pass." >&2
  echo "Use --dry-run to inspect a candidate device." >&2
  exit 3
fi

lsblk --json --bytes --output NAME,PATH,TYPE,SIZE,MODEL,VENDOR,TRAN,RM,MOUNTPOINTS "$device"
echo "Dry run only: no partition table or filesystem was changed."

