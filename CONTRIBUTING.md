# Contributing to EspressoGuardian Projects

First off, thanks for taking the time to contribute! It's people like you that make these tools better for everyone.

## Our Philosophy

We build tools that solve real problems. We prefer small, focused changes over large refactors.

## How Can I Contribute?

### Reporting Bugs

- Use the **Bug Report** template.
- Provide a clear, reproducible example.
- Mention your environment (OS, Godot version, etc.).

### Suggesting Enhancements

- Use the **Feature Request** template.
- Explain why this enhancement would be useful to others.

### Pull Requests

- **Small changes preferred**: Large PRs are harder to review and more likely to be rejected or asked for split.
- **Tests required**: If you change behavior, you must include a test.
- **Style**: Follow the existing coding style of the repository.

### Repo Guard (Required)

Enable the local pre-commit guard before contributing:

```bash
git config core.hooksPath .githooks
```

## Safety & Ethics

- **Offline-first**: Do not suggest features that require telemetry or cloud connectivity.
- **Determinism**: Avoid introducing non-deterministic behavior in logic.

By contributing, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
