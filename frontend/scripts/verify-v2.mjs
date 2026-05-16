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

function requireExcludes(relativePath, phrases) {
  const content = read(relativePath)

  for (const phrase of phrases) {
    if (content.includes(phrase)) {
      failures.push(`${relativePath} should not include "${phrase}"`)
    }
  }
}

requireIncludes('package.json', ['"verify:v2": "node scripts/verify-v2.mjs"'])

requireIncludes('src/router/index.ts', [
  '/archive',
  "name: 'archive'",
  'EventArchiveView.vue',
])

requireIncludes('src/App.vue', ['事件档案', "name: 'archive'"])

requireIncludes('src/views/RecordView.vue', [
  'event_date',
  '事件日期',
  'createEventRecord',
])

requireIncludes('src/views/EventArchiveView.vue', [
  '事件档案',
  'fetchEventArchive',
  '生成压力分析报告',
  "name: 'analysis'",
])

requireIncludes('src/data/eventArchive.ts', [
  '/api/events',
  '/api/events/analysis',
  '/api/events/insight',
  'ArchiveAnalysisResponse',
  'ArchiveInsightResponse',
  'source_breakdown',
  'communication_focus',
])

requireIncludes('src/styles/main.css', [
  'archive-page',
  'event-timeline',
  'archive-event-card',
  'page-pop-in',
  'sticker-paste-in',
  'bounce-float',
  'typing-bounce',
  'prefers-reduced-motion',
])

requireIncludes('src/views/AnalysisView.vue', [
  'fetchArchiveAnalysis',
  'fetchArchiveInsight',
  'source_breakdown',
  'AI 心晴见解',
  '事件档案',
])
requireExcludes('src/views/AnalysisView.vue', ['Math.floor(100 / labels.length)'])

requireIncludes('src/views/SimulationView.vue', [
  'conversationMessages',
  'appendReplyWithDelay',
  'replyDelayMs',
  'dialogue',
  '正在生成',
])
requireExcludes('src/views/SimulationView.vue', ['replies.value = result.replies'])

requireIncludes('src/views/ReviewView.vue', ['storedDialogue', '完整对话'])

if (failures.length > 0) {
  console.error('v2 verification failed:')
  for (const failure of failures) {
    console.error(`- ${failure}`)
  }
  process.exit(1)
}

console.log('v2 verification passed')
