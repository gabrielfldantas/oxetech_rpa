from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="p2_upload txt")

STORAGE = Path(__file__).parent / "storage"
STORAGE.mkdir(exist_ok=True)


class TextPayload(BaseModel):
    filename: str
    content: str


@app.post("/files", status_code=201)
def save_text(payload: TextPayload):
    name = payload.filename.strip()
    if not name or "/" in name or "\\" in name or ".." in name:
        raise HTTPException(400, "invalid filename")
    if not name.endswith(".txt"):
        name += ".txt"
    path = STORAGE / name
    path.write_text(payload.content, encoding="utf-8")
    return {"saved": str(path.name), "bytes": path.stat().st_size}
