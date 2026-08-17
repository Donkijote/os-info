# Field source precedence

This document records intended precedence. Linux execution remains pending until it is validated on target hardware.

| Domain | Preferred source | Fallback | Rule |
|---|---|---|---|
| System identity | `/sys/devices/virtual/dmi/id` | `dmidecode` | Reject known placeholders and all-zero UUIDs. |
| Board and firmware | sysfs DMI | `dmidecode`, then `lshw` | Preserve disagreements as diagnostics. |
| CPU | `lscpu --json` | `/proc/cpuinfo` | Keep current and rated frequencies distinct. |
| RAM total | kernel usable memory | SMBIOS installed memory | Report both values; do not force them to match. |
| RAM modules | SMBIOS type 17 | `lshw` | Do not convert empty slots into installed modules. |
| Storage topology | explicit-column `lsblk --json --bytes` | udev/sysfs | Never mount detected filesystems. |
| Storage health | `smartctl --json` / `nvme-cli -o json` | unavailable diagnostic | Do not infer universal ATA wear percentages. |
| PCI/GPU | numeric `lspci` IDs and bound driver | `lshw` | Dedicated VRAM remains unknown without an authoritative source. |
| Network | `ip -json link`, sysfs | `lshw` | Do not connect to a network. |
| Battery | UPower and power-supply sysfs | DMI type 22 | Compute health only from compatible positive units. |
| Boot/security | EFI sysfs and `mokutil` | presence-only result | UEFI and Secure Boot are separate fields. |

