"""前后端接口契约和 AI 结构化输出模型。"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EventType(StrEnum):
    NOISE = "noise"
    SCHEDULE = "schedule"
    HYGIENE = "hygiene"
    COST = "cost"
    PRIVACY = "privacy"
    EMOTION = "emotion"


class EventFrequency(StrEnum):
    OCCASIONAL = "occasional"
    WEEKLY_MULTIPLE = "weekly_multiple"
    DAILY = "daily"


class Emotion(StrEnum):
    IRRITABLE = "irritable"
    ANXIOUS = "anxious"
    WRONGED = "wronged"
    ANGRY = "angry"
    HELPLESS = "helpless"
    DEPRESSED = "depressed"


class AnalyzeRequest(BaseModel):
    event_type: EventType
    severity: int = Field(ge=1, le=5)
    frequency: EventFrequency
    emotion: Emotion
    has_communicated: bool
    has_conflict: bool
    description: str = Field(max_length=500)

    @field_validator("description", mode="before")
    @classmethod
    def trim_and_require_description(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("description must be a string")

        description = value.strip()
        if not description:
            raise ValueError("description must not be empty")

        return description


AnalyzeRiskLevel = Literal["stable", "pressure", "high", "severe"]


class AnalyzeResponse(BaseModel):
    pressure_score: int
    risk_level: AnalyzeRiskLevel
    risk_label: str
    main_sources: list[str]
    emotion_keywords: list[str]
    trend_message: str
    suggestion: str
    recommend_simulation: bool
    disclaimer: str


RoommateName = Literal["舍友 A", "舍友 B", "舍友 C"]
RoommatePersonality = Literal["直接型", "回避型", "调和型"]
DialogueSpeaker = Literal["user", "roommate_a", "roommate_b", "roommate_c", "system"]

# 兼容前端展示文案，进入 AI 服务前统一收敛为后端稳定枚举。
FRONTEND_DIALOGUE_SPEAKER_ALIASES = {
    "我": "user",
    "你": "user",
    "用户": "user",
    "系统": "system",
    "舍友 A": "roommate_a",
    "舍友A": "roommate_a",
    "舍友 A（直接型）": "roommate_a",
    "舍友 A(直接型)": "roommate_a",
    "舍友 B": "roommate_b",
    "舍友B": "roommate_b",
    "舍友 B（回避型）": "roommate_b",
    "舍友 B(回避型)": "roommate_b",
    "舍友 C": "roommate_c",
    "舍友C": "roommate_c",
    "舍友 C（调和型）": "roommate_c",
    "舍友 C(调和型)": "roommate_c",
}

# 旧演示数据和当前 UI 的事件 id 不完全一致，这里只做显式白名单归一化。
FRONTEND_REVIEW_EVENT_TYPE_ALIASES = {
    "noise_conflict": "noise",
    "schedule_conflict": "schedule",
    "hygiene_conflict": "hygiene",
    "expense_conflict": "cost",
    "cost_conflict": "cost",
    "privacy_boundary": "privacy",
    "privacy_conflict": "privacy",
    "emotional_conflict": "emotion",
    "emotion_conflict": "emotion",
}
ANALYSIS_ONLY_EVENT_TYPE_ALIASES = {
    "risk-stable",
    "risk-pressure",
    "risk-high",
    "risk-severe",
}


def _validate_safety_note_boundaries(value: str) -> str:
    """校验 AI 输出仍保留项目要求的安全边界。"""
    if not isinstance(value, str):
        raise ValueError("safety_note must be a string")

    safety_note = value.strip()
    if not safety_note:
        raise ValueError("safety_note must not be empty")

    has_diagnosis_boundary = (
        "不进行心理诊断" in safety_note or "不进行心理疾病诊断" in safety_note
    )
    has_required_boundaries = (
        has_diagnosis_boundary
        and "不进行医学判断" in safety_note
        and "不进行人格评价" in safety_note
    )
    has_reality_support = any(
        phrase in safety_note for phrase in ("辅导员", "心理老师", "现实支持")
    )
    has_rehearsal_purpose = (
        "仅用于宿舍沟通演练" in safety_note or "仅用于沟通训练建议" in safety_note
    )
    has_virtual_roommate_boundary = "不代表真实舍友想法" in safety_note

    if (
        not has_required_boundaries
        or not has_reality_support
        or not has_rehearsal_purpose
        or not has_virtual_roommate_boundary
    ):
        raise ValueError("safety_note must include phase-2 safety boundaries")

    return safety_note


class SimulateRequest(BaseModel):
    scenario: str = Field(max_length=300)
    user_message: str = Field(max_length=500)
    risk_level: AnalyzeRiskLevel | None = None
    context: str | None = Field(default=None, max_length=500)

    @field_validator("scenario", "user_message", mode="before")
    @classmethod
    def trim_and_require_text(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("field must be a string")

        text = value.strip()
        if not text:
            raise ValueError("field must not be empty")

        return text

    @field_validator("risk_level", mode="before")
    @classmethod
    def trim_optional_risk_level(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("risk_level must be a string")

        risk_level = value.strip()
        return risk_level or None

    @field_validator("context", mode="before")
    @classmethod
    def trim_optional_context(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("context must be a string")

        context = value.strip()
        return context or None


class RoommateReply(BaseModel):
    roommate: RoommateName
    personality: RoommatePersonality
    message: str = Field(max_length=500)

    @field_validator("message", mode="before")
    @classmethod
    def trim_and_require_message(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("message must be a string")

        message = value.strip()
        if not message:
            raise ValueError("message must not be empty")

        return message


class SimulateResponse(BaseModel):
    replies: list[RoommateReply]
    safety_note: str

    @field_validator("safety_note", mode="before")
    @classmethod
    def validate_safety_note(cls, value: str) -> str:
        return _validate_safety_note_boundaries(value)

    @model_validator(mode="after")
    def require_fixed_roommate_roles(self) -> "SimulateResponse":
        """保证三位虚拟舍友的角色顺序稳定，方便前端固定展示。"""
        expected_roles = [
            ("舍友 A", "直接型"),
            ("舍友 B", "回避型"),
            ("舍友 C", "调和型"),
        ]
        actual_roles = [(reply.roommate, reply.personality) for reply in self.replies]

        if actual_roles != expected_roles:
            raise ValueError("replies must contain fixed roommate roles in order")

        return self


class DialogueMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    speaker: DialogueSpeaker
    message: str = Field(max_length=500)

    @field_validator("speaker", mode="before")
    @classmethod
    def normalize_frontend_speaker_alias(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("speaker must be a string")

        speaker = value.strip()
        return FRONTEND_DIALOGUE_SPEAKER_ALIASES.get(speaker, speaker)

    @field_validator("message", mode="before")
    @classmethod
    def trim_and_require_message(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("message must be a string")

        message = value.strip()
        if not message:
            raise ValueError("message must not be empty")

        return message


class ReviewOriginalEvent(BaseModel):
    """复盘时携带的原始事件摘要，用于给 AI 提供上下文。"""

    model_config = ConfigDict(extra="forbid")

    event_type: EventType | None = None
    severity: int | None = Field(default=None, ge=1, le=5)
    frequency: EventFrequency | None = None
    emotion: Emotion | None = None
    has_communicated: bool | None = None
    has_conflict: bool | None = None
    pressure_score: int | None = Field(default=None, ge=0, le=100)
    risk_level: AnalyzeRiskLevel | None = None
    risk_label: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=300)

    @field_validator("event_type", mode="before")
    @classmethod
    def normalize_frontend_event_type_alias(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("event_type must be a string")

        event_type = value.strip()
        if not event_type or event_type in ANALYSIS_ONLY_EVENT_TYPE_ALIASES:
            return None

        return FRONTEND_REVIEW_EVENT_TYPE_ALIASES.get(event_type, event_type)

    @field_validator("risk_label", "description", mode="before")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("field must be a string")

        text = value.strip()
        return text or None


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: str = Field(max_length=300)
    dialogue: list[DialogueMessage] = Field(min_length=1, max_length=20)
    original_event: ReviewOriginalEvent | None = None

    @field_validator("scenario", mode="before")
    @classmethod
    def trim_and_require_scenario(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("scenario must be a string")

        scenario = value.strip()
        if not scenario:
            raise ValueError("scenario must not be empty")

        return scenario


class ReviewResponse(BaseModel):
    summary: str
    strengths: list[str] = Field(min_length=1)
    risks: list[str] = Field(min_length=1)
    rewritten_message: str
    next_steps: list[str] = Field(min_length=1)
    safety_note: str

    @field_validator("summary", "rewritten_message", "safety_note", mode="before")
    @classmethod
    def trim_and_require_text(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("field must be a string")

        text = value.strip()
        if not text:
            raise ValueError("field must not be empty")

        return text

    @field_validator("safety_note", mode="after")
    @classmethod
    def validate_safety_note(cls, value: str) -> str:
        return _validate_safety_note_boundaries(value)

    @field_validator("strengths", "risks", "next_steps")
    @classmethod
    def require_non_empty_items(cls, value: list[str]) -> list[str]:
        cleaned_items: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("list items must be strings")

            cleaned_item = item.strip()
            if not cleaned_item:
                raise ValueError("list items must not be empty")
            cleaned_items.append(cleaned_item)

        return cleaned_items
