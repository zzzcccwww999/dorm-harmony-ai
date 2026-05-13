from dataclasses import dataclass
import os
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from app.ai_prompts import build_review_messages, build_simulate_messages
from app.schemas import ReviewRequest, ReviewResponse, SimulateRequest, SimulateResponse


class AIServiceConfigurationError(RuntimeError):
    pass


class AIServiceUnavailableError(RuntimeError):
    pass


class AIOutputStructureError(AIServiceUnavailableError):
    pass


@dataclass(frozen=True)
class AISettings:
    api_key: str
    model: str
    timeout: float


class AIRunner(Protocol):
    def generate_simulation(self, request: SimulateRequest) -> SimulateResponse:
        raise NotImplementedError

    def generate_review(self, request: ReviewRequest) -> ReviewResponse:
        raise NotImplementedError


OutputModel = TypeVar("OutputModel", bound=BaseModel)


def load_ai_settings() -> AISettings:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AIServiceConfigurationError("AI 服务未配置：请设置 OPENAI_API_KEY。")

    timeout_text = os.getenv("DORM_HARMONY_LLM_TIMEOUT", "20").strip()
    try:
        timeout = float(timeout_text)
    except ValueError:
        raise AIServiceConfigurationError(
            "AI 服务未配置：DORM_HARMONY_LLM_TIMEOUT 必须是数字。"
        ) from None

    if timeout <= 0:
        raise AIServiceConfigurationError(
            "AI 服务未配置：DORM_HARMONY_LLM_TIMEOUT 必须大于 0。"
        )

    return AISettings(
        api_key=api_key,
        model=os.getenv("DORM_HARMONY_LLM_MODEL", "gpt-4o-mini").strip()
        or "gpt-4o-mini",
        timeout=timeout,
    )


class LangChainOpenAIRunner:
    def __init__(self, settings: AISettings | None = None) -> None:
        self._settings = settings or load_ai_settings()
        self.model = self._settings.model

    def generate_simulation(self, request: SimulateRequest) -> SimulateResponse:
        return self._invoke_structured(SimulateResponse, build_simulate_messages(request))

    def generate_review(self, request: ReviewRequest) -> ReviewResponse:
        return self._invoke_structured(ReviewResponse, build_review_messages(request))

    def _invoke_structured(
        self, schema: type[OutputModel], messages: list[tuple[str, str]]
    ) -> OutputModel:
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=self._settings.model,
                temperature=0.3,
                timeout=self._settings.timeout,
                max_retries=1,
                api_key=self._settings.api_key,
            )
            structured_llm = llm.with_structured_output(schema)
            result = structured_llm.invoke(messages)
            return _ensure_model_instance(result, schema)
        except ValidationError:
            raise AIOutputStructureError("AI 输出结构异常，请稍后重试。") from None
        except AIOutputStructureError:
            raise
        except Exception:
            raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。") from None


class DormHarmonyAIService:
    def __init__(self, runner: AIRunner | None = None) -> None:
        self._runner = runner

    def _get_runner(self) -> AIRunner:
        if self._runner is None:
            self._runner = LangChainOpenAIRunner()
        return self._runner

    def simulate(self, request: SimulateRequest) -> SimulateResponse:
        try:
            return _ensure_model_instance(
                self._get_runner().generate_simulation(request), SimulateResponse
            )
        except AIServiceUnavailableError:
            raise
        except AIServiceConfigurationError:
            raise
        except ValidationError:
            raise AIOutputStructureError("AI 输出结构异常，请稍后重试。") from None
        except Exception:
            raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。") from None

    def review(self, request: ReviewRequest) -> ReviewResponse:
        try:
            return _ensure_model_instance(
                self._get_runner().generate_review(request), ReviewResponse
            )
        except AIServiceUnavailableError:
            raise
        except AIServiceConfigurationError:
            raise
        except ValidationError:
            raise AIOutputStructureError("AI 输出结构异常，请稍后重试。") from None
        except Exception:
            raise AIServiceUnavailableError("AI 服务暂时不可用，请稍后重试。") from None


def _ensure_model_instance(value: object, schema: type[OutputModel]) -> OutputModel:
    if isinstance(value, schema):
        return value

    if isinstance(value, dict):
        try:
            return schema.model_validate(value)
        except ValidationError:
            raise AIOutputStructureError("AI 输出结构异常，请稍后重试。") from None

    raise AIOutputStructureError("AI 输出结构异常，请稍后重试。")
