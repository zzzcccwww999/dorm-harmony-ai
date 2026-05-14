"""演示和测试共用的典型宿舍关系场景。"""

# 每个场景同时覆盖分析、模拟和复盘请求，确保 Demo 数据能跑通完整链路。
DEMO_SCENARIOS = [
    {
        "id": "noise_conflict",
        "title": "夜间游戏噪音影响睡眠",
        "analyze_request": {
            "event_type": "noise",
            "severity": 4,
            "frequency": "daily",
            "emotion": "anxious",
            "has_communicated": False,
            "has_conflict": True,
            "description": "舍友最近几乎每天晚上打游戏开麦，声音持续到凌晨，影响我睡眠，我们已经有点冷战。",
        },
        "simulate_request": {
            "scenario": "舍友晚上打游戏和开麦声音较大，影响睡眠。",
            "user_message": "我最近被晚上游戏声音影响得睡不好，能不能 11 点后戴耳机并小声一点？",
            "risk_level": "high",
            "context": "用户还没有正式沟通，担心一开口就争吵。",
        },
        "review_request": {
            "scenario": "舍友晚上打游戏和开麦声音较大，影响睡眠。",
            "dialogue": [
                {
                    "speaker": "user",
                    "message": "我最近被晚上游戏声音影响得睡不好，能不能 11 点后戴耳机并小声一点？",
                },
                {
                    "speaker": "roommate_a",
                    "message": "我也没觉得多吵，大家都在宿舍生活，别太敏感吧。",
                },
            ],
            "original_event": {
                "event_type": "noise",
                "frequency": "daily",
                "risk_level": "high",
            },
        },
    },
    {
        "id": "hygiene_division",
        "title": "公共卫生分工不均",
        "analyze_request": {
            "event_type": "hygiene",
            "severity": 3,
            "frequency": "weekly_multiple",
            "emotion": "wronged",
            "has_communicated": True,
            "has_conflict": False,
            "description": "公共区域经常没人打扫，我承担了大部分清理工作，提醒过一次但没有形成固定分工。",
        },
        "simulate_request": {
            "scenario": "宿舍公共区域卫生分工不清，用户承担了较多清理工作。",
            "user_message": "这周公共区域主要是我在收拾，能不能一起排个简单值日表？",
            "risk_level": "pressure",
            "context": "用户之前提醒过一次，但没有明确提出分工方案。",
        },
        "review_request": {
            "scenario": "宿舍公共区域卫生分工不清，用户承担了较多清理工作。",
            "dialogue": [
                {
                    "speaker": "user",
                    "message": "这周公共区域主要是我在收拾，能不能一起排个简单值日表？",
                },
                {
                    "speaker": "roommate_c",
                    "message": "可以，我们可以按周轮流，先把垃圾和地面分出来。",
                },
            ],
            "original_event": {
                "event_type": "hygiene",
                "frequency": "weekly_multiple",
                "risk_level": "pressure",
            },
        },
    },
    {
        "id": "privacy_boundary",
        "title": "未经允许使用个人物品",
        "analyze_request": {
            "event_type": "privacy",
            "severity": 4,
            "frequency": "occasional",
            "emotion": "angry",
            "has_communicated": False,
            "has_conflict": False,
            "description": "舍友未经允许用了我的护肤品和充电器，我发现后很生气，但还没有当面说明边界。",
        },
        "simulate_request": {
            "scenario": "舍友未经允许使用用户的个人物品，用户想表达隐私边界。",
            "user_message": "我发现我的东西被用过了，以后用我的个人物品前能不能先问我？",
            "risk_level": "high",
            "context": "用户希望坚定表达边界，但不想把关系弄僵。",
        },
        "review_request": {
            "scenario": "舍友未经允许使用用户的个人物品，用户想表达隐私边界。",
            "dialogue": [
                {
                    "speaker": "user",
                    "message": "我发现我的东西被用过了，以后用我的个人物品前能不能先问我？",
                },
                {
                    "speaker": "roommate_b",
                    "message": "我只是临时用一下，没想到你会这么介意。",
                },
            ],
            "original_event": {
                "event_type": "privacy",
                "frequency": "occasional",
                "risk_level": "high",
            },
        },
    },
]
