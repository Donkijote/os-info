# os-info

`os-info` is an experimental, bootable Linux hardware inventory scanner. The finished appliance will boot from USB without using the installed operating system, collect hardware information through Linux utilities, show a simple interface, and export matching Excel and JSON reports to the same USB.

> [!IMPORTANT]
> The project is in early development. There is no tested boot image yet. Do not use development provisioning scripts on a USB containing valuable data.

## Current status

The repository currently supports fixture-driven development on macOS and Linux:

- versioned normalized JSON inventory model
- parsers for representative DMI, CPU, storage, network, and battery fixtures
- validated JSON and Excel report generation
- safe subprocess runner with time and output limits
- testable application/view-model layer

Real Linux hardware collection, boot-image creation, USB provisioning, and cross-vendor physical testing remain separate validation milestones. See the [implementation plan](docs/implementation-plan.md) for the live status.

## Development

Requires Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run pytest
uv run ruff check .
uv run mypy src
uv run hwscan collect --fixture-dir tests/fixtures/dell/latitude-7420 --output build/sample.json
uv run hwscan export --fixture-dir tests/fixtures/dell/latitude-7420 --destination build/sample-report
```

## Releases

No bootable release has been validated yet. When a physical release is ready, it will be published with checksums here:

- [Latest release](https://github.com/Donkijote/os-info/releases/latest)
- [Latest amd64 image](https://github.com/Donkijote/os-info/releases/latest/download/os-info-amd64.img.zst)
- [Latest checksums](https://github.com/Donkijote/os-info/releases/latest/download/SHA256SUMS)

Generated images are GitHub Release assets and are never committed to this repository.

## Safety boundary

The intended appliance must not mount internal filesystems or issue commands that modify detected storage devices. Inventory completion is not equivalent to a hardware diagnostic pass. Missing or unsupported data must remain explicit rather than being guessed.

## License

MIT

