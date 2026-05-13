<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import {
  ANALYSIS_RESULT_STORAGE_KEY,
  LAST_EVENT_STORAGE_KEY,
  REVIEW_RESULT_STORAGE_KEY,
  SIMULATION_RESULT_STORAGE_KEY,
  buildDemoReviewResponse,
  mapEventTypeToAnalyzeApi,
  mapRoommateToReviewSpeaker,
  isAnalyzeResult,
  isStoredReviewResult,
  submitReviewRequest,
  type AnalyzeRequest,
  type AnalyzeResult,
  type ReviewRewriteSuggestion,
  type ReviewDialogueLine,
  type ReviewRequest,
  type ReviewResponse,
  type SimulationRequest,
  type SimulationResponse,
} from '@/data/week1'

interface RecordLike {
  [key: string]: unknown
}

const fallbackDialogueMessage = '请先明确你本次沟通希望对方做出的具体调整。'

interface ReviewContext {
  scenario: string
  dialogue: ReviewDialogueLine[]
  original_event?: ReviewRequest['original_event']
}

type ReviewSimulationCache = {
  request: SimulationRequest
  response: SimulationResponse
}

const defaultRewriteSuggestion: ReviewRewriteSuggestion = {
  feeling_expression: '先把“我最近睡眠受影响”作为开场，让对方知道你的处境。',
  specific_request: '建议约定 11 点后使用耳机或调低音量，并提前说明你的作息边界。',
  communication_space: '我想先一起定个试行的规则，我们看看一周后是否都能适应。',
  instead: '你总是打游戏太吵，别人会不会想过我？',
  instead_after: '我最近睡眠状态不太好，晚上声音比较容易影响我。我们能不能约定 11 点后戴耳机？',
}

const scoreFallback = {
  clarity: 85,
  empathy: 72,
  resolution: 90,
}

const reviewError = ref('')
const isLoading = ref(false)
const reviewSource = ref('')
const reviewRequest = ref<ReviewRequest>({ scenario: '沟通复盘场景', dialogue: [] })
const reviewResponse = ref<ReviewResponse>(buildDemoReviewResponse('复盘页初始化', reviewRequest.value))

