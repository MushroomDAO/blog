# banner-creator

A Claude Code skill that generates **photorealistic article banners locally** using FLUX.2
Klein (MLX) on Apple Silicon. 1200×630, under 99KB, no baked-in text — in ~75s, zero cloud cost.

## Install (global, any project)

```bash
cp -r banner-creator ~/.claude/skills/
chmod +x ~/.claude/skills/banner-creator/generate-banner.sh
```

Claude Code auto-registers it; invoke by saying "generate a banner / 做封面", or call the
script directly.

## Dependencies

- macOS Apple Silicon
- Python venv with `mflux` at `~/venvs/ml` (override via `FLUX_VENV`)
- FLUX.2 model at `~/.omlx/models/FLUX.2-klein-4B-mflux-4bit` (override via `FLUX_MODEL_PATH`)
  - download: `source ~/venvs/ml/bin/activate && mdt download Runpod/FLUX.2-klein-4B-mflux-4bit`
- ImageMagick: `brew install imagemagick`

(The companion `flux-gen` skill covers model setup.)

## Use

```bash
bash ~/.claude/skills/banner-creator/generate-banner.sh "my-article-slug" \
  "a researcher's desk at night with multiple monitors showing data dashboards, warm lamp light"
```

Output: `<auto-detected-dir>/my-article-slug-banner.jpg`. The output dir is auto-detected
(`src/assets/images` → `public/images` → `assets` → `banners`) or forced with `BANNER_OUT_DIR`.

## Tunables

| Env | Default | Purpose |
|-----|---------|---------|
| `BANNER_OUT_DIR` | auto | output directory |
| `BANNER_SIZE` | `1200x630` | banner dimensions |
| `BANNER_MAXKB` | `98` | hard file-size cap (always < 99KB) |
| `BANNER_STEPS` | `16` | FLUX inference steps (quality vs speed) |

## Design notes

- **Photorealistic is enforced** in the script (style suffix appended automatically) — callers
  supply only the scene subject. This keeps every banner on-brand.
- **No text**: the prompt suffix suppresses lettering; banners are clean backgrounds, with the
  page title rendered by the site, not baked into the image.
- File size is capped via ImageMagick `-define jpeg:extent=` so output is always publish-ready.

## License

MIT — free to use, adapt, and redistribute.
