# Privacy and safety contract

Hardware reports can contain chassis, board, memory, storage and battery serials; UUIDs; asset tags; MAC addresses; and operator notes.

The appliance must:

- remain offline by default;
- never mount an internal filesystem;
- never read user files from installed operating systems;
- never start storage self-tests or issue device-modifying commands;
- keep raw evidence in volatile `/run` storage unless a diagnostic bundle is explicitly requested;
- mount the reports partition with `nosuid,nodev,noexec`;
- treat all firmware/device strings as hostile input;
- prevent spreadsheet formula injection;
- label unavailable or contradictory information rather than guessing;
- require explicit confirmation before any USB provisioning operation.

Only small, scrubbed or synthetic fixtures may be committed. Real captures must be placed in `private-fixtures/`, which is ignored, until identifiers have been removed and the fixture metadata declares its origin and redaction status.

