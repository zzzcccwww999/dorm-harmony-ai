# 前端 `/api/analyze` 字段对照表

## 接口

- 路径：`/api/analyze`
- 方法：`POST`
- 用途：事件记录页提交宿舍事件信息，压力分析页展示压力分数、风险等级、主要原因、系统建议和安全提示。
- 第一阶段状态：前端先使用本地模拟结果展示页面结构，后续联调时替换为真实接口返回。

## 请求字段

| 前端页面字段 | 请求字段 | 类型 | 示例值 | 说明 |
| --- | --- | --- | --- | --- |
| 事件类型 | `event_type` | string | `noise_conflict` | 作息、卫生、噪音、费用、隐私边界、情绪冲突等场景 |
| 严重程度 | `severity` | number | `4` | 1-5 分，分数越高代表影响越明显 |
| 发生频率 | `frequency` | string | `weekly` | `occasionally`、`weekly`、`daily` |
| 当前情绪 | `emotion` | string | `irritated` | 烦躁、焦虑、委屈、愤怒、无奈、压抑 |
| 是否已经沟通 | `has_communicated` | boolean | `false` | 是否已经和舍友沟通过 |
| 是否出现争吵或冷战 | `has_conflict` | boolean | `true` | 是否出现争吵、冷战或关系恶化 |
| 事件描述 | `description` | string | `舍友晚上打游戏声音比较大...` | 用户对事件的简短描述 |

## 请求示例

```json
{
  "event_type": "noise_conflict",
  "severity": 4,
  "frequency": "weekly",
  "emotion": "irritated",
  "has_communicated": false,
  "has_conflict": true,
  "description": "舍友晚上打游戏声音比较大，最近一周影响了睡眠。"
}
```

## 响应展示字段

| 压力分析页区域 | 响应字段 | 类型 | 示例值 |
| --- | --- | --- | --- |
| 压力分数 | `pressure_score` | number | `76` |
| 风险等级 | `risk_level` | string | `冲突风险较高` |
| 主要原因 | `main_reasons` | string[] | `["夜间噪音影响休息", "问题每周多次出现"]` |
| 系统建议 | `suggestions` | string[] | `["先选择双方情绪较平稳的时间沟通。"]` |
| 安全提示 | `safety_notice` | string | `本结果仅用于宿舍关系压力趋势提示，不作为医学或心理诊断依据。` |

## 响应示例

```json
{
  "pressure_score": 76,
  "risk_level": "冲突风险较高",
  "main_reasons": ["夜间噪音影响休息", "问题每周多次出现", "尚未形成有效沟通"],
  "suggestions": [
    "先选择双方情绪较平稳的时间沟通。",
    "表达自己的睡眠受影响，再提出 12 点后戴耳机的具体请求。"
  ],
  "safety_notice": "本结果仅用于宿舍关系压力趋势提示，不作为医学或心理诊断依据。"
}
```
