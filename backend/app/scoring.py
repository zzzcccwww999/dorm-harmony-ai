"""宿舍关系压力评分模型。"""

from app.safety import SAFETY_DISCLAIMER
from app.schemas import AnalyzeRequest, AnalyzeResponse, Emotion, EventFrequency, EventType


FREQUENCY_SCORES: dict[EventFrequency, int] = {
    EventFrequency.OCCASIONAL: 30,
    EventFrequency.WEEKLY_MULTIPLE: 70,
    EventFrequency.DAILY: 100,
}

EMOTION_SCORES: dict[Emotion, int] = {
    Emotion.HELPLESS: 30,
    Emotion.ANXIOUS: 58,
    Emotion.WRONGED: 62,
    Emotion.IRRITABLE: 68,
    Emotion.ANGRY: 86,
    Emotion.DEPRESSED: 90,
}

EMOTION_KEYWORDS: dict[Emotion, str] = {
    Emotion.IRRITABLE: "烦躁",
    Emotion.ANXIOUS: "焦虑",
    Emotion.WRONGED: "委屈",
    Emotion.ANGRY: "愤怒",
    Emotion.HELPLESS: "无助",
    Emotion.DEPRESSED: "低落",
}

EVENT_SOURCE_LABELS: dict[EventType, str] = {
    EventType.NOISE: "噪音冲突",
    EventType.SCHEDULE: "作息冲突",
    EventType.HYGIENE: "卫生习惯差异",
    EventType.COST: "费用分摊压力",
    EventType.PRIVACY: "隐私边界压力",
    EventType.EMOTION: "情绪压力",
}


def analyze_pressure(request: AnalyzeRequest) -> AnalyzeResponse:
    """把用户记录转换成 0-100 压力值和前端可展示的分析结果。"""
    severity_score = request.severity * 20
    frequency_score = FREQUENCY_SCORES[request.frequency]
    emotion_score = EMOTION_SCORES[request.emotion]
    communication_score = 30 if request.has_communicated else 100
    conflict_score = 100 if request.has_conflict else 40

    # 权重保持可解释：严重程度、发生频率和情绪强度是主要因素，
    # 沟通状态和是否已冲突作为辅助放大项。
    pressure_score = round(
        severity_score * 0.30
        + frequency_score * 0.25
        + emotion_score * 0.25
        + communication_score * 0.10
        + conflict_score * 0.10
    )

    risk_level, risk_label = _risk_for_score(pressure_score)
    recommend_simulation = pressure_score >= 61

    return AnalyzeResponse(
        pressure_score=pressure_score,
        risk_level=risk_level,
        risk_label=risk_label,
        main_sources=_main_sources(request),
        emotion_keywords=[EMOTION_KEYWORDS[request.emotion]],
        trend_message=_trend_message(pressure_score, risk_label),
        suggestion=_suggestion(recommend_simulation),
        recommend_simulation=recommend_simulation,
        disclaimer=SAFETY_DISCLAIMER,
    )


def _risk_for_score(score: int) -> tuple[str, str]:
    """把压力分数映射为接口使用的风险等级和中文标签。"""
    if score <= 30:
        return "stable", "关系平稳"
    if score <= 60:
        return "pressure", "存在压力"
    if score <= 80:
        return "high", "冲突风险较高"
    return "severe", "高压力状态"


def _main_sources(request: AnalyzeRequest) -> list[str]:
    """根据事件类型、频率、沟通状态和冲突状态提取主要压力来源。"""
    sources = [EVENT_SOURCE_LABELS[request.event_type]]

    if request.frequency in {EventFrequency.WEEKLY_MULTIPLE, EventFrequency.DAILY}:
        sources.append("发生频率较高")
    if not request.has_communicated:
        sources.append("尚未有效沟通")
    if request.has_conflict:
        sources.append("已出现争吵或冷战")

    return sources


def _trend_message(score: int, risk_label: str) -> str:
    """根据压力分数和风险标签生成前端展示的趋势文案。"""
    if score <= 30:
        return f"当前压力值为 {score}，处于“{risk_label}”状态。整体关系较平稳，建议继续保持清晰、温和的沟通。"
    if score <= 60:
        return f"当前压力值为 {score}，处于“{risk_label}”状态。问题已有一定积累，建议尽早用具体事实表达感受和需求。"
    if score <= 80:
        return f"当前压力值为 {score}，处于“{risk_label}”状态。问题可能正在积累，建议先练习表达方式，再选择合适时机沟通。"
    return f"当前压力值为 {score}，处于“{risk_label}”状态。当前压力较高，建议优先确保安全，并寻求现实中的支持。"


def _suggestion(recommend_simulation: bool) -> str:
    """根据是否建议沟通演练生成下一步行动建议。"""
    if recommend_simulation:
        return "建议先进行沟通演练，练习表达方式，再选择双方情绪相对平稳的时间进行现实沟通。"
    return "建议继续保持现有沟通节奏，及时表达具体需求，避免小问题长期积累。"
