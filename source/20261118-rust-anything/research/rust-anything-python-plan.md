# Rust migration plan: python (Python)

1 packages, 1 source files (46 lines), 0 test files, 0 UI files, grouped into 1 units.

| Ready | Caution | Blocked | Keep in source language |
| ---: | ---: | ---: | ---: |
| 1 | 0 | 0 | 0 |

## Start here

Best first ports: safe to port (readiness) and worth porting (loops and string work, tests, size).

| # | Unit | Lines | Priority | Readiness | Tests | Bridge | Main risks |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `tcli.py` | 46 | 57 | 85 | 0 | PyO3 | String offsets and slicing (2); Division and modulo (2); Dynamic typing (1) |

### `tcli.py`

46 lines in 1 files, wave 0, priority 57, readiness 85, bridge **PyO3**.

- Leaf: imports no other unit.
- No tests found: write characterization tests against the original code first.
- String offsets and slicing x2: `tcli.py:13`, `tcli.py:52`
- Division and modulo x2: `tcli.py:27`, `tcli.py:27`
- Dynamic typing x1: `tcli.py:10`
- Exceptions x3: `tcli.py:19`, `tcli.py:31`, `tcli.py:37`

## Order by package

Packages come after the workspace packages they use. Inside a package, port by wave: a unit's imports are in earlier waves.

### 1. python (`.`, portable, 0 test files)

| Wave | Unit | Status | Lines | Readiness | Bridge | Main risks |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | `tcli.py` | ready | 46 | 85 | PyO3 | String offsets and slicing (2); Division and modulo (2) |

## Risk guide

- **String offsets and slicing** (High): JS indexes strings in UTF-16 code units, Rust in UTF-8 bytes. Offsets that cross the boundary must be converted, or non-ASCII text gets wrong ranges silently.
- **Dynamic typing** (Medium): Values whose shape is checked at runtime need an explicit Rust enum or `serde_json::Value`.
- **Exceptions** (Low): Thrown errors become `Result`. Errors crossing the bridge must map back to the same JS error shape.
- **Division and modulo** (Medium): Python `//` and `%` floor toward negative infinity; Rust `/` and `%` truncate: use `div_euclid`/`rem_euclid` or explicit floor math. C division by zero is undefined.

## Whole app

Shape: **cli**.

| Entry point | Kind | Found from |
| --- | --- | --- |
| `tcli.py` | cli | `if __name__ == "__main__"` at tcli.py:51 |

### Every dependency

None.

### Pieces, in port order

- wave 0: `tcli.py` (46 lines)

### Decisions for the user

**D1** (shape): The app is a cli, entered through tcli.py. Port every entry point, in that shape?

> Yes: a clap front door (`app front-door`) takes every command over first

