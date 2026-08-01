# Re-base from the official listmonk image so `wrangler deploy` builds and
# pushes this to Cloudflare's OWN registry (cached, fast starts) instead of
# referencing docker.io directly — Cloudflare does not cache pulls from
# external registries, so every container start was re-pulling from Docker
# Hub, likely hitting rate limits after repeated starts during this spike.
FROM docker.io/listmonk/listmonk:v6.2.0
