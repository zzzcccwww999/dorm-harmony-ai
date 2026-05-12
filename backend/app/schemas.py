from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


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


class AnalyzeResponse(BaseModel):
    pressure_score: int
    risk_level: str
    risk_label: str
    main_sources: list[str]
    emotion_keywords: list[str]
    trend_message: str
    suggestion: str
    recommend_simulation: bool
    disclaimer: str
