import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = dirname(dirname(fileURLToPath(import.meta.url)))
const failures = []

function read(relativePath) {
  const absolutePath = join(root, relativePath)
  if (!existsSync(absolutePath)) {
    failures.push(`Missing file: ${relativePath}`)
    return ''
  }

  return readFileSync(absolutePath, 'utf8')
}

function requireIncludes(relativePath, phrases) {
  const content = read(relativePath)

  for (const phrase of phrases) {
    if (!content.includes(phrase)) {
      failures.push(`${relativePath} is missing "${phrase}"`)
    }
  }
}

function requireRegex(relativePath, pattern, description) {
  const content = read(relativePath)

  if (!pattern.test(content)) {
    failures.push(`${relativePath} is missing ${description}`)
  }
}

requireIncludes('package.json', ['"verify:phase2": "node scripts/verify-phase2.mjs"'])

requireIncludes('src/router/index.ts', [
  "'/simulate'",
  "name: 'simulate'",
  'SimulationView.vue',
  "'/review'",
  "name: 'review'",
  'ReviewView.vue',
])

requireIncludes('src/App.vue', ['沟通模拟', '沟通复盘', "name: 'simulate'", "name: 'review'"])

requireIncludes('src/data/week1.ts', [
  'ANALYSIS_RESULT_STORAGE_KEY',
  'SIMULATION_RESULT_STORAGE_KEY',
  'REVIEW_RESULT_STORAGE_KEY',
  'submitAnalyzeRequest',
  'submitSimulationRequest',
  'submitReviewRequest',
  '/api/analyze',
  '/api/simulate',
  '/api/review',
  'SimulationResponsePayload',
  'isSimulationResponsePayload',
  'normalizeSimulationResponse',
  'ReviewResponsePayload',
  'isReviewResponsePayload',
  'hasCompatibleSourceFields',
  'normalizeAnalyzeResponse',
  'buildDemoSimulationResponse',
  'buildDemoReviewResponse',
])

requireIncludes('src/views/RecordView.vue', [
  'submitAnalyzeRequest',
  'ANALYSIS_RESULT_STORAGE_KEY',
  'isSubmitting',
  'submitError',
])

requireIncludes('src/views/AnalysisView.vue', [
  'ANALYSIS_RESULT_STORAGE_KEY',
  'recommend_simulation',
  "name: 'simulate'",
  '进入沟通演练',
])

requireIncludes('src/views/SimulationView.vue', [
  '沟通模拟',
  '夜间噪音冲突',
  '场景选择',
  '选择演练场景',
  '沟通话术',
  'AI 舍友库',
  '对话模拟器',
  '当前场景：',
  '建议先表达感受，再提出具体请求',
  '重置',
  '发送',
  'submitSimulationRequest',
  'SIMULATION_RESULT_STORAGE_KEY',
  '舍友 A',
  '直接型',
  '舍友 B',
  '回避型',
  '舍友 C',
  '调和型',
  "name: 'review'",
])

requireIncludes('src/views/ReviewView.vue', [
  '沟通复盘报告',
  '表现总结',
  'Clarity',
  'Empathy',
  'Resolution',
  '复盘维度',
  '本次表达的优点',
  '感受表达',
  '可能引发防御心理的表述',
  '沟通空间',
  '优化后的沟通话术',
  '而不是这样说',
  '建议这样说',
  '表达总结',
  '表达优点',
  '潜在问题',
  '优化话术',
  '后续行动建议',
  '安全提示',
  'submitReviewRequest',
  'REVIEW_RESULT_STORAGE_KEY',
])

requireIncludes('src/styles/main.css', [
  'simulation-page',
  'simulation-header-card',
  'roommate-grid',
  'roommate-card',
  'chat-panel',
  'chat-bubble',
  'simulation-input-bar',
  'review-page',
  'review-hero-title',
  'review-score-grid',
  'review-section-grid',
  'speech-rewrite-row',
])

requireRegex(
  'src/views/AnalysisView.vue',
  /RouterLink[\s\S]*name:\s*'simulate'[\s\S]*进入沟通演练/,
  'analysis page action that routes to simulation',
)

requireRegex(
  'src/views/SimulationView.vue',
  /RouterLink[\s\S]*name:\s*'review'[\s\S]*生成复盘报告/,
  'simulation page action that routes to review',
)

requireRegex(
  'src/data/week1.ts',
  /if\s*\(!isSimulationResponsePayload\(raw\)\)/,
  'simulation API guard that accepts payloads without source fields before normalization',
)

requireRegex(
  'src/data/week1.ts',
  /is_demo:\s*typeof raw\.is_demo === 'boolean'\s*\?\s*raw\.is_demo\s*:\s*false/,
  'simulation response normalization default for missing is_demo',
)

requireRegex(
  'src/data/week1.ts',
  /if\s*\(!isReviewResponsePayload\(raw\)\)/,
  'review API guard that accepts payloads without source fields before normalization',
)

requireRegex(
  'src/data/week1.ts',
  /is_demo:\s*typeof raw\.is_demo === 'boolean'\s*\?\s*raw\.is_demo\s*:\s*false/,
  'review response normalization default for missing is_demo',
)

if (failures.length > 0) {
  console.error('Phase 2 verification failed:')
  for (const failure of failures) {
    console.error(`- ${failure}`)
  }
  process.exit(1)
}

console.log('Phase 2 verification passed.')
