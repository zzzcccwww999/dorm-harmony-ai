from fastapi import Depends, FastAPI, HTTPException

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


app = FastAPI(title="Dorm Harmony AI")


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
