# 后端 API 契约

本文档记录第一阶段后端已实现接口和第二阶段字段草案。当前第一阶段只提供健康检查与压力分析接口；沟通模拟、沟通复盘、历史记录和 LangChain / 大模型调用尚未接入运行时。

## 安全边界

- 本项目输出仅用于宿舍关系压力趋势提示和沟通训练建议。
- 系统不进行心理疾病诊断、医学判断或人格评价。
- 当用户描述中出现高压力、暴力风险、严重失眠等情况时，返回内容应提示用户寻求辅导员、心理老师、家人或可信任同学等现实支持。

## 已实现接口

### GET /health

用途：检查 FastAPI 服务是否可访问。

响应示例：

```json
{
  "status": "ok"
}
```

### POST /api/analyze

用途：接收宿舍事件记录，返回压力评分、风险等级、主要来源、趋势提示和沟通建议。

请求字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `event_type` | string | 事件类型：`noise`、`schedule`、`hygiene`、`cost`、`privacy`、`emotion` |
| `severity` | number | 严重程度，整数 1-5 |
| `frequency` | string | 发生频率：`occasional`、`weekly_multiple`、`daily` |
| `emotion` | string | 当前情绪：`irritable`、`anxious`、`wronged`、`angry`、`helpless`、`depressed` |
| `has_communicated` | boolean | 是否已经沟通过 |
| `has_conflict` | boolean | 是否已经出现争吵、冷战或关系恶化 |
| `description` | string | 事件描述，去除首尾空白后不能为空，最长 500 字符 |

请求示例：

```json
{
  "event_type": "noise",
  "severity": 4,
  "frequency": "weekly_multiple",
  "emotion": "anxious",
  "has_communicated": false,
  "has_conflict": true,
  "description": "舍友晚上打游戏声音很大，影响睡眠。"
}
```

响应字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `pressure_score` | number | 0-100 压力值 |
| `risk_level` | string | 风险等级代码：`stable`、`pressure`、`high`、`severe` |
| `risk_label` | string | 风险等级中文标签 |
| `main_sources` | string[] | 主要压力来源 |
| `emotion_keywords` | string[] | 当前情绪关键词 |
| `trend_message` | string | 冲突风险趋势提示 |
| `suggestion` | string | 沟通建议 |
| `recommend_simulation` | boolean | 是否建议进入沟通演练 |
| `disclaimer` | string | 非诊断性安全提示 |

响应示例：

```json
{
  "pressure_score": 76,
  "risk_level": "high",
  "risk_label": "冲突风险较高",
  "main_sources": [
    "噪音冲突",
    "发生频率较高",
    "尚未有效沟通",
    "已出现争吵或冷战"
  ],
  "emotion_keywords": [
    "焦虑"
  ],
  "trend_message": "当前压力值为 76，处于“冲突风险较高”状态。问题可能正在积累，建议先练习表达方式，再选择合适时机沟通。",
  "suggestion": "建议先进行沟通演练，练习表达方式，再选择双方情绪相对平稳的时间进行现实沟通。",
  "recommend_simulation": true,
  "disclaimer": "本结果仅用于宿舍关系压力趋势提示，不作为心理诊断依据、医学诊断或人格评价依据。如压力持续升高或出现暴力风险、严重失眠等情况，请及时联系辅导员、心理老师、家人或可信任同学。"
}
```

## 第二阶段字段草案

以下内容仅为第二阶段字段草案，第一阶段未实现运行时路由，当前不能作为可调用接口验收。

### POST /api/simulate

状态：第一阶段未实现，仅保留字段草案。

拟定请求字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `scenario` | string | 宿舍沟通场景 |
| `user_message` | string | 用户准备表达的话术 |
| `risk_level` | string | 可选，来自 `/api/analyze` 的风险等级 |
| `context` | string | 可选，补充背景 |

拟定响应字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `replies` | object[] | 多个虚拟舍友回复 |
| `safety_note` | string | 非诊断性安全提示 |

拟定请求示例：

```json
{
  "scenario": "舍友晚上打游戏声音较大，影响睡眠",
  "user_message": "我想和你商量一下，晚上能不能把游戏声音调小一点，我最近睡眠受影响比较明显。",
  "risk_level": "high",
  "context": "用户尚未正式沟通过，但已经因为噪音问题感到焦虑。"
}
```

拟定响应示例：

```json
{
  "replies": [
    {
      "roommate": "舍友 A",
      "personality": "直接型",
      "message": "我也没开很大声吧，不过如果真的影响你了，我可以试着戴耳机。"
    },
    {
      "roommate": "舍友 B",
      "personality": "回避型",
      "message": "这个事情之后再说吧，我现在不太想聊。"
    },
    {
      "roommate": "舍友 C",
      "personality": "调和型",
      "message": "我们可以一起定个休息时间规则，尽量别互相影响。"
    }
  ],
  "safety_note": "本回复仅用于宿舍沟通演练，不代表真实舍友想法，也不构成心理诊断或人格评价。"
}
```

### POST /api/review

状态：第一阶段未实现，仅保留字段草案。

拟定请求字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `scenario` | string | 沟通场景 |
| `dialogue` | object[] | 用户与虚拟舍友的对话记录 |
| `original_event` | object | 可选，原始事件摘要 |

拟定响应字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `summary` | string | 表达总结 |
| `strengths` | string[] | 表达优点 |
| `risks` | string[] | 潜在问题 |
| `rewritten_message` | string | 优化话术 |
| `next_steps` | string[] | 后续行动建议 |
| `safety_note` | string | 非诊断性安全提示 |

拟定请求示例：

```json
{
  "scenario": "舍友晚上打游戏声音较大，影响睡眠",
  "dialogue": [
    {
      "speaker": "user",
      "message": "我想和你商量一下，晚上能不能把游戏声音调小一点，我最近睡眠受影响比较明显。"
    },
    {
      "speaker": "roommate_a",
      "message": "我也没开很大声吧，不过如果真的影响你了，我可以试着戴耳机。"
    }
  ],
  "original_event": {
    "event_type": "noise",
    "risk_level": "high",
    "pressure_score": 76
  }
}
```

拟定响应示例：

```json
{
  "summary": "用户表达了噪音对睡眠的影响，并使用了商量式语气，整体较温和。",
  "strengths": [
    "说明了具体影响，没有直接指责对方",
    "使用了请求和协商语气"
  ],
  "risks": [
    "可以进一步明确希望调整的时间范围",
    "如果对方回避，需要预留下一次沟通时间"
  ],
  "rewritten_message": "我想和你商量一下，晚上 11 点后能不能戴耳机或调低音量？我最近睡眠受影响比较明显，也想一起找个不影响你娱乐的办法。",
  "next_steps": [
    "选择双方情绪平稳的时间沟通",
    "提出具体可执行的休息时间规则",
    "如果多次沟通无效，可以寻求辅导员或宿舍管理员协助"
  ],
  "safety_note": "本复盘仅用于沟通训练建议，不进行心理疾病诊断、医学判断或舍友人格评价。"
}
```
