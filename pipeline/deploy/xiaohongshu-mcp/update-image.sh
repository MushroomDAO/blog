#!/bin/bash
set -e
cd "$(dirname "$0")"
docker-compose pull
docker-compose up -d --force-recreate
echo "[*] 镜像已更新并重启"
