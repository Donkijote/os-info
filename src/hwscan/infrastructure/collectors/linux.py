from __future__ import annotations

import platform

from hwscan.infrastructure.command_runner import CommandSpec

LINUX_COMMANDS = {
    "lscpu": CommandSpec("cpu", ("/usr/bin/lscpu", "--json")),
    "lsblk": CommandSpec(
        "storage-topology",
        (
            "/usr/bin/lsblk",
            "--json",
            "--bytes",
            "--output",
            "NAME,PATH,TYPE,TRAN,VENDOR,MODEL,SERIAL,SIZE,ROTA,RM,WWN",
        ),
    ),
    "ip-link": CommandSpec("network", ("/usr/sbin/ip", "-json", "link")),
    "smartctl-scan": CommandSpec(
        "storage-health-scan", ("/usr/sbin/smartctl", "--scan-open", "--json")
    ),
    "nvme-list": CommandSpec("nvme", ("/usr/sbin/nvme", "list", "-o", "json")),
    "lshw": CommandSpec("fallback", ("/usr/bin/lshw", "-json", "-notime"), 30.0),
}


def linux_collection_supported() -> bool:
    return platform.system() == "Linux"
