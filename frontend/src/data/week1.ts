export interface AnalyzeRequest {
  event_type: string
  severity: number
  frequency: string
  emotion: string
  has_communicated: boolean
  has_conflict: boolean
  description: string
}

export interface AnalyzeResult {
  pressure_score: number
  risk_level: string
  main_reasons: string[]
  suggestions: string[]
  safety_notice: string
  trend_notice: string
}

export const LAST_EVENT_STORAGE_KEY = 'dorm-harmony:last-event'

export const eventTypeOptions = [
  { value: 'schedule_conflict', label: '作息冲突', icon: 'schedule' },
  { value: 'hygiene_conflict', label: '卫生冲突', icon: 'cleaning_services' },
  { value: 'noise_conflict', label: '噪音冲突', icon: 'volume_up' },
  { value: 'expense_conflict', label: '费用冲突', icon: 'payments' },
  { value: 'privacy_boundary', label: '隐私边界', icon: 'visibility_off' },
  { value: 'emotional_conflict', label: '情绪冲突', icon: 'mood_bad' },
]

export const frequencyOptions = [
  { value: 'occasionally', label: '偶尔', icon: 'looks_one' },
  { value: 'weekly', label: '每周多次', icon: 'calendar_month' },
  { value: 'daily', label: '几乎每天', icon: 'event_repeat' },
]

export const emotionOptions = [
  { value: 'irritated', label: '烦躁', icon: 'sentiment_dissatisfied' },
  { value: 'anxious', label: '焦虑', icon: 'psychology' },
  { value: 'wronged', label: '委屈', icon: 'sentiment_sad' },
  { value: 'angry', label: '愤怒', icon: 'sentiment_extremely_dissatisfied' },
  { value: 'helpless', label: '无奈', icon: 'sentiment_neutral' },
  { value: 'repressed', label: '压抑', icon: 'sentiment_stressed' },
]

export const sampleAnalyzeRequest: AnalyzeRequest = {
  event_type: 'noise_conflict',
  severity: 4,
  frequency: 'weekly',
  emotion: 'irritated',
  has_communicated: false,
  has_conflict: true,
  description: '舍友晚上打游戏声音比较大，最近一周影响了睡眠，也不知道怎么开口说。',
}

export const mockAnalyzeResult: AnalyzeResult = {
  pressure_score: 76,
  risk_level: '冲突风险较高',
  main_reasons: ['夜间噪音影响休息', '问题每周多次出现', '尚未形成有效沟通'],
  suggestions: [
    '先选择双方情绪较平稳的时间沟通。',
    '表达自己的睡眠受影响，再提出 12 点后戴耳机的具体请求。',
    '如果沟通后仍持续影响生活，可联系辅导员或宿舍管理人员协助。',
  ],
  safety_notice: '本结果仅用于宿舍关系压力趋势提示，不作为医学或心理诊断依据。',
  trend_notice: '问题发生频率较高，且已经出现关系紧张迹象，建议先进行沟通演练。',
}

export function optionLabel(options: Array<{ value: string; label: string }>, value: string) {
  return options.find((option) => option.value === value)?.label ?? value
}
