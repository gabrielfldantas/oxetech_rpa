import time
from collections import deque
from threading import Lock
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="p5_rate limit 1/s")

MAX_REQS = 1
WINDOW = 1.0
_hits: dict[str, deque[float]] = {}
_lock = Lock()


def allowed(client: str) -> bool:
    now = time.monotonic()
    with _lock:
        q = _hits.setdefault(client, deque())
        cutoff = now - WINDOW
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= MAX_REQS:
            return False
        q.append(now)
        return True


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client = request.client.host if request.client else "anon"
    if not allowed(client):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests"},
            headers={"Retry-After": "1"},
        )
    return await call_next(request)


@app.get("/")
def ping():
    return {"ok": True}
