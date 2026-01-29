# shell-guard

Git safety hooks for the paranoid.

`shell-guard` is a minimal bash script that prevents you from running critical commands (like releases or major merges) if your git repository is in a "dirty" state (uncommitted changes or untracked files).

## Installation

1. Copy `shell-guard.sh` to your project's `bin/` or `tools/` directory.
2. Make it executable: `chmod +x shell-guard.sh`.

## Usage

Check if the repo is clean before a build:

```bash
./shell-guard.sh --check || exit 1
```

Snapshot current dirty state before an experiment:

```bash
./shell-guard.sh --snapshot
```

## Principles

- **Fail early**: Stop operations before they pollute your history.
- **Traceable**: Snapshot changes if you choose to proceed in a dirty state.
- **Minimalist**: Plain bash, no dependencies.

## License

MIT
