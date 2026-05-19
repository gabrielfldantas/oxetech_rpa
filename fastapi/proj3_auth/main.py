from fastapi import Depends, FastAPI, Header, HTTPException, status

app = FastAPI(title="p3_auth perms")

TOKENS = {
    "tok-admin": {"user": "alice", "scopes": {"read", "write", "admin"}},
    "tok-writer": {"user": "bob", "scopes": {"read", "write"}},
    "tok-reader": {"user": "carol", "scopes": {"read"}},
}


def current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    user = TOKENS.get(token)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    return user


def require_scope(scope: str):
    def checker(user=Depends(current_user)):
        if scope not in user["scopes"]:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"missing scope: {scope}")
        return user
    return checker


@app.get("/public")
def public():
    return {"ok": True}


@app.get("/me")
def me(user=Depends(current_user)):
    return {"user": user["user"], "scopes": sorted(user["scopes"])}


@app.get("/reports")
def reports(user=Depends(require_scope("read"))):
    return {"user": user["user"], "data": ["report-a", "report-b"]}


@app.get("/admin")
def admin(user=Depends(require_scope("admin"))):
    return {"user": user["user"], "secret": "42"}
