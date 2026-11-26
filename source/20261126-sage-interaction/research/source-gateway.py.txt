"""Loopback browser gateway for independent, single-session model workers."""

import argparse
import asyncio

import httpx
import uvicorn
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sage_demo.protocol import PROJECT, backend_headers, configuration


def create_app(cfg):
    app = FastAPI()
    reserved = set()

    async def health():
        async with httpx.AsyncClient(trust_env=False, timeout=2) as client:

            async def worker(index):
                try:
                    response = await client.get(
                        f"http://127.0.0.1:{cfg['worker_port'] + index}/health"
                    )
                    response.raise_for_status()
                    return response.json()
                except (httpx.HTTPError, ValueError):
                    return {"gpu": index, "ready": False, "busy": False}

            workers = await asyncio.gather(
                *(worker(index) for index in range(cfg["worker_count"]))
            )
        backend = {"ready": False, "model": cfg["backend_model_name"]}
        try:
            async with httpx.AsyncClient(trust_env=True, timeout=3) as client:
                response = await client.get(
                    cfg["backend_base_url"] + "/models", headers=backend_headers()
                )
                response.raise_for_status()
                backend["ready"] = cfg["backend_model_name"] in [
                    row["id"] for row in response.json()["data"]
                ]
        except (httpx.HTTPError, ValueError, KeyError):
            pass
        return {
            "ready": backend["ready"] and any(row["ready"] for row in workers),
            "frontend": cfg["frontend_model_name"],
            "backend": backend,
            "workers": workers,
            "available_sessions": sum(
                row["ready"] and not row["busy"] and row["gpu"] not in reserved
                for row in workers
            ),
        }

    app.get("/api/health")(health)

    @app.websocket("/ws")
    async def route(ws: WebSocket):
        await ws.accept()
        snapshot = await health()
        candidates = [
            row["gpu"]
            for row in snapshot["workers"]
            if row["ready"] and not row["busy"] and row["gpu"] not in reserved
        ]
        if not snapshot["backend"]["ready"] or not candidates:
            await ws.send_json(
                {"type": "error", "message": "服务准备中或当前会话已满，请稍后重试。"}
            )
            await ws.close(code=1013)
            return
        device = candidates[0]
        reserved.add(device)
        try:
            async with websockets.connect(
                f"ws://127.0.0.1:{cfg['worker_port'] + device}/ws",
                proxy=None,
                max_size=2**20,
                open_timeout=10,
            ) as worker:

                async def upstream():
                    while True:
                        await worker.send(await ws.receive_text())

                async def downstream():
                    async for message in worker:
                        await ws.send_text(message)

                tasks = [
                    asyncio.create_task(upstream()),
                    asyncio.create_task(downstream()),
                ]
                try:
                    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                finally:
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
        except (websockets.exceptions.WebSocketException, WebSocketDisconnect, OSError):
            pass
        finally:
            reserved.discard(device)
            try:
                await ws.close()
            except RuntimeError:
                pass

    @app.get("/")
    async def index():
        return FileResponse(
            PROJECT / "sage_demo/static/index.html",
            headers={"Cache-Control": "no-store"},
        )

    app.mount(
        "/static", StaticFiles(directory=PROJECT / "sage_demo/static"), name="static"
    )
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = configuration(args.config)
    uvicorn.run(create_app(cfg), host="127.0.0.1", port=cfg["port"], ws_max_size=2**20)
