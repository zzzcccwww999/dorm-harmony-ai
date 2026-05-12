from fastapi.testclient import TestClient

from app.main import app
from app.safety import SAFETY_DISCLAIMER


client = TestClient(app)


def test_health_endpoint_returns_ok_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_endpoint_returns_structured_pressure_analysis():
    response = client.post(
        "/api/analyze",
        json={
            "event_type": "noise",
            "severity": 4,
            "frequency": "weekly_multiple",
            "emotion": "anxious",
            "has_communicated": False,
            "has_conflict": True,
            "description": "舍友晚上打游戏声音很大，影响睡眠。",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body.keys() == {
        "pressure_score",
        "risk_level",
        "risk_label",
        "main_sources",
        "emotion_keywords",
        "trend_message",
        "suggestion",
        "recommend_simulation",
        "disclaimer",
    }
    assert body["pressure_score"] == 76
    assert body["risk_level"] == "high"
    assert body["risk_label"] == "冲突风险较高"
    assert body["main_sources"] == ["噪音冲突", "发生频率较高", "尚未有效沟通", "已出现争吵或冷战"]
    assert body["emotion_keywords"] == ["焦虑"]
    assert body["recommend_simulation"] is True
    assert "当前压力值为 76" in body["trend_message"]
    assert "沟通演练" in body["suggestion"]
    assert body["disclaimer"] == SAFETY_DISCLAIMER


def test_analyze_endpoint_rejects_out_of_range_severity():
    response = client.post(
        "/api/analyze",
        json={
            "event_type": "noise",
            "severity": 6,
            "frequency": "daily",
            "emotion": "angry",
            "has_communicated": False,
            "has_conflict": True,
            "description": "测试严重程度越界。",
        },
    )

    assert response.status_code == 422
