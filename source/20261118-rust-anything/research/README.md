<p align="center">
  <img src="docs/assets/logo.svg" width="160" height="160" alt="The rust-anything crab, its mouth a code tag">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">by <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><em>Rewrite your whole app in Rust. Keep it working the whole way.</em></p>

<p align="center"><em>CLIs, servers and libraries, piece by piece, checked against the original at every step.</em></p>

<p align="center">Node.js and TypeScript · Python · C · Go · Ruby · Java · PHP and C# in preview</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io version"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm version"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 languages">
  <a href="#works-with"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="Works with 4 agents"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT license"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub stars"></a>
</p>

<p align="center">up to 20x faster · 38,251 recorded cases replayed · 0 mismatches · one command</p>

<p align="center">
  <img src="docs/assets/race.gif" alt="Typing user.profile into x18n's search over 50,000 keys: TypeScript spends 143 ms, the rust-anything batch 6.9 ms, with the same results at every keystroke." width="820">
</p>

**Rewrite your whole app in Rust, one piece at a time.** rust-anything records what your
Node.js (TypeScript/JavaScript), Python, C, Go, Ruby or Java app does today, then checks every piece of the
Rust rewrite against that recording before it moves on, until the app is pure Rust. CLIs, HTTP
servers and libraries; your coding agent (or you) writes the Rust. It can only catch what the
recording covers: see [What it can't catch](#what-it-cant-catch). Only need the slow part fast?
Port just that, one hot path at a time:

| Real workload, same results as the original | Original | With rust-anything |
| --- | ---: | ---: |
| x18n's sidebar search, 50,000 keys (TypeScript, Node) | 10 ms per query | **0.5 ms: 20x faster** |
| The same search in the browser (wasm, one thread) | 10 ms | **0.95 ms: 11.5x** |
| `slugify` over 20,000 strings (Python) | 98 ms | **17x faster** |
| `Shellwords.shellescape` from Ruby's standard library, 50,000 values | 88 ms | **11.8x faster** |
| `Slugify` over 50,000 strings (Go) | 49 ms | **4x faster** |
| `slugify` over 50,000 strings (Java) | 43 ms | **3x faster** |

Measured on 4 cores; every number has a benchmark in [`demo/`](./demo) that first checks the
results are identical. Calling Rust once per small function is usually *slower* than a JIT;
rust-anything finds the loop worth moving, and moves it.

> rust-anything is an independent project, not affiliated with or endorsed by the Rust Project
> or the Rust Foundation. "Rust" is a trademark of the Rust Foundation.

## Quick start

Paste this into Claude Code, Codex, Cursor or Gemini CLI and let your agent install it:

```text
Install rust-anything: run `cargo install rust-anything`, then `rust-anything setup`.
Tell me when to restart you.
```

Or yourself:

```sh
cargo install rust-anything   # from crates.io
rust-anything setup           # registers it with Claude Code, Codex, Cursor and Gemini CLI
```

No Rust toolchain yet? Prebuilt binaries for macOS, Linux and Windows are attached to each
[GitHub release](https://github.com/erkamyaman/rust-anything/releases), and for JavaScript
projects `npm install -g rust-anything` installs the same binary.

In Claude Code you can also install it as a plugin (the MCP server and the skill; the CLI above
must be on your `PATH`):

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` adds the MCP server to each agent it finds and installs the workflow skill where the agent
reads skills. It keeps your other settings, is safe to run again, and `--remove` undoes it.
Then ask your agent, for example:

- *"Rewrite this CLI in Rust with rust-anything, end to end, and prove it behaves the same."*
- *"This search feels slow. Profile it with rust-anything and move the hot loop to Rust."*
- *"Plan a migration of `src/parser/` to Rust with rust-anything; port the first unit and prove it."*
- *"Bench the Rust port in `rust/text-rs` against the original and tell me whether to ship it."*

### Works with

| Agent | `rust-anything setup` adds |
| --- | --- |
| Claude Code | MCP server in `~/.claude.json`, skill in `~/.claude/skills/` |
| Codex | MCP server in `~/.codex/config.toml`, skill in `~/.codex/skills/` |
| Cursor | MCP server in `~/.cursor/mcp.json` |
| Gemini CLI | MCP server in `~/.gemini/settings.json` |
| Any other MCP client | add `rust-anything mcp` as a stdio server by hand (see [Install](#install)) |

Before changing a file that exists, `setup` saves a copy beside it (`<file>.rust-anything.bak`).

Or run the steps yourself:

<p align="center">
  <img src="docs/assets/terminal.gif" alt="rust-anything profile finds fuzzyScore in a loop, bridge --batch generates the Rust crate, gate passes with 2000/2000 recorded cases, and the benchmark shows 20.7x faster than TS." width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # what is hot, and who calls it
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# write src/port.rs (or let your agent), then:
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # every recorded case must match
rust-anything bench rust/fuzzy-rs                      # faster? the verdict says
rust-anything gate rust/fuzzy-rs                       # done means this passes
```

rust-anything does not translate code: your coding agent (Claude Code, Codex, Cursor, ...) or you write
the Rust. rust-anything supplies what an agent cannot guess reliably: where the time goes, what to port
first and in which order, a bridge so the rest of the code calls the Rust with its API unchanged,
the exact behavior the port must match, a safe way to ship it, and a gate that says when a port is
done.

## Languages

| Language | Unit | Bridge | Recorded and replayed by |
| --- | --- | --- | --- |
| TypeScript/JavaScript | folder or file | napi-rs or wasm-bindgen with a generated binary wire; classes and async included | Node, running the `.ts` sources |
| Python | package or module | PyO3 (abi3), direct conversion, typed exceptions | Python, importing the original |
| C | `.c` file | `extern "C"` functions with the original names and a header | the original compiled to a shared library, called through ctypes, one fork per case |
| Go | package | typed cgo calls and a generated binary wire, in a package with the original API | a generated Go driver, built as its own module |
| Ruby | file or folder of module functions | a magnus extension under the original modules | a generated Ruby driver |
| Java | package of `public static` methods | typed JNI and a generated binary wire, in wrapper classes with the original methods | a generated reflection driver |
| PHP (preview) | folder of functions and `public static` methods | coming next: PHP FFI over a C ABI | whole apps today: `app record`, `app replay` and the front door, for CLIs and servers (`php -S`) |
| C# (preview) | folder of `public static` methods | coming next: P/Invoke over a C ABI | whole apps today: `app record`, `app replay` and the front door, for CLIs and ASP.NET servers (`dotnet <app>.dll`) |

Every language except C also gets batch classes (`--batch`): the items cross once and stay in
Rust, and each call runs over all of them on all cores.

The language is detected from the repository (`go.mod`, `pom.xml`, a `.csproj` or `.sln`,
`pyproject.toml`, `Gemfile`, `composer.json`, `package.json`, else the most common source files);
`--lang` overrides it. Types come from the source: TS types, Python hints, C, Go, Java and C#
signatures, Ruby YARD tags, PHP types and phpdoc; untyped parameters used as numbers are inferred
as numbers.

PHP is in preview: `analyze` plans a PHP app (Composer packages and PSR-4 autoloading, risks
such as loose comparison and integer overflow into floats, Composer packages mapped to crates),
and a PHP CLI or server can be recorded, replayed and put behind a Rust front door. Porting its
units into Rust through PHP's FFI is the next step ([issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

C# is in preview the same way: `analyze` reads `.csproj` projects and their NuGet packages
(mapped to crates), resolves `using` directives to folders, and flags what C# does differently
(`decimal`, `dynamic`, LINQ's deferred queries, `Task`, `lock`, reflection). A C# CLI or ASP.NET
server can be recorded, replayed and put behind a Rust front door; porting units through P/Invoke
comes next.

## How it works

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 where the    what to     the Rust   what the    you or      every     faster?    both side   done means
 time goes    port first  crate and  original    your agent  recorded  the        by side in  this passes
                          wrapper    does        write it    case      verdict    production
```

The original stays the source of truth: `record` runs it on edge cases (and your own inputs) and
saves what it returns or throws; `diff` replays every case against the Rust; nothing ships until
they all match and `gate` passes. Callers keep the original API throughout.

A whole app goes through the same loop unit by unit, inside a frame that proves the whole
program ([Port a whole app](#port-a-whole-app)):

```
analyze --whole-app ──> app record ──> app front-door ──> per unit: the loop above, then app wire ──> app lift
 shape, every           what the app    Rust owns the       gate passes, so the unit answers in         pure Rust,
 dependency, the        does from the   entry point; the     Rust: replay 100%, fallback rate down      proved by
 decisions to make      outside         original answers                                                replay
```

## The loop

| Step | Command | What it does |
| --- | --- | --- |
| 0. Profile | `rust-anything profile <repo> -- node bench.mjs` | Runs a real workload under the language's profiler (node, cProfile, `go test` pprof, JFR, a Ruby tracer): hot functions by inclusive time, their callers, and which loops to batch; flags code that is already compiled (numba, Cython, JAX), where Rust gains little |
| 1. Plan | `rust-anything analyze <repo>` | Units, port order, risks with `file:line`, bridge per unit, dependency-to-crate fit, best first ports; `--whole-app` adds entry points and shape, every dependency (imported or declared) with its crate, pieces (units that import each other move together) and numbered decisions with a recommended answer |
| 2. Bridge | `rust-anything bridge <repo> <unit>` | Crate with the bindings (`lib.rs`, plus the wrapper the source language loads) and stubs to port (`port.rs`); `--batch fn:param` adds a class that keeps many `param` values in Rust |
| 3. Record | `rust-anything record <crate>` | Runs the original on generated edge cases (non-ASCII, emoji, `-0`, `NaN`, ints where floats are expected, ...) and on every semantic trap in every parameter (string length and case, signed division, overflow edges, float printing, map and sort order), and saves `cases.jsonl`; `--float-tolerance 1e-9` lets floats match within that share for numeric code |
| 3. Build | `rust-anything build <crate>` | Builds the Rust side: `.node`, wasm package, Python extension or shared library |
| 3. Diff | `rust-anything diff <crate>` | Replays the recorded cases against Rust, called the way the original's callers call it; lists mismatches |
| 3. Bench | `rust-anything bench <crate>` | Times the recorded cases on the original and on Rust, bridge included |
| 4. Shadow | `rust-anything shadow <crate>` | Drop-in that runs both, returns the original's result, reports mismatches; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Gate | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, tests, `unsafe` audit, nothing unported, a recorded failing case for every error path of the original, no `unwrap`/`expect`/`panic!` where the original returns an error (unless marked `// INFALLIBLE: <why>`), build, API, behavior |
| Agents | `rust-anything setup` | Registers the MCP server (`rust-anything mcp`, every step as a tool) and the workflow skill ([`skills/rust-anything/SKILL.md`](./skills/rust-anything/SKILL.md)) with your coding agents |

## Port a whole app

The goal is a pure Rust app that behaves like the original, with the original kept as reference.
Your agent writes the Rust; rust-anything orders the work, scaffolds it, and proves every step.
The [whole-app skill](./skills/rust-anything/whole-app.md) walks the agent through it, starting
with the decisions only you can make:

- **Grilling**: the agent asks in rounds, each question with its recommended answer, until every
  decision the port depends on is settled, and writes each one as an ADR in `rust/DECISIONS.md`,
  with `rust/GLOSSARY.md` mapping the original's terms to Rust names.
- **Research**: background agents read each dependency's primary sources and write
  `rust/research/<topic>.md`, with every semantic trap they found.
- **Across sessions**: `rust/MAP.md` lists every unit with its state; a session claims one unit
  before it starts, and each checkpoint leaves a `rust/HANDOFF.md` for the next session. Units in
  one wave can be ported in parallel by subagents.
- **Cutover**: the agent does what it can and writes `rust/cutover.sh`, an interactive script for
  the steps only you can do (deploys, DNS, secrets), with a way back at each step.

Grilling, research and these practices are adapted from
[Matt Pocock's skills](https://github.com/mattpocock/skills).

Plan first: `rust-anything analyze . --whole-app` adds the app's shape (CLI, server or library)
and entry points, every external dependency (imported or declared) with its Rust crate and fit,
the port order as pieces (units that import each other move together), and numbered decisions
with a recommended answer: keep units, blocked units, dependencies with no or a partial crate.

Then prove the whole program from the outside. `record` and `diff` prove one unit; `app record`
and `app replay` prove the app, for CLIs and servers in any of the six languages (the app is a
black box):

```sh
rust-anything app record . -- python3 cli.py          # the command that runs the original
rust-anything app replay .                            # the original must pass 100%
rust-anything app replay . --build "target/release/mytool"
```

- `app record` runs the original on the app's own documented examples (`$ mytool ...` lines in
  its Markdown and shell files, with the files they name), an `--inputs` JSONL file
  (`{"name", "args", "stdin", "env", "files"}`), and semantic traps derived from those cases
  (non-ASCII and emoji strings, negative division and modulo, overflow, large and tiny floats,
  map order, missing files). Each case runs twice; what differs between the two runs becomes a
  `[..]` wildcard. `--normalize timestamps|uuids|key-order` or `--normalize name=regex` adds
  normalizers, saved with the cases.
- Cases are [trycmd](https://docs.rs/trycmd) files in `rust/app-cases/`: `<case>.toml` (argv, env,
  exit code), `.stdin`, `.stdout`, `.stderr`, `.in/` (files in) and `.out/` (files written). Read
  and edit them by hand; a Rust test can run them with `trycmd` once the port has a binary.
- `app replay` runs any build against the cases, prints `passed/total`, writes
  `rust/app-cases/replay-report.md` with a diff per failing case, and exits non-zero on any
  mismatch. A build that appends to the file named by `RUST_ANYTHING_FALLBACK_LOG` (one line per
  fallback to the original), as the front door below does, also gets its fallback rate reported.
- `app replay --case <name>` reruns one case by the name the report gives it: the fast,
  repeatable loop for fixing a mismatch before running everything again.

Then move the entry point to Rust and hand it commands one unit at a time:

```sh
rust-anything app front-door .                            # rust/app: every command runs the original
rust-anything app wire . textkit --command upper          # after textkit-rs passes gate
# write the glue in rust/app/src/units/textkit.rs, then:
rust-anything app wire . textkit                          # 100% again, lower fallback rate
```

- `app front-door` scaffolds `rust/app`, a Rust binary named after the app: a clap parser for the
  commands and flags in the recorded cases, where every command runs the original with the same
  argv, stdin and environment and passes its output and exit code through. Each fallback is
  counted, so replaying the fresh front door gives 100% passed at 100% fallback (it builds and
  replays to show it). It never overwrites `rust/app`: the code is yours from then on.
- `app wire <repo> <unit> --command <name>` runs `gate` on the unit crate (`--skip-gate` if it just
  passed), adds it to `rust/app` as a library, writes `src/units/<unit>.rs` once for you or your
  agent to fill in (parse the arguments, call `<crate>::port`, print what the original prints),
  routes the commands to it, then builds and replays. `RUST_ANYTHING_UNIT_<NAME>=original` sends a
  wired unit back to the original until the lift.

Wire the app's own name as a command (`--command mytool`) for argv that names no command: no
arguments, unknown commands, usage errors.

When replay passes with fallback rate 0 and every unit passes gate, make it a pure Rust app:

```sh
rust-anything app lift .
```

- `app lift` refuses until both hold, and says what blocks it: the cases still falling back,
  glue still a stub, units failing gate.
- On a copy first, it removes the fallback path and the kill switches, turns each unit crate into
  a plain library of `rust/app` (no `cdylib`, bindings or generated wrappers), and adds
  `rust/app/tests/app_cases.rs`, which runs `rust/app-cases` with trycmd on `cargo test`, so CI
  needs nothing but cargo.
- Then it runs the lift checklist: fmt, clippy `-D warnings` and tests on every unit and on
  `rust/app`, every target named in `rust/DECISIONS.md` built or checked where it is installed,
  files read at run time and asset folders not embedded, and replay on the pure binary. Only when
  all of it passes are the changes written back. The original is never touched.

### Servers

The same commands prove HTTP servers. `--http` says the command starts a server; it takes its
port from `PORT` or `{port}` in the command (`--port` for one that always listens on the same
port):

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: every route proxied
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- Requests come from `curl` lines in the app's docs (`curl -X POST -d ... http://localhost:8080/x`),
  `--inputs` (`{"name", "method", "path", "headers", "body"}`) and traps: path segments and query
  values swapped for the same traps as CLI arguments, bodies for text and JSON traps, and an
  unknown route. Each run starts the server fresh and sends the requests in name order, so state
  between requests is kept.
- Cases are `rust/app-cases/http/<case>.toml` (the request, the status and the headers that matter)
  and `<case>.body` (the response body, with `[..]` where two runs differed). Date, server and
  other per-response headers are left out; delete any header line you do not care about.
- The front door is an axum server that starts the original on a port of its own and proxies
  every route no unit answers. `wire --route` takes axum routes: `METHOD /path/{param}`, `/path`
  for any method, `*` for everything else; the glue gets the route, its parameters and the
  request. `lift` removes the proxy; HTTP cases then run in CI with `app replay`.

### Libraries

A library has no process to replay: its public API is the front door, and each unit's recorded
cases are the proof.

```sh
rust-anything app front-door .        # rust/app: a Rust crate with the public API
# each unit through the loop: bridge, record, port.rs, build, diff, gate; then:
rust-anything app wire . textkit-rs   # re-exported from rust/app; the original imports its shadow
rust-anything app replay .            # every wired unit's cases; fallback = exports still in the original
rust-anything app lift .
```

- `app front-door` finds the public API (every unit's exports) when the repository has no `main`
  and no server (`--library` otherwise), and scaffolds `rust/app` as a library crate. Each wired
  unit becomes a module of it: `pub use textkit_rs::port as textkit;`.
- `app wire` takes a crate made by `bridge`, runs `gate`, and writes the unit's shadow drop-in:
  the original package imports it in place of the unit, so its callers keep the original API and
  reach the Rust. `RUST_ANYTHING_UNIT_<NAME>=original` sends the unit back (C: build without the
  shadow's flags).
- `app replay` runs every wired unit's recorded cases through its bindings. The fallback rate is
  the share of public exports Rust does not answer yet: unwired units, and exports `bridge` keeps
  in the original language.
- `app lift` needs fallback 0 and every unit through `gate`; it strips the bindings, wrappers and
  shadows from the units and leaves `rust/app` as one pure Rust library. It does not touch any
  `port.rs`, so the cases that matched through the bindings still describe it; the checklist
  warns about files of the original that still import the shadows.

All five are MCP tools too: `app_record`, `app_replay`, `app_front_door`, `app_wire` and
`app_lift`.

## Case study: x18n's core

All 29 functions of x18n's core that can move without an API change were ported with rust-anything:
every gate passes and 7,925 recorded cases match exactly. `rust-anything bench` then showed the ports
are slower than the TS as called from JS, because the bridge costs more than the work. Full report:
[`demo/x18n-core`](./demo/x18n-core/README.md). The lesson is built in: measure with `bench` before
shipping a port.

## Hot paths: keep the data in Rust

A port called once per item pays the bridge once per item, and loses to a JIT. What wins is
moving the loop: `profile` finds it, and `--batch` generates a class that takes the items once
and runs the function over all of them per call, on all cores, with typed-array results.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: a quarter of the run, called per key by `matched`: batch it
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // once
const order = search.rank(query, 0)               // per keystroke: indexes, best first
```

A `FuzzyScoreIndex` struct in `port.rs` replaces the default loop with one that prepares the
items once, and can rank by itself (`rank`): it keeps the keys lowercased with a character mask
each, a table of each key's first position of every common character (a one-letter query is one
column), and the last query's matches (typing `se` after `s` rescores only what `s` matched). On
x18n's sidebar search over 50,000 keys, typed letter by letter, with identical results:

| | Per query | vs TS |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`, filter, sort | 10 ms | 1x |
| TS with the same narrowing as the index | 4.1-5.4 ms | 2x |
| The same port, called per key | - | 0.2-0.4x |
| `FuzzyScoreBatch`, default index (4 cores) | 5.1 ms | 1.7x |
| `FuzzyScoreBatch` with `FuzzyScoreIndex` (napi, 4 cores) | 0.45-0.56 ms | **18-22x** |
| The same with wasm (one thread) | 0.95 ms | **11.5x** |

Against TS doing the same narrowing, Rust is still 7-12x faster (wasm 5x). Turn the returned
indexes into keys with a plain loop: `Array.from(order, i => keys[i])` cost 20x more, 0.4 ms.

Every language gets batches, and they beat the original even where per-call ports lose. The
same work on 4 cores, identical results and errors (benchmarks in each demo folder):

| Language | Workload | Original | Per-call port vs original | Batch vs original |
| --- | --- | ---: | ---: | ---: |
| TS | x18n search, 50,000 keys | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`, 20,000 strings | 98 ms | - | **17x** |
| Ruby | `slugify`, 20,000 strings | 110 ms | - | **12.7x** |
| Ruby | `shellescape` (stdlib), 50,000 mixed values | 88 ms | - | **11.8x** |
| Go | `Slugify`, 50,000 strings | 49 ms | 0.93x | **4x** |
| Java | `slugify`, 50,000 strings | 43 ms | 0.68x | **3x** |

Compiled originals gain less: the per-item work is already fast, so the batch wins by the number of
cores. Batch crates allocate with mimalloc: with the system allocator the Go batch was slower than
one thread. Demo: [`demo/x18n-search`](./demo/x18n-search/README.md).

## Real code in six languages

Go's `path`, Ruby's `shellwords`, Python's `colorsys`, JDK and glibc behavior behind small
facades: every port passes its gate, 13,010 recorded cases in all. The runs found and fixed
bugs in rust-anything (floats off by one ULP through `serde_json`, C crashes during recording,
untyped code getting garbage inputs). Called per function, the Ruby port runs 4.4x faster than
Ruby and the Python port 1.35x faster than CPython, while Go and Java leaf functions stay faster
in their own language; as batches, all of them win (see the table above).
Report: [`docs/real-world-languages.md`](./docs/real-world-languages.md).

## Example: a real module from x18n

`packages/core/src/fuzzy.ts` from [x18n](https://github.com/x18n-dev/x18n), ported both ways in
[`demo/`](./demo):

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: ready, wasm-bindgen (core runs in browsers)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# write src/port.rs
rust-anything gate demo/fuzzy-rs
```

A first port that indexed by Rust `char` passed simple tests but failed `diff`:

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS `indexOf` counts UTF-16 code units, so an emoji is two positions. The port in
`demo/*/src/port.rs` uses the generated `utf16` helpers and passes 2000/2000 cases and the gate,
as napi-rs (`demo/fuzzy-napi`) and as wasm-bindgen (`demo/fuzzy-rs`).

The plan rust-anything writes for all of x18n: [`docs/examples/x18n.md`](./docs/examples/x18n.md).

## Install

```sh
cargo install --path .
```

`record`, `diff` and `bench` run the original in its own runtime: Node 22.6+ for TS (it runs `.ts`
sources directly), Python 3.9+ for Python and C (ctypes), Go 1.21+, Ruby 3+, JDK 17+
(`javac` and `java`). C also needs a C compiler. wasm bridges also need `rustup target add wasm32-unknown-unknown` and
`cargo install wasm-bindgen-cli --version <the crate's wasm-bindgen version> --locked`; `build` names
the exact version.

For agents, `rust-anything setup` registers everything (see Quick start). To add the MCP server to
one project by hand instead (`.mcp.json`):

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## What `bridge` decides

- Exports that cannot cross a bridge stay in the source language, with the reason, and the shadow
  module re-exports the original. For TS:
  functions that take or return functions, generators and iterators, RegExp, `instanceof` checks,
  generics, and values whose types (followed through imports, re-exports and `extends`) hold
  functions. `--keep "name: reason"` keeps more, e.g. code that depends on `Intl` data.
- TS types map to Rust types, with type aliases resolved through imports and parameter types
  inferred from default values; structured values cross as a generated binary wire (JSON only
  as a fallback for shapes the wire does not model).
- JSON cannot express `undefined`, NaN, Infinity, -0 or lone surrogates: structured values carry
  markers (`{"$undefined": true}`, `{"$num": "NaN"}`, `{"$utf16": [...]}`) that the generated
  `index.cjs` translates, with helpers in the crate's `js.rs`.

`record` runs TS sources as they are: a Node resolve hook follows bundler-style imports
(`./errors` to `./errors.ts`), `--resolve-from` supplies npm packages when the repo has none
installed, and TS that needs transforming (enums, parameter properties) is retried with
`--experimental-transform-types`.

## What `analyze` looks at

- Packages (`package.json`) and source files; skips `node_modules`, build output, fixtures,
  playgrounds, tool configs. Vue/Svelte/Astro `<script>` blocks are parsed for imports.
- **Units**: a folder of source files, or a file at a package's source root.
- **Waves**: a unit's imports come in earlier waves; import cycles are ported together.
- **Bridge**: napi-rs when the unit or anything it imports needs Node; wasm-bindgen for portable
  code; keep in JS for UI and editor code.
- **Readiness** (how safe) and **priority** (safe and worth it: loops and string work, tests, size).

| Risk | Severity | Example |
| --- | --- | --- |
| String offsets | high | `slice`, `indexOf`, `matchAll`, the `d` flag: UTF-16 vs UTF-8 |
| Regex syntax | high | lookaround, backreferences, `y`: not in the `regex` crate |
| Dynamic regex | high | `new RegExp(userPattern)`: JS syntax at runtime |
| Dynamic code | high | `eval`, `new Function`, computed `import()` |
| Dynamic typing | medium | `any`, `'key' in value` |
| Ordered collections | medium | `Map`, `Set`, `Object.keys`: insertion order |
| Async, generators | medium | promise and generator boundaries |
| Class inheritance, reflection | medium | `extends`, `Proxy`, `Reflect`, `Symbol` |
| Callback-shaped APIs | medium | function-typed params and methods: chatty bridges |
| Exceptions, numbers, JSON | low | `throw`, bitwise ops, `JSON.stringify` order |

## Development

```sh
cargo test                        # unit tests, fixture repo, record/diff/shadow loop (needs node), app record/replay per language
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Design choices and their reasons: [DECISIONS.md](./DECISIONS.md).

## Update or remove

```sh
cargo install rust-anything                                    # update (Cargo)
npm install -g rust-anything@latest                            # update (npm)
rust-anything setup                                            # refresh agent settings
rust-anything setup --remove && cargo uninstall rust-anything  # remove (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # remove (npm)
```

`setup --remove` takes out only rust-anything's entries; the copies it saved
(`<file>.rust-anything.bak`) stay until you delete them.

## What it can't catch

Passing means the Rust matches every case that was recorded, nothing more. What bites rewrites
usually lives outside the recording, so know where the edges are:

- **Inputs nobody recorded.** The generated cases, the traps and your own `--inputs` are the
  ceiling. Add real inputs (production samples, bug reports, the original's test fixtures); the
  user input that breaks prod is rarely one a generator thinks of.
- **Regexes.** The `regex` crate has no lookaround or backreferences, and even a pattern that
  compiles can treat `\w`, `\b`, `\d` and case-insensitive matching on non-ASCII text differently
  from JS, Python or Java. Swapping in `fancy-regex` or rewriting the pattern can pass every
  recorded case and still differ on a Turkish dotless `ı` or a zero-width joiner. `record` adds
  regex traps (those, the Kelvin sign, long s, Arabic-Indic digits, line separators, final sigma)
  to every function in a file that uses regexes, but fuzz your real patterns against real text too.
- **What changes between runs.** `record` runs the original twice and sorts out what differed:
  changed values (times, ids) become wildcards; the same lines in another order (hash maps,
  concurrency) are compared in any order, so a port still has to produce exactly those lines; a
  different number of lines becomes `...`, which matches anything. `record` lists each kind:
  look at every one, since a hash-order or concurrency difference is exactly what can change for
  real in a port.
- **Floats.** Number-to-text formatting differs between languages (`1e21`, `-0`, digit counts).
  The traps include those values, and they must match exactly; `--float-tolerance` forgives
  rounding only, never formatting.
- **Anything not in the output.** Timing, memory, concurrency under load, and side effects other
  than stdout, stderr, exit codes, written files and HTTP responses (network calls, databases,
  signals) are not compared.
- **Other platforms.** A recording proves behavior on the machine that ran it. C whose results
  depend on type sizes, endianness or the compiler can behave differently on the target; `analyze`
  keeps hardware-facing C in C for that reason.

## FAQ

**Does it rewrite my code automatically?** No. It finds what to move, generates the bridge,
records what the original does and checks the Rust against it. You or your agent write the Rust
in `port.rs`; `diff` and `gate` decide when it is right.

**Will my app's API change?** No. Callers import the same functions (or the shadow module, which
runs both and returns the original's result while you build confidence).

**Is Rust always faster?** No, and rust-anything says so. A small function called once per item
is often slower in Rust, because each call crosses a bridge; V8, the JVM and Go run such functions
in nanoseconds. `profile` finds the loop around it, `--batch` moves the whole loop, and `bench`
gives a verdict before you ship. Code already compiled by numba, Cython or JAX runs as machine
code too: `profile` and `analyze` flag it, since porting it buys little speed.

**My code is numeric; will the floats match exactly?** Often not: operation order, fused
multiply-add and the math library differ between compilers. Record with `--float-tolerance 1e-9`
(`record` or `app record`), and floats match within that share of the larger value (absolute below
1). Integers, text and structure still have to match exactly.

**Can it port an app I only have as an APK, a JAR or an .exe?** No. It ports source code: it
parses the functions, records what each one does, and checks the Rust against the running
original. A compiled app has none of that to work with, and `analyze` says so. Writing a new Rust
app from a binary's visible behavior is a different project.

**Should I port battle-tested C?** Often not, and `analyze` tells you where. C that touches
hardware registers, relies on its compiler's type sizes or memory layout, or uses inline assembly
(`volatile`, bitfields, packed structs, `__asm__`, integers cast to addresses) is marked "keep in
C": a recording on your machine proves nothing about the target, and stable driver or firmware
code gains little from a rewrite. The portable logic around it (parsing, protocols, data handling)
is what moves well.

**Can it port my Electron app?** The logic, yes; the windows stay web pages. `analyze
--whole-app` spots Electron and plans the main process piece by piece while the renderer stays as
it is. Moving the UI to Tauri (the same web UI on a Rust backend) is a separate step once the logic
is Rust.

**What about C#, Kotlin or Swift?** C# is in preview (see [Languages](#languages)); Kotlin and
Swift are not supported yet. Each language needs a parser, a recorder, a bridge and a replay
driver, all tested end to end. Open an issue (or upvote one) for the language you need.

**Won't the Rust be much bigger than the original?** It shouldn't be. `gate` compares the port's
lines with the original's and fails above 3x (plus 50 lines for imports and signatures): that usually means hand-writing what a crate already
does, or handling cases one by one. `analyze` lists the crates to use.

**Doesn't porting piece by piece lock the Rust into the old app's design?** Only while both run
side by side. The recordings check behavior at the app's edges (a CLI's output, a server's
responses, a module's exported functions), not its internals. Mirror the old structure while
units still cross the bridge; once `app lift` has removed the original, restructure the Rust
freely, and `app replay` still proves the behavior. Nothing calls back into the original either:
the front door runs it as a separate process (or forwards HTTP to it), bridged units are called
by the original and never the other way round, and callbacks stay in the source language.

**Does my code leave my machine?** No: rust-anything runs locally and sends none of your code
anywhere. Cargo downloads crates as usual, and your agent's model provider sees what your agent
sends it, under its own policy.

**What does it need installed?** Rust, plus the runtime of the language you port (see
[Install](#install)).

**Something broke.** Open an issue with the command, its output and your platform.

## Sponsors

rust-anything is free and open source. If it helps your work, please consider sponsoring it. Your support keeps development going.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="Sponsor rust-anything on GitHub" /></a>
</p>

### Company sponsors

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Individual sponsors

<!-- sponsors -->
<!-- prettier-ignore-start -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/aliyilmazco"><img src="https://github.com/aliyilmazco.png?size=100" width="80px;" alt="Ali Yilmaz"/><br /><sub><b>Ali Yilmaz</b></sub></a></td>
    </tr>
  </tbody>
</table>
<!-- prettier-ignore-end -->
<!-- /sponsors -->

## Contributing

Issues and pull requests are welcome; [CONTRIBUTING.md](./CONTRIBUTING.md) covers the setup, where
tests go, and how to add a language. Design choices and their reasons are in
[DECISIONS.md](./DECISIONS.md). Case studies of real ports are especially welcome. Please report
security problems privately ([SECURITY.md](./SECURITY.md)), and see the
[code of conduct](./CODE_OF_CONDUCT.md).

## License

[MIT](./LICENSE) © [Erkam Yaman](https://github.com/erkamyaman). Ports and generated code in your repository are yours.
