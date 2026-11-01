# Offline checks
```bash
git clone https://github.com/RUC-NLPIR/FlashRSI.git
cd FlashRSI
git checkout 98bebaf7f6d5f3f6f69ee22d87e02d0d8b89b591
uv venv /tmp/flashrsi-check --python 3.12
uv pip install --python /tmp/flashrsi-check/bin/python pytest pyyaml
/tmp/flashrsi-check/bin/python -m pytest tests/test_algorithm.py -o addopts='' -q
PYTHONPATH=. /tmp/flashrsi-check/bin/python -c 'from flashrsi.cli import main; raise SystemExit(main())' run --config examples/quickstart.yaml --prepare-only --output-dir /tmp/flashrsi-prepared
```
These are fixture-driven interface tests and configuration persistence only. No model requests or actual evolution accuracy/performance measurements. Full installation instructions in the article require extra dependencies beyond this minimal check.
