<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  LAST_EVENT_STORAGE_KEY,
  eventTypeOptions,
  frequencyOptions,
  mockAnalyzeResult,
  optionLabel,
  sampleAnalyzeRequest,
  type AnalyzeRequest,
} from '@/data/week1'

const eventRecord = ref<AnalyzeRequest>({ ...sampleAnalyzeRequest })
const result = mockAnalyzeResult
const sourceBreakdown = [
  { label: '噪音问题', percent: 45, tone: 'danger' },
  { label: '作息冲突', percent: 35, tone: 'warning' },
  { label: '卫生 (Hygiene)', percent: 20, tone: 'fresh' },
]

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isAnalyzeRequest(value: unknown): value is AnalyzeRequest {
  if (!isRecord(value)) {
    return false
  }

  return (
    typeof value.event_type === 'string' &&
    typeof value.severity === 'number' &&
    Number.isFinite(value.severity) &&
    value.severity >= 1 &&
    value.severity <= 5 &&
    typeof value.frequency === 'string' &&
    typeof value.emotion === 'string' &&
    typeof value.has_communicated === 'boolean' &&
    typeof value.has_conflict === 'boolean' &&
    typeof value.description === 'string'
  )
}

function fallbackToSampleRecord() {
  eventRecord.value = { ...sampleAnalyzeRequest }
  localStorage.removeItem(LAST_EVENT_STORAGE_KEY)
}

onMounted(() => {
  const stored = localStorage.getItem(LAST_EVENT_STORAGE_KEY)

  if (!stored) {
    return
  }

  try {
    const parsed = JSON.parse(stored) as unknown

    if (isAnalyzeRequest(parsed)) {
      eventRecord.value = parsed
      return
    }

    fallbackToSampleRecord()
  } catch {
    fallbackToSampleRecord()
  }
})

const eventTypeLabel = computed(() => optionLabel(eventTypeOptions, eventRecord.value.event_type))
const frequencyLabel = computed(() => optionLabel(frequencyOptions, eventRecord.value.frequency))
const communicationLabel = computed(() => (eventRecord.value.has_communicated ? '已沟通' : '尚未沟通'))
</script>

<template>
  <main class="page analysis-page bg-diagonal-stripes">
    <span class="analysis-decoration analysis-decoration-squiggle" aria-hidden="true"></span>
    <span class="analysis-decoration analysis-decoration-dots" aria-hidden="true"></span>

    <section class="page-heading analysis-heading">
      <div>
        <h1>
          宿舍压力分析报告
          <span class="update-chip card-border">本周更新</span>
        </h1>
        <p>通过对近期宿舍动态的分析，我们为您生成了这份专属的压力评估。保持关注，及时沟通！</p>
      </div>
    </section>

    <section class="analysis-bento">
      <article class="score-card pop-card pop-shadow" aria-label="压力分数 76/100，冲突风险较高">
        <span class="floating-icon material-symbol" aria-hidden="true">vital_signs</span>
        <h2>当前压力指数</h2>
        <div class="score-ring">
          <svg viewBox="0 0 192 192" aria-hidden="true">
            <circle class="score-ring-track" cx="96" cy="96" r="80"></circle>
            <circle class="score-ring-fill" cx="96" cy="96" r="80"></circle>
          </svg>
          <div class="score-ring-label">
            <strong>{{ result.pressure_score }}</strong>
            <span>/100</span>
          </div>
        </div>
        <p>
          状态：
          <span class="risk-badge">{{ result.risk_level }}</span>
        </p>
      </article>

      <div class="analysis-stack">
        <article class="result-panel pop-card">
          <span class="floating-icon floating-icon-left material-symbol" aria-hidden="true">bar_chart</span>
          <h2>主要压力来源</h2>
          <div class="bar-list">
            <div v-for="source in sourceBreakdown" :key="source.label" class="bar-item">
              <div class="bar-caption">
                <span>
                  <i :class="['bar-dot', `bar-dot-${source.tone}`]"></i>
                  {{ source.label }}
                </span>
                <strong>{{ source.percent }}%</strong>
              </div>
              <div class="bar-track card-border">
                <span :class="['bar-fill', `bar-fill-${source.tone}`]" :style="{ width: `${source.percent}%` }"></span>
              </div>
            </div>
          </div>
        </article>

        <article class="insight-card pop-card">
          <span class="floating-icon floating-icon-left material-symbol" aria-hidden="true">tips_and_updates</span>
          <h2>AI 心晴见解</h2>
          <div class="insight-list">
            <p>
              <strong>主要压力来源：</strong>
              {{ result.main_reasons.join('、') }}
            </p>
            <p>
              <strong>情绪关键词：</strong>
              {{ result.emotion_keywords.join('、') }}
            </p>
            <p>
              <strong>冲突风险趋势提示：</strong>
              {{ result.trend_notice }}
            </p>
            <p>
              <strong>系统建议：</strong>
              {{ result.suggestions[0] }}
            </p>
            <p>
              <strong>是否推荐进入 AI 沟通模拟：</strong>
              推荐
            </p>
            <p>
              <strong>安全提示：</strong>
              {{ result.safety_notice }}
            </p>
          </div>

          <button class="dark-action pop-shadow" type="button">
            进入沟通演练
            <span class="action-icon material-symbol" aria-hidden="true">arrow_forward</span>
          </button>
        </article>
      </div>
    </section>

  </main>
</template>
