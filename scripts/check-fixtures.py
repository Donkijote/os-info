#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

MAX_FIXTURE_BYTES = 1024 * 1024


def main() -> int:
    fixture_root = Path("tests/fixtures")
    errors: list[str] = []
    for metadata_path in fixture_root.rglob("fixture-metadata.json"):
        directory = metadata_path.parent
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("contains_real_identifiers") is not False:
            errors.append(f"{directory}: identifiers must be declared absent")
        for path in directory.iterdir():
            if path.is_file() and path.stat().st_size > MAX_FIXTURE_BYTES:
                errors.append(f"{path}: fixture exceeds {MAX_FIXTURE_BYTES} bytes")
    data_directories = {
        path.parent for path in fixture_root.rglob("*.json") if path.name != "fixture-metadata.json"
    }
    metadata_directories = {path.parent for path in fixture_root.rglob("fixture-metadata.json")}
    for directory in sorted(data_directories - metadata_directories):
        errors.append(f"{directory}: missing fixture-metadata.json")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Validated {len(metadata_directories)} scrubbed fixture set(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
