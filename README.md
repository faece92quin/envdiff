# envdiff

> Compare `.env` files across environments and surface missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff
pip install .
```

---

## Usage

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DEBUG
  - STRIPE_TEST_KEY

Mismatched values:
  - DATABASE_URL  (values differ between files)

✔ All other keys match.
```

You can also compare more than two files at once:

```bash
envdiff .env.development .env.staging .env.production
```

### Options

| Flag | Description |
|------|-------------|
| `--keys-only` | Ignore value mismatches, check keys only |
| `--quiet` | Exit with a non-zero code if differences are found (useful in CI) |
| `--json` | Output results as JSON |

---

## License

This project is licensed under the [MIT License](LICENSE).