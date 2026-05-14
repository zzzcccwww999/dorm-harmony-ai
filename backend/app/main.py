import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.env import load_project_env
from app.ai_service import (
    AIServiceConfigurationError,
    AIServiceUnavailableError,
    DormHarmonyAIService,
)
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ReviewRequest,
    ReviewResponse,
    SimulateRequest,
    SimulateResponse,
)
from app.scoring import analyze_pressure


load_project_env()


def _get_cors_origins() -> list[str]:
    configured_origins = os.getenv("DORM_HARMONY_CORS_ORIGINS", "")
    origins = [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]
    return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]


app = FastAPI(title="Dorm Harmony AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def get_ai_service() -> DormHarmonyAIService:
    return DormHarmonyAIService()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_pressure(request)


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate(
    request: SimulateRequest,
    ai_service: DormHarmonyAIService = Depends(get_ai_service),
) -> SimulateResponse:
    try:
        return ai_service.simulate(request)
    except AIServiceConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIServiceUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/review", response_model=ReviewResponse)
def review(
    request: ReviewRequest,
    ai_service: DormHarmonyAIService = Depends(get_ai_service),
) -> ReviewResponse:
    try:
        return ai_service.review(request)
    except AIServiceConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AIServiceUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
