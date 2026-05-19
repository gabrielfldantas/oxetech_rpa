from fastapi import FastAPI

app = FastAPI(title="p1_hello")

@app.get("/")
def hello():
    return {"message": "hello world"}
