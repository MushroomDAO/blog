# netron-graph

**English** · [简体中文](README.zh-CN.md)

A [Claude Code](https://claude.com/claude-code) skill that turns a code path, an architecture or a data flow into a **Netron-style interactive graph**: one self-contained HTML file with typed nodes, `key = value` attributes, labelled edges and a click-for-details side panel.

Each edge is a claim about the code, so each one cites the source line that makes it true (`path:line`). `build.py` re-checks every one of those lines on every rebuild. When the code moves, the graph tells you which edges went stale.

**Live demos:** [vLLM `serve` request path (中文)](https://oliver0719.github.io/netron-graph/vllm_serve.html) · [read-through cache (English)](https://oliver0719.github.io/netron-graph/minimal.html)

## What you get

- **Lanes** for lifecycles or processes (startup vs per-request, parent vs child). Edges between lanes are the coupling.
- **Evidence dots** on each node: observed, read from source, or unknown.
- **Issues overlay**: red rows and red dashed "leak" edges for reads that bypass an interface.
- **Current / proposed switch**: show a refactor as a diff on the same canvas.
- **Sibling-branch toggle**: show alternative code paths without cluttering the main one.
- **Source-check badge**: "27/28 edges checked" against a real checkout.
- **`scan`**: assert that *every* touch point of a config or global is drawn. The build fails on any match the graph doesn't show.
- **Chrome in Chinese or English** (`"lang": "zh"` / `"en"`). Content stays in whatever language you write it in.

## Install

### As a plugin (recommended)

In Claude Code:

```
/plugin marketplace add Oliver0719/netron-graph
/plugin install netron-graph@netron-graph
```

### As a plain skill

Copy `skills/netron-graph/` into `~/.claude/skills/` (all projects) or `<project>/.claude/skills/` (one project):

```bash
git clone https://github.com/Oliver0719/netron-graph.git
cp -r netron-graph/skills/netron-graph ~/.claude/skills/
```

Requires Python 3.9+ (standard library only) for `build.py`.

## Use

Ask Claude for a graph, e.g.

> Draw a netron-graph of how a request flows from `POST /orders` to the database in this repo.

> 用 netron-graph 画一下这个仓库里配置是怎么从 env 一路传到 worker 的链路图。

The skill traces the code, writes `<name>.graph.json` (the source of truth), builds the HTML with `--src <repo root>`, looks at it in a browser and sends it to you. To refresh a graph after the code changes:

```bash
python skills/netron-graph/scripts/build.py X.graph.json X.html --src <repo> --fix-refs
```

## Examples

| file | language | what it shows |
|---|---|---|
| [`examples/minimal.json`](skills/netron-graph/examples/minimal.json) | en | Small synthetic app with its own [`minimal_src`](skills/netron-graph/examples/minimal_src). Uses every layout mechanism, plus an issue, a leak edge and a `scan`. |
| [`examples/vllm_serve.json`](skills/netron-graph/examples/vllm_serve.json) | zh | Real open-source code: `vllm serve` → `/v1/chat/completions` → EngineCore subprocess, pinned to **vLLM v0.34.0**. Three lanes, 27/28 edges source-checked, a `scan`, a proposed view and a sibling branch. |

Rebuild them yourself:

```bash
python skills/netron-graph/scripts/build.py skills/netron-graph/examples/minimal.json minimal.html \
  --src skills/netron-graph/examples/minimal_src

git clone --depth 1 --branch v0.34.0 https://github.com/vllm-project/vllm.git /tmp/vllm
python skills/netron-graph/scripts/build.py skills/netron-graph/examples/vllm_serve.json vllm_serve.html \
  --src /tmp/vllm
```

The "proposed" view in the vLLM example only demonstrates the feature. It is not a change planned upstream.

## Layout

```
.claude-plugin/        plugin + marketplace manifests
skills/netron-graph/
  SKILL.md             instructions Claude follows
  SCHEMA.md            graph JSON reference
  scripts/build.py     validator + source checker + renderer
  assets/viewer.html   the fixed viewer template
  examples/            minimal (en) and vllm_serve (zh)
docs/                  prebuilt demo HTML (GitHub Pages)
```

## License

[MIT](LICENSE). Not affiliated with [Netron](https://github.com/lutzroeder/netron) or vLLM; "Netron-style" describes the look.
