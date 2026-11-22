#!/bin/sh
set -eu
trust_tmp=$(mktemp -d)
git clone https://github.com/Tim-rppl/trust-pyramid.git "$trust_tmp/repo"
git -C "$trust_tmp/repo" checkout d3401ada02803a2974b44fbf9e53cd84160423b9
cd "$trust_tmp/repo"
# Use Node and Python 3.12+ on PATH; the default macOS Python3 may be too old.
python3 --version
npm ci --ignore-scripts
npm test
