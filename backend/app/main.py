from fastapi import FastAPI

from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.scoring import analyze_pressure


app = FastAPI(title="Dorm Harmony AI")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_pressure(request)
