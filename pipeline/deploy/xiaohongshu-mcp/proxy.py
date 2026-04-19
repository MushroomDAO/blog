#!/usr/bin/env python3
"""将 Tailscale IP:3456 转发到 localhost:3456
解决 Docker Desktop on macOS 不绑 Tailscale 接口的问题"""
import socket
import threading
import subprocess

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 3456
LISTEN_PORT = 3456


def get_tailscale_ip() -> str:
    try:
        out = subprocess.check_output(["tailscale", "ip", "-4"], text=True).strip()
        return out
    except Exception:
        return "0.0.0.0"


def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        for s in (src, dst):
            try:
                s.close()
            except Exception:
                pass


def handle(client):
    try:
        server = socket.create_connection((TARGET_HOST, TARGET_PORT))
    except Exception:
        client.close()
        return
    threading.Thread(target=pipe, args=(client, server), daemon=True).start()
    threading.Thread(target=pipe, args=(server, client), daemon=True).start()


def main():
    listen_host = get_tailscale_ip()
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((listen_host, LISTEN_PORT))
    srv.listen(128)
    print(f"[proxy] {listen_host}:{LISTEN_PORT} → {TARGET_HOST}:{TARGET_PORT}")
    while True:
        client, addr = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()


if __name__ == "__main__":
    main()