function isRecord(value: unknown): value is RecordLike {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function toJsonLine(value: unknown): string {
  return JSON.stringify(value)
}

function requestFingerprint(value: ReviewRequest): string {
  return toJsonLine({
    scenario: value.scenario,
    dialogue: value.dialogue,
    original_event: value.original_event,
  })
}

function buildFallbackAnalysisSource(parsed?: AnalyzeResult): ReviewContext['original_event'] | undefined {
  if (!parsed) {
    return undefined
  }

  return {
    risk_level: parsed.risk_level,
    pressure_score: parsed.pressure_score,
  }
}

function hydrateStoredAnalysis() {
  try {
    const raw = localStorage.getItem(ANALYSIS_RESULT_STORAGE_KEY)
    if (!raw) {
      return
    }

    const parsed = JSON.parse(raw) as unknown
    if (isAnalyzeResult(parsed)) {
      return parsed
    }

    localStorage.removeItem(ANALYSIS_RESULT_STORAGE_KEY)
  } catch {
    // ignore malformed storage in sandboxed browsers
  }
}

function hydrateStoredLastEvent(): AnalyzeRequest | null {
  try {
    const raw = localStorage.getItem(LAST_EVENT_STORAGE_KEY)
    if (!raw) {
      return null
    }

    const parsed = JSON.parse(raw) as unknown
    if (isRecord(parsed) && typeof parsed.event_type === 'string') {
      return {
        event_type: parsed.event_type,
        severity: Number(parsed.severity) || 1,
        frequency: typeof parsed.frequency === 'string' ? parsed.frequency : '',
        emotion: typeof parsed.emotion === 'string' ? parsed.emotion : '',
        has_communicated: parsed.has_communicated === true,
        has_conflict: parsed.has_conflict === true,
        description:
          typeof parsed.description === 'string' ? parsed.description : fallbackDialogueMessage,
      }
    }
  } catch {
    // ignore malformed storage
  }

  return null
}

function isSimulationReply(value: unknown): value is SimulationResponse['replies'][number] {
  return (
    isRecord(value) &&
    typeof (value as { roommate?: unknown }).roommate === 'string' &&
    typeof (value as { personality?: unknown }).personality === 'string' &&
    typeof (value as { message?: unknown }).message === 'string'
  )
}

function isStoredSimulationResult(value: unknown): value is ReviewSimulationCache {
  if (!isRecord(value)) {
    return false
  }

  const request = (value as { request?: unknown }).request
  const response = (value as { response?: unknown }).response

  if (!isRecord(request) || !isRecord(response)) {
    return false
  }

  const replies = (response as { replies?: unknown }).replies
  const safetyNote = (response as { safety_note?: unknown }).safety_note
  const isDemo = (response as { is_demo?: unknown }).is_demo
  const demoNotice = (response as { demo_notice?: unknown }).demo_notice

  return (
    typeof request.scenario === 'string' &&
    typeof request.user_message === 'string' &&
    Array.isArray(replies) &&
    replies.every(isSimulationReply) &&
    typeof safetyNote === 'string' &&
    typeof isDemo === 'boolean' &&
    typeof demoNotice === 'string'
  )
}

function buildDialogueFromSimulation(simulation: {
  request: SimulationRequest
  response: SimulationResponse
}): ReviewDialogueLine[] {
  const lines: ReviewDialogueLine[] = []

  if (simulation.request.user_message.trim().length > 0) {
    lines.push({
      speaker: 'user',
      message: simulation.request.user_message.trim(),
    })
  }

  for (const reply of simulation.response.replies.slice(0, 3)) {
    lines.push({
      speaker: mapRoommateToReviewSpeaker(reply.roommate),
      message: reply.message,
    })
  }

  return lines
}

function hydrateReviewContext(): ReviewContext {
  const analysis = hydrateStoredAnalysis()
  const lastEvent = hydrateStoredLastEvent()
  const fallbackDialogue: ReviewDialogueLine[] = [{ speaker: 'user', message: fallbackDialogueMessage }]

  let scenario = '沟通复盘场景'
  let dialogue = fallbackDialogue
  let originalEvent: ReviewContext['original_event'] | undefined

  try {
    const raw = localStorage.getItem(SIMULATION_RESULT_STORAGE_KEY)

    if (raw) {
      const parsed = JSON.parse(raw) as unknown
      if (isStoredSimulationResult(parsed)) {
        scenario = parsed.request.scenario || scenario
        dialogue = buildDialogueFromSimulation(parsed)
      }
    }
  } catch {
    // ignore malformed simulation cache
  }

  if (!dialogue.length) {
    const eventHint =
      typeof lastEvent?.description === 'string' && lastEvent.description.length > 0
        ? lastEvent.description
        : '先梳理你在沟通中希望对方调整的具体内容。'
    dialogue = [{ speaker: 'user', message: eventHint }]
    scenario = lastEvent?.event_type
      ? `舍友${lastEvent.event_type === 'noise_conflict' ? '作息' : '沟通'}场景`
      : scenario
  }

  originalEvent = buildFallbackAnalysisSource(analysis)

  if (lastEvent?.event_type) {
    const mappedEventType = mapEventTypeToAnalyzeApi(lastEvent.event_type)
    if (mappedEventType) {
      originalEvent = {
        ...originalEvent,
        event_type: mappedEventType,
      }
    }
  }

  return {
    scenario,
    dialogue,
    original_event:
      originalEvent &&
      Object.keys(originalEvent).length > 0
        ? originalEvent
        : undefined,
  }
}

function hydrateStoredReview(payload: ReviewRequest): ReviewResponse | null {
  const clearStoredReview = () => {
    try {
      localStorage.removeItem(REVIEW_RESULT_STORAGE_KEY)
    } catch {
      // ignore restricted storage
    }
  }

  try {
    const raw = localStorage.getItem(REVIEW_RESULT_STORAGE_KEY)
    if (!raw) {
      return null
    }

    const parsed = JSON.parse(raw) as unknown
    if (!isStoredReviewResult(parsed)) {
      clearStoredReview()
      return null
    }

    const matches = requestFingerprint(parsed.request) === requestFingerprint(payload)
    if (!matches) {
      clearStoredReview()
      return null
    }

    return parsed.response
  } catch {
    clearStoredReview()
    // ignore malformed cache
  }

  return null
}

const scoreCards = computed(() => [
  {
    title: 'Clarity',
    value: Math.max(68, scoreFallback.clarity - (reviewResponse.value.risks.length > 2 ? 10 : 0)),
    description: '表达清晰度',
  },
  {
    title: 'Empathy',
    value: Math.max(
      60,
      scoreFallback.empathy + (reviewResponse.value.strengths.length >= 2 ? 8 : 0),
    ),
    description: '共情能力',
  },
  {
    title: 'Resolution',
    value: Math.max(60, scoreFallback.resolution - (reviewResponse.value.risks.length >= 3 ? 6 : 2)),
    description: '问题解决度',
  },
])

const rewriteSuggestion = computed<ReviewRewriteSuggestion>(() => {
  if (typeof reviewResponse.value.rewritten_message === 'string') {
    return {
      ...defaultRewriteSuggestion,
      instead_after: reviewResponse.value.rewritten_message,
    }
  }

  return reviewResponse.value.rewritten_message
})

const canRender = computed(() => reviewResponse.value.strengths.length > 0)

function toSafeArray(value: string[]): string[] {
  return value.length > 0 ? value : ['暂无数据']
}

async function initReview() {
  isLoading.value = true
  reviewError.value = ''

  const context = hydrateReviewContext()
  reviewRequest.value = {
    scenario: context.scenario,
    dialogue: context.dialogue,
    original_event: context.original_event,
  }

  const cached = hydrateStoredReview(reviewRequest.value)
  if (cached) {
    reviewResponse.value = cached
    reviewSource.value = cached.is_demo ? '本地缓存（演示）' : '本地缓存'
    isLoading.value = false
    return
  }

  try {
    const result = await submitReviewRequest(reviewRequest.value)
    reviewResponse.value = result
    reviewSource.value = result.is_demo ? '演示复盘' : '后端返回复盘'

    try {
      localStorage.setItem(
        REVIEW_RESULT_STORAGE_KEY,
        JSON.stringify({
          request: reviewRequest.value,
          response: result,
        }),
      )
    } catch {
      // restricted browser sessions may block storage writes
    }
  } catch {
    reviewError.value = '复盘生成失败，请返回模拟页后重试'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  void initReview()
})

</script>

<template>
  <main class="page review-page bg-diagonal-stripes">
    <span class="review-bg-ball review-bg-ball-yellow" aria-hidden="true"></span>
    <span class="review-bg-ball review-bg-ball-green" aria-hidden="true"></span>
    <span class="review-bg-ball review-bg-ball-square" aria-hidden="true"></span>

    <section class="review-hero card-border pop-card pop-shadow">
      <h1 class="review-hero-title">沟通复盘报告</h1>
      <p>
        {{ reviewResponse.summary || '当前对话复盘已生成' }}
      </p>
      <p v-if="reviewResponse.is_demo" class="analysis-source-badge">
        {{ reviewResponse.demo_notice || '演示复盘（未接入后端）' }}
      </p>
    </section>

    <section class="review-summary-card card-border pop-card pop-shadow">
      <div class="section-title-wrap">
        <h2>表现总结</h2>
        <p>表达总结</p>
      </div>
      <div class="review-score-grid">
        <article v-for="card in scoreCards" :key="card.title" class="review-score-card card-border pop-card">
          <div class="review-score-ring">
            <strong>{{ card.value }}%</strong>
          </div>
          <h3>{{ card.title }}</h3>
          <p>{{ card.description }}</p>
        </article>
      </div>
    </section>

    <div class="review-squiggle" aria-hidden="true"></div>

    <section class="review-summary-card card-border pop-card pop-shadow">
      <div class="section-title-wrap">
        <h2>复盘维度</h2>
        <p>表达优点 / 潜在问题</p>
      </div>
      <div class="review-section-grid">
        <article class="review-sticker-card card-border pop-card">
          <div class="review-sticker-badge">+1</div>
          <h3>本次表达的优点</h3>
          <ul>
            <li v-for="item in toSafeArray(reviewResponse.strengths)" :key="`strength-${item}`">
              {{ item }}
            </li>
          </ul>
        </article>
        <article class="review-sticker-card card-border pop-card">
          <div class="review-sticker-badge">A</div>
          <h3>感受表达</h3>
          <p>{{ rewriteSuggestion.feeling_expression }}</p>
        </article>
        <article class="review-sticker-card card-border pop-card">
          <div class="review-sticker-badge">!</div>
          <h3>可能引发防御心理的表述</h3>
          <ul>
            <li v-for="item in toSafeArray(reviewResponse.risks)" :key="`risk-${item}`">
              {{ item }}
            </li>
          </ul>
          <p class="review-risk-example">示例：{{ rewriteSuggestion.instead }}</p>
        </article>
        <article class="review-sticker-card card-border pop-card">
          <div class="review-sticker-badge">?</div>
          <h3>沟通空间</h3>
          <p>{{ rewriteSuggestion.communication_space }}</p>
        </article>
      </div>
    </section>

    <div class="review-squiggle review-squiggle-soft" aria-hidden="true"></div>

    <section class="review-summary-card card-border pop-card pop-shadow">
      <div class="section-title-wrap">
        <h2>优化后的沟通话术</h2>
        <p>优化话术</p>
      </div>
      <div class="review-speech-grid">
        <article class="review-speech-card card-border pop-card">
          <p class="review-tag">感受表达</p>
          <p>{{ rewriteSuggestion.feeling_expression }}</p>
        </article>
        <article class="review-speech-card card-border pop-card">
          <p class="review-tag">具体请求</p>
          <p>{{ rewriteSuggestion.specific_request }}</p>
        </article>
        <article class="review-speech-card card-border pop-card">
          <p class="review-tag">沟通空间</p>
          <p>{{ rewriteSuggestion.communication_space }}</p>
        </article>
      </div>

      <div class="speech-rewrite-row card-border pop-card">
        <article class="speech-before card-border pop-card">
          <p class="rewrite-label">而不是这样说</p>
          <p>{{ rewriteSuggestion.instead }}</p>
        </article>
        <div class="speech-arrow" aria-hidden="true">
          <span class="material-symbol">arrow_forward</span>
        </div>
        <article class="speech-after card-border pop-card">
          <p class="rewrite-label">建议这样说</p>
          <p>{{ rewriteSuggestion.instead_after }}</p>
        </article>
      </div>
    </section>

    <section class="review-summary-card card-border pop-card pop-shadow review-bottom-grid">
      <article class="review-block card-border pop-card">
        <div class="section-title-wrap">
          <h2>后续行动建议</h2>
        </div>
        <ul>
          <li v-for="item in toSafeArray(reviewResponse.next_steps)" :key="`next-${item}`">
            {{ item }}
          </li>
        </ul>
      </article>
      <article class="review-block card-border pop-card">
        <div class="section-title-wrap">
          <h2>安全提示</h2>
        </div>
        <p>{{ reviewResponse.safety_note }}</p>
      </article>
    </section>

    <p v-if="reviewError" class="chat-hint-label review-error">{{ reviewError }}</p>

    <section class="review-actions">
      <RouterLink class="primary-action pop-shadow" :to="{ name: 'simulate' }">
        再次演练
        <span class="action-icon material-symbol">refresh</span>
      </RouterLink>
      <RouterLink class="secondary-action pop-shadow" :to="{ name: 'home' }">
        返回首页
        <span class="action-icon material-symbol">home</span>
      </RouterLink>
    </section>

    <p v-if="isLoading" class="chat-hint-label review-loading">正在生成复盘...</p>
    <p v-if="canRender" class="review-note">
      {{ reviewSource || (reviewResponse.is_demo ? '复盘结果来自演示模式' : '复盘结果已渲染') }}
      <span v-if="reviewRequest.scenario">｜场景：{{ reviewRequest.scenario }}</span>
    </p>
  </main>
</template>
