from pathlib import Path

import pytest

from hwscan.infrastructure.collectors.fixture import FixtureCollector
from hwscan.infrastructure.exporters.json_exporter import validate_report

FIXTURE = Path("tests/fixtures/dell/latitude-7420")


def test_complete_fixture_matches_schema() -> None:
    validate_report(FixtureCollector(FIXTURE).collect().as_dict())


def test_invalid_schema_version_is_rejected() -> None:
    data = FixtureCollector(FIXTURE).collect().as_dict()
    data["schema_version"] = "2.0.0"
    with pytest.raises(ValueError, match="schema_version"):
        validate_report(data)
