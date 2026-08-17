from pathlib import Path

from hwscan.infrastructure.collectors.fixture import FixtureCollector

FIXTURE = Path("tests/fixtures/dell/latitude-7420")


def test_collects_normalized_inventory() -> None:
    report = FixtureCollector(FIXTURE).collect()
    assert report.system["product_name"] == "Latitude 7420"
    assert report.system["serial_number"] == "TEST7420"
    assert report.cpus[0]["physical_cores"] == 4
    assert report.memory["installed_bytes"] == 17179869184
    assert report.memory["slots_populated"] == 2
    assert report.storage[0]["estimated_life_remaining_percent"] == 97
    assert report.batteries[0]["health_percent"] == 82.0
    assert len(report.network) == 1
    assert report.boot["mode"] == "uefi"
    assert len(report.sources) == 9
