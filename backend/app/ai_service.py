from dataclasses import dataclass
import os
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from app.ai_prompts import build_review_messages, build_simulate_messages
from app.env import load_project_env
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
    base_url: str
    timeout: float


class AIRunner(Protocol):
    def generate_simulation(self, request: SimulateRequest) -> SimulateResponse:
        raise NotImplementedError

    def generate_review(self, request: ReviewRequest) -> ReviewResponse:
        raise NotImplementedError


OutputModel = TypeVar("OutputModel", bound=BaseModel)
_STRUCTURE_ERROR_MESSAGE = "AI 输出结构异常，请稍后重试。"
_UNAVAILABLE_ERROR_MESSAGE = "AI 服务暂时不可用，请稍后重试。"
_DEFAULT_LLM_BASE_URL = "https://api.deepseek.com"
_DEFAULT_LLM_MODEL = "deepseek-v4-flash"


def load_ai_settings() -> AISettings:
    load_project_env()

    api_key = (
        os.getenv("DEEPSEEK_API_KEY", "").strip()
        or os.getenv("OPENAI_API_KEY", "").strip()
    )
    if not api_key:
        raise AIServiceConfigurationError(
            "AI 服务未配置：请设置 DEEPSEEK_API_KEY（推荐）或 OPENAI_API_KEY（兼容旧配置）。"
        )

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
        model=os.getenv("DORM_HARMONY_LLM_MODEL", _DEFAULT_LLM_MODEL).strip()
        or _DEFAULT_LLM_MODEL,
        base_url=os.getenv("DORM_HARMONY_LLM_BASE_URL", _DEFAULT_LLM_BASE_URL).strip()
        or _DEFAULT_LLM_BASE_URL,
        timeout=timeout,
    )


class LangChainDeepSeekRunner:
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
        public_error: AIServiceUnavailableError | None = None
        result: object | None = None

        try:
            from langchain_deepseek import ChatDeepSeek

            llm = ChatDeepSeek(
                model=self._settings.model,
                temperature=0.3,
                timeout=self._settings.timeout,
                max_retries=1,
                api_key=self._settings.api_key,
                api_base=self._settings.base_url,
            )
            structured_llm = llm.with_structured_output(schema, method="json_mode")
            result = structured_llm.invoke(messages)
        except ValidationError:
            public_error = AIOutputStructureError(_STRUCTURE_ERROR_MESSAGE)
        except Exception:
            public_error = AIServiceUnavailableError(_UNAVAILABLE_ERROR_MESSAGE)

        if public_error is not None:
            raise public_error

        return _ensure_model_instance(result, schema)


class DormHarmonyAIService:
    def __init__(self, runner: AIRunner | None = None) -> None:
        self._runner = runner

    def _get_runner(self) -> AIRunner:
        if self._runner is None:
            self._runner = LangChainDeepSeekRunner()
        return self._runner

    def simulate(self, request: SimulateRequest) -> SimulateResponse:
        public_error: AIServiceUnavailableError | None = None
        result: object | None = None

        try:
            result = self._get_runner().generate_simulation(request)
        except AIServiceConfigurationError:
            raise
        except AIOutputStructureError:
            public_error = AIOutputStructureError(_STRUCTURE_ERROR_MESSAGE)
        except AIServiceUnavailableError:
            public_error = AIServiceUnavailableError(_UNAVAILABLE_ERROR_MESSAGE)
        except ValidationError:
            public_error = AIOutputStructureError(_STRUCTURE_ERROR_MESSAGE)
        except Exception:
            public_error = AIServiceUnavailableError(_UNAVAILABLE_ERROR_MESSAGE)

        if public_error is not None:
            raise public_error

        return _ensure_model_instance(result, SimulateResponse)

    def review(self, request: ReviewRequest) -> ReviewResponse:
        public_error: AIServiceUnavailableError | None = None
        result: object | None = None

        try:
            result = self._get_runner().generate_review(request)
        except AIServiceConfigurationError:
            raise
        except AIOutputStructureError:
            public_error = AIOutputStructureError(_STRUCTURE_ERROR_MESSAGE)
        except AIServiceUnavailableError:
            public_error = AIServiceUnavailableError(_UNAVAILABLE_ERROR_MESSAGE)
        except ValidationError:
            public_error = AIOutputStructureError(_STRUCTURE_ERROR_MESSAGE)
        except Exception:
            public_error = AIServiceUnavailableError(_UNAVAILABLE_ERROR_MESSAGE)

        if public_error is not None:
            raise public_error

        return _ensure_model_instance(result, ReviewResponse)


def _ensure_model_instance(value: object, schema: type[OutputModel]) -> OutputModel:
    if isinstance(value, schema):
        return value

    if isinstance(value, dict):
        validation_failed = False
        model: OutputModel | None = None
        try:
            model = schema.model_validate(value)
        except ValidationError:
            validation_failed = True

        if validation_failed:
            raise AIOutputStructureError(_STRUCTURE_ERROR_MESSAGE)

        if model is not None:
            return model

    raise AIOutputStructureError(_STRUCTURE_ERROR_MESSAGE)


LangChainOpenAIRunner = LangChainDeepSeekRunner
