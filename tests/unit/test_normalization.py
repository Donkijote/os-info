from hwscan.domain.normalization import (
    clean_identifier,
    excel_safe_text,
    percentage,
    safe_filename_component,
)


def test_rejects_placeholder_identifiers() -> None:
    assert clean_identifier("To Be Filled By O.E.M.") is None
    assert clean_identifier("0000-0000-0000") is None
    assert clean_identifier(" TEST-001 ") == "TEST-001"


def test_calculates_percentage_only_for_valid_values() -> None:
    assert percentage(82, 100) == 82.0
    assert percentage(1, 0) is None
    assert percentage(-1, 100) is None


def test_sanitizes_filenames_and_excel_formulas() -> None:
    assert safe_filename_component("Dell / Latitude 7420") == "Dell-Latitude-7420"
    assert excel_safe_text('=HYPERLINK("bad")') == '\'=HYPERLINK("bad")'
