# shell-guard 🛡️

**Additional Git safety hooks.**

`shell-guard` is a lightweight bash utility designed to protect your repository from accidental commits during "dirty" states. It ensures that critical operations—like releases or merges—only proceed when your working directory is clean, or after a safety snapshot has been taken.

## Features

- **Deterministic**: Validates your git state before you execute irreversible commands.
- **Safety Snapshots**: Automatically archives diffs and untracked files into `.guardian/snapshots/` if you're working in a dirty repo.
- **CI-Ready**: Returns standard exit codes for easy integration into build pipelines.

## Installation

1. Drop `shell-guard.sh` into your project's `bin/` or `scripts/` folder.
2. Grant execution permissions: `chmod +x shell-guard.sh`.

## Usage

**Halt if repo is dirty:**

```bash
./shell-guard.sh --check || exit 1
```

**Force a state snapshot:**

```bash
./shell-guard.sh --snapshot
```

## Principles

- **Fail-Fast**: Catch configuration and state drift before it enters your history.
- **Risk-Averse**: Designed to prioritize data safety by observing and archiving state rather than modifying it.
- **Zero Dependencies**: Pure bash. Works everywhere git does.

## Disclaimer

This software is provided "as is", without warranty of any kind. While designed to be non-destructive, always verify scripts before running them in your environment.

## License

MIT
