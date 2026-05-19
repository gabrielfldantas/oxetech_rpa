from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
import json
import sys
from datetime import datetime

app = FastAPI(title="Proj7 - Request Logger")

logger.remove()
logger.add(
    "logs/requests.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="1 MB",
    retention="7 days"
)
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_body = ""

    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            request_body = await request.body()
            request_body = request_body.decode("utf-8")
        except Exception as e:
            request_body = f"Error reading body: {str(e)}"

    headers_dict = dict(request.headers)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": headers_dict,
        "body": request_body if request_body else None,
    }

    try:
        response = await call_next(request)
        log_entry["status_code"] = response.status_code
        logger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))
        return response
    except Exception as e:
        log_entry["error"] = str(e)
        logger.error(json.dumps(log_entry, ensure_ascii=False, indent=2))
        raise


@app.get("/")
async def root():
    return {"message": "Proj7 - Request Logger Active"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/data")
async def receive_data(request: Request):
    body = await request.json()
    return {"received": body, "timestamp": datetime.now().isoformat()}


@app.put("/update/{item_id}")
async def update_item(item_id: int, request: Request):
    body = await request.json()
    return {"item_id": item_id, "updated": body}


@app.delete("/delete/{item_id}")
async def delete_item(item_id: int):
    return {"deleted": item_id}


@app.get("/search")
async def search(q: str = None, limit: int = 10):
    return {"query": q, "limit": limit}