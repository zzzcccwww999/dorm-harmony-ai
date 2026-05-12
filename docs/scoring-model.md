# 压力评分模型

本文档记录第一阶段 `/api/analyze` 使用的规则评分模型。当前模型不调用 LangChain 或大模型，仅根据用户提交的结构化字段计算压力值。

## 输入指标

| 指标 | 来源字段 | 原始取值 | 规则分 |
| --- | --- | --- | --- |
| 事件严重程度 | `severity` | 1-5 | `severity * 20` |
| 发生频率 | `frequency` | `occasional` / `weekly_multiple` / `daily` | 30 / 70 / 100 |
| 情绪强度 | `emotion` | `helpless` / `anxious` / `wronged` / `irritable` / `angry` / `depressed` | 30 / 58 / 62 / 68 / 86 / 90 |
| 沟通状态 | `has_communicated` | `true` / `false` | 30 / 100 |
| 冲突升级情况 | `has_conflict` | `false` / `true` | 40 / 100 |

## 权重

| 指标 | 权重 |
| --- | --- |
| 事件严重程度 | 30% |
| 发生频率 | 25% |
| 情绪强度 | 25% |
| 沟通状态 | 10% |
| 冲突升级情况 | 10% |

计算公式：

```text
pressure_score = round(
  severity_score * 0.30
  + frequency_score * 0.25
  + emotion_score * 0.25
  + communication_score * 0.10
  + conflict_score * 0.10
)
```

## 风险区间

| 压力值 | `risk_level` | `risk_label` | 说明 |
| --- | --- | --- | --- |
| 0-30 | `stable` | 关系平稳 | 当前压力较低，可继续保持日常沟通 |
| 31-60 | `pressure` | 存在压力 | 宿舍关系存在一定摩擦，建议及时沟通 |
| 61-80 | `high` | 冲突风险较高 | 问题可能正在积累，建议先进行沟通演练 |
| 81-100 | `severe` | 高压力状态 | 建议优先确保安全，并寻求现实支持 |

## 典型示例

夜间噪音案例：

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

分项计算：

| 指标 | 规则分 | 权重 | 加权分 |
| --- | --- | --- | --- |
| 严重程度 4 | 80 | 30% | 24 |
| 每周多次 | 70 | 25% | 17.5 |
| 焦虑 | 58 | 25% | 14.5 |
| 尚未沟通 | 100 | 10% | 10 |
| 已有冲突 | 100 | 10% | 10 |

合计为 76，风险等级为 `high`，中文标签为“冲突风险较高”。该结果只表示宿舍关系压力趋势，不作为心理诊断、医学诊断或人格评价依据。
