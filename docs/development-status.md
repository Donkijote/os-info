# Development status

Last updated: 2026-08-17

## Verified on the current Mac

- Apple Silicon (`arm64`) development environment created with Python 3.12.
- Public GitHub repository created at `Donkijote/os-info` with `main` as the only branch.
- Normalized inventory model and JSON Schema 1.0.0 implemented.
- Fixture-driven collection implemented for system/DMI, CPU, memory, storage health, graphics, network, battery, and boot/security examples.
- Safe subprocess runner implemented with an executable allowlist boundary, controlled locale/path, timeouts, process-group termination, and bounded captured output.
- Matching JSON, Excel, and SHA-256 manifest export implemented with temporary-file validation and atomic final renames.
- Excel formula-injection protection implemented for untrusted text.
- Testable UI view model and a fixture-driven Tk development screen implemented.
- Formatting, linting, strict type checking, schema validation, and automated tests run locally.

## Scaffolded but not yet validated on Linux

- Linux collector command specifications.
- Debian 13 `live-build` configuration and package list.
- Linux-only image build entry point.
- Destructive USB provisioning remains intentionally disabled; only target inspection is scaffolded.
- GitHub Actions CI configuration.

## Requires an amd64 Linux environment

- Real sysfs, DMI, `lscpu`, `lsblk`, PCI, SMART/NVMe, UPower, EDID, sensor, TPM, and Secure Boot collection.
- Root privilege boundary through systemd and polkit.
- Debian live image build and QEMU BIOS/UEFI boot tests.
- Linux graphical session integration and full-screen appliance behavior.

## Requires a USB and physical target PCs

- Final partitioning/provisioning implementation and destructive safety validation.
- Same-USB report persistence and clean unmount/power-off behavior.
- UEFI, legacy BIOS, and Secure Boot tests.
- Cross-vendor hardware comparisons and HWiNFO cross-checks.
- Verification that the report partition opens on Windows.

