# Release checklist

- [ ] All formatting, lint, typing, unit, contract, and integration checks pass.
- [ ] No generated image or private fixture is tracked by Git.
- [ ] Debian image builds from a clean pinned environment.
- [ ] QEMU BIOS and UEFI boot tests reach the UI.
- [ ] Secure Boot is either verified or explicitly documented as unsupported.
- [ ] Provisioning refuses the system disk, partitions, mounted targets, and undersized devices.
- [ ] Physical USB boots on representative Dell, HP, Lenovo, Intel, and AMD systems.
- [ ] Internal filesystems remain unmounted and receive no writes.
- [ ] JSON validates; Excel reopens; checksums match; reports survive shutdown.
- [ ] Windows can read the exFAT report partition.
- [ ] Fixtures and release logs have been scrubbed of private identifiers.
- [ ] Package manifest, build metadata, checksums, known limitations, and test matrix are attached.
- [ ] The version tag points to tested `main`.

