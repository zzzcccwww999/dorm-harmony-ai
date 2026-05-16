"""封装 LangChain/DeepSeek 调用、配置读取和结构化输出校验。"""

from collections.abc import Sequence
from dataclasses import dataclass
import os
from typing import Protocol, TypeVar

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ValidationError

from app.ai_prompts import (
    build_archive_insight_messages,
    build_review_messages,
    build_simulate_messages,
)
from app.env import load_project_env
from app.schemas import (
    ArchiveAnalysisResponse,
    ArchiveInsightResponse,
    EventRecord,
    ReviewRequest,
    ReviewResponse,
    SimulateRequest,
    SimulateResponse,
)


class AIServiceConfigurationError(RuntimeError):
    """表示本地 AI 服务配置缺失或配置值非法。"""

    pass


class AIServiceUnavailableError(RuntimeError):
    """表示已配置 AI 服务但上游调用暂时不可用。"""

    pass


class AIOutputStructureError(AIServiceUnavailableError):
    """表示模型返回内容无法通过后端结构化响应校验。"""

    pass


@dataclass(frozen=True)
class AISettings:
    """封装一次 LLM 调用所需的连接、模型和超时配置。"""

    api_key: str
    model: str
    base_url: str
    timeout: float


class AIRunner(Protocol):
    """定义 AI 运行器必须提供的三个结构化生成能力。"""

    def generate_simulation(self, request: SimulateRequest) -> SimulateResponse:
        """根据沟通模拟请求生成三位虚拟舍友的结构化回复。"""
        raise NotImplementedError

    def generate_review(self, request: ReviewRequest) -> ReviewResponse:
        """根据对话复盘请求生成结构化沟通复盘报告。"""
        raise NotImplementedError

    def generate_archive_insight(
        self,
        events: list[EventRecord],
        analysis: ArchiveAnalysisResponse,
    ) -> ArchiveInsightResponse:
        """根据事件档案和总压力分析生成结构化心晴见解。"""
        raise NotImplementedError


OutputModel = TypeVar("OutputModel", bound=BaseModel)
_STRUCTURE_ERROR_MESSAGE = "AI 输出结构异常，请稍后重试。"
_UNAVAILABLE_ERROR_MESSAGE = "AI 服务暂时不可用，请稍后重试。"
_DEFAULT_LLM_BASE_URL = "https://api.deepseek.com"
_DEFAULT_LLM_MODEL = "deepseek-v4-flash"


def load_ai_settings() -> AISettings:
    """读取 AI 配置；优先使用 DeepSeek Key，保留旧 OpenAI Key 兼容。"""
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
    """通过 LangChain 调用 DeepSeek，并按 Pydantic schema 解析输出。"""

    def __init__(self, settings: AISettings | None = None) -> None:
        """初始化 DeepSeek 调用配置；未传入时从环境变量加载。"""
        self._settings = settings or load_ai_settings()
        self.model = self._settings.model

    def generate_simulation(self, request: SimulateRequest) -> SimulateResponse:
        """构造模拟 Prompt 并返回结构化沟通演练结果。"""
        return self._invoke_structured(SimulateResponse, build_simulate_messages(request))

    def generate_review(self, request: ReviewRequest) -> ReviewResponse:
        """构造复盘 Prompt 并返回结构化沟通复盘结果。"""
        return self._invoke_structured(ReviewResponse, build_review_messages(request))

    def generate_archive_insight(
        self,
        events: list[EventRecord],
        analysis: ArchiveAnalysisResponse,
    ) -> ArchiveInsightResponse:
        """构造档案见解 Prompt 并返回结构化心晴见解。"""
        return self._invoke_structured(
            ArchiveInsightResponse,
            build_archive_insight_messages(events, analysis),
        )

    def _invoke_structured(
        self, schema: type[OutputModel], messages: Sequence[BaseMessage]
    ) -> OutputModel:
        """调用模型的 JSON 模式，并把异常收敛为前端可理解的错误。"""
        public_error: AIServiceUnavailableError | None = None
        result: object | None = None

        try:
            # 延迟导入让无 API Key 的测试环境也能构造服务对象。
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
            # 不把供应商异常、网络细节或潜在密钥内容暴露给前端。
            public_error = AIServiceUnavailableError(_UNAVAILABLE_ERROR_MESSAGE)

        if public_error is not None:
            raise public_error

        return _ensure_model_instance(result, schema)


class DormHarmonyAIService:
    """FastAPI 依赖使用的 AI 服务门面，统一错误和结构校验语义。"""

    def __init__(self, runner: AIRunner | None = None) -> None:
        """保存可替换的 AI 运行器，方便接口测试注入 fake runner。"""
        self._runner = runner

    def _get_runner(self) -> AIRunner:
        """懒加载默认 LangChain Runner，避免无 Key 环境提前失败。"""
        if self._runner is None:
            self._runner = LangChainDeepSeekRunner()
        return self._runner

    def simulate(self, request: SimulateRequest) -> SimulateResponse:
        """生成沟通模拟结果，并保证返回值符合 SimulateResponse。"""
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
        """生成沟通复盘结果，并保证返回值符合 ReviewResponse。"""
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

    def archive_insight(
        self,
        events: list[EventRecord],
        analysis: ArchiveAnalysisResponse,
    ) -> ArchiveInsightResponse:
        """生成事件档案 AI 见解，并保证返回值符合 ArchiveInsightResponse。"""
        public_error: AIServiceUnavailableError | None = None
        result: object | None = None

        try:
            result = self._get_runner().generate_archive_insight(events, analysis)
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

        return _ensure_model_instance(result, ArchiveInsightResponse)


def _ensure_model_instance(value: object, schema: type[OutputModel]) -> OutputModel:
    """统一把 LangChain 返回值收敛到接口响应模型。"""
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
