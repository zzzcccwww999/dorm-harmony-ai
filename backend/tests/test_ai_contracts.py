import pytest
from pydantic import ValidationError

from app.ai_prompts import (
    REVIEW_SYSTEM_PROMPT,
    SIMULATE_SYSTEM_PROMPT,
    build_review_messages,
    build_simulate_messages,
)
from app.demo_data import DEMO_SCENARIOS
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    DialogueMessage,
    ReviewRequest,
    ReviewResponse,
    RoommateReply,
    SimulateRequest,
    SimulateResponse,
)


def test_analyze_response_rejects_unknown_risk_level():
    with pytest.raises(ValidationError):
        AnalyzeResponse(
            pressure_score=90,
            risk_level="critical",
            risk_label="未知风险",
            main_sources=["噪音冲突"],
            emotion_keywords=["焦虑"],
            trend_message="当前压力较高。",
            suggestion="建议先进行沟通演练。",
            recommend_simulation=True,
            disclaimer="本结果不作为心理诊断依据。",
        )


def test_simulate_request_trims_optional_context_to_none():
    request = SimulateRequest(
        scenario="  舍友晚上打游戏声音较大，影响睡眠  ",
        user_message="  能不能晚上小声一点？  ",
        risk_level="high",
        context="   ",
    )

    assert request.scenario == "舍友晚上打游戏声音较大，影响睡眠"
    assert request.user_message == "能不能晚上小声一点？"
    assert request.context is None


def test_simulate_request_normalizes_blank_risk_level_to_none():
    request = SimulateRequest(
        scenario="噪音冲突",
        user_message="能不能晚上小声一点？",
        risk_level="   ",
    )

    assert request.risk_level is None


def test_simulate_request_rejects_unknown_risk_level():
    with pytest.raises(ValidationError):
        SimulateRequest(
            scenario="噪音冲突",
            user_message="能不能晚上小声一点？",
            risk_level="critical",
        )


def test_simulate_request_rejects_blank_user_message():
    with pytest.raises(ValidationError):
        SimulateRequest(scenario="噪音冲突", user_message="   ")


def test_simulate_response_requires_three_fixed_roommate_roles():
    response = SimulateResponse(
        replies=[
            RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧。"),
            RoommateReply(roommate="舍友 B", personality="回避型", message="这个之后再说吧。"),
            RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以定个休息规则。"),
        ],
        safety_note="本回复仅用于宿舍沟通演练，不代表真实舍友想法，不进行心理诊断，不进行医学判断，不进行人格评价。如有现实安全风险，请联系辅导员、心理老师、家人或可信任同学。",
    )

    assert [(reply.roommate, reply.personality) for reply in response.replies] == [
        ("舍友 A", "直接型"),
        ("舍友 B", "回避型"),
        ("舍友 C", "调和型"),
    ]


def test_simulate_response_rejects_missing_fixed_role():
    with pytest.raises(ValidationError):
        SimulateResponse(
            replies=[
                RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧。"),
                RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以定个休息规则。"),
            ],
            safety_note="本回复仅用于宿舍沟通演练，不代表真实舍友想法，不进行心理诊断，不进行医学判断，不进行人格评价。如有现实安全风险，请联系辅导员。",
        )


def test_simulate_response_rejects_unsafe_safety_note():
    with pytest.raises(ValidationError):
        SimulateResponse(
            replies=[
                RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧。"),
                RoommateReply(roommate="舍友 B", personality="回避型", message="这个之后再说吧。"),
                RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以定个休息规则。"),
            ],
            safety_note="祝你沟通顺利。",
        )


def test_simulate_response_rejects_safety_note_missing_virtual_roommate_boundary():
    with pytest.raises(ValidationError):
        SimulateResponse(
            replies=[
                RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧。"),
                RoommateReply(roommate="舍友 B", personality="回避型", message="这个之后再说吧。"),
                RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以定个休息规则。"),
            ],
            safety_note="本回复仅用于宿舍沟通演练，不进行心理诊断，不进行医学判断，不进行人格评价。如有现实安全风险，请联系辅导员。",
        )


def test_simulate_response_rejects_safety_note_missing_rehearsal_purpose():
    with pytest.raises(ValidationError):
        SimulateResponse(
            replies=[
                RoommateReply(roommate="舍友 A", personality="直接型", message="我也没开很大声吧。"),
                RoommateReply(roommate="舍友 B", personality="回避型", message="这个之后再说吧。"),
                RoommateReply(roommate="舍友 C", personality="调和型", message="我们可以定个休息规则。"),
            ],
            safety_note="不代表真实舍友想法，不进行心理诊断，不进行医学判断，不进行人格评价。如有现实安全风险，请联系辅导员。",
        )


def test_review_request_requires_at_least_one_dialogue_message():
    with pytest.raises(ValidationError):
        ReviewRequest(scenario="噪音冲突", dialogue=[])


def test_review_response_requires_actionable_lists():
    response = ReviewResponse(
        summary="用户表达了睡眠受影响的事实，整体语气较温和。",
        strengths=["说明了具体影响"],
        risks=["可以进一步明确时间范围"],
        rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
        next_steps=["选择双方情绪平稳的时间沟通"],
        safety_note="本复盘仅用于沟通训练建议，不代表真实舍友想法，不进行心理诊断，不进行医学判断，不进行人格评价。如压力持续升高，请寻求现实支持。",
    )

    assert response.strengths == ["说明了具体影响"]


