.PHONY: sync test lint typecheck fixtures verify sample

sync:
	uv sync --extra dev

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

fixtures:
	uv run python scripts/check-fixtures.py

verify: fixtures lint typecheck test

sample:
	uv run hwscan export --fixture-dir tests/fixtures/dell/latitude-7420 --destination build/sample-report
