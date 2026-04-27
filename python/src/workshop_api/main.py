from fastapi import FastAPI

app = FastAPI(title="Architecture Python API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