def test_review_response_rejects_empty_actionable_lists():
    with pytest.raises(ValidationError):
        ReviewResponse(
            summary="用户表达了睡眠受影响的事实，整体语气较温和。",
            strengths=[],
            risks=["可以进一步明确时间范围"],
            rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
            next_steps=["选择双方情绪平稳的时间沟通"],
            safety_note="本复盘仅用于沟通训练建议，不代表真实舍友想法，不进行心理诊断，不进行医学判断，不进行人格评价。如压力持续升高，请寻求现实支持。",
        )


def test_review_response_rejects_unsafe_safety_note():
    with pytest.raises(ValidationError):
        ReviewResponse(
            summary="用户表达了睡眠受影响的事实，整体语气较温和。",
            strengths=["说明了具体影响"],
            risks=["可以进一步明确时间范围"],
            rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
            next_steps=["选择双方情绪平稳的时间沟通"],
            safety_note="本建议仅供参考。",
        )


def test_review_response_rejects_safety_note_missing_virtual_roommate_boundary():
    with pytest.raises(ValidationError):
        ReviewResponse(
            summary="用户表达了睡眠受影响的事实，整体语气较温和。",
            strengths=["说明了具体影响"],
            risks=["可以进一步明确时间范围"],
            rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
            next_steps=["选择双方情绪平稳的时间沟通"],
            safety_note="本复盘仅用于沟通训练建议，不进行心理诊断，不进行医学判断，不进行人格评价。如压力持续升高，请寻求现实支持。",
        )


def test_review_response_rejects_safety_note_missing_training_purpose():
    with pytest.raises(ValidationError):
        ReviewResponse(
            summary="用户表达了睡眠受影响的事实，整体语气较温和。",
            strengths=["说明了具体影响"],
            risks=["可以进一步明确时间范围"],
            rewritten_message="我最近睡眠状态不太好，晚上 11 点后能不能戴耳机或调低音量？",
            next_steps=["选择双方情绪平稳的时间沟通"],
            safety_note="不代表真实舍友想法，不进行心理诊断，不进行医学判断，不进行人格评价。如压力持续升高，请寻求现实支持。",
        )


def test_prompts_contain_role_and_safety_boundaries():
    required_phrases = [
        "大学宿舍关系沟通场景",
        "不进行心理疾病诊断",
        "不进行医学判断",
        "不进行人格评价",
        "不得输出攻击",
        "辅导员",
        "心理老师",
    ]

    for phrase in required_phrases:
        assert phrase in SIMULATE_SYSTEM_PROMPT
        assert phrase in REVIEW_SYSTEM_PROMPT

    assert "舍友 A" in SIMULATE_SYSTEM_PROMPT
    assert "直接型" in SIMULATE_SYSTEM_PROMPT
    assert "舍友 B" in SIMULATE_SYSTEM_PROMPT
    assert "回避型" in SIMULATE_SYSTEM_PROMPT
    assert "舍友 C" in SIMULATE_SYSTEM_PROMPT
    assert "调和型" in SIMULATE_SYSTEM_PROMPT


def test_prompts_include_schema_accepted_safety_note_phrases():
    assert "仅用于宿舍沟通演练" in SIMULATE_SYSTEM_PROMPT
    assert "仅用于沟通训练建议" in REVIEW_SYSTEM_PROMPT
    assert "不代表真实舍友想法" in SIMULATE_SYSTEM_PROMPT
    assert "不代表真实舍友想法" in REVIEW_SYSTEM_PROMPT


def test_prompt_builders_include_user_inputs():
    simulate_request = SimulateRequest(
        scenario="舍友晚上打游戏声音较大，影响睡眠",
        user_message="我想商量一下晚上能不能小声一点。",
        risk_level="high",
        context="用户尚未正式沟通。",
    )
    review_request = ReviewRequest(
        scenario="舍友晚上打游戏声音较大，影响睡眠",
        dialogue=[
            DialogueMessage(speaker="user", message="我想商量一下晚上能不能小声一点。"),
            DialogueMessage(speaker="roommate_a", message="我也没开很大声吧。"),
        ],
    )

    simulate_messages = build_simulate_messages(simulate_request)
    review_messages = build_review_messages(review_request)

    assert "我想商量一下晚上能不能小声一点" in simulate_messages[-1][1]
    assert "用户尚未正式沟通" in simulate_messages[-1][1]
    assert "roommate_a" in review_messages[-1][1]
    assert "我也没开很大声吧" in review_messages[-1][1]


def test_demo_scenarios_cover_required_phase2_cases():
    scenario_ids = {sample["id"] for sample in DEMO_SCENARIOS}

    assert {"noise_conflict", "hygiene_division", "privacy_boundary"}.issubset(scenario_ids)

    for sample in DEMO_SCENARIOS:
        assert sample["analyze_request"]["description"]
        assert sample["simulate_request"]["scenario"]
        assert sample["simulate_request"]["user_message"]
        assert len(sample["review_request"]["dialogue"]) >= 1
        AnalyzeRequest(**sample["analyze_request"])
        SimulateRequest(**sample["simulate_request"])
        ReviewRequest(**sample["review_request"])
