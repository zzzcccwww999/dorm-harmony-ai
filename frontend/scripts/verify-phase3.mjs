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

requireIncludes('package.json', ['"verify:phase3": "node scripts/verify-phase3.mjs"'])

requireIncludes('vite.config.ts', [
  'server:',
  'proxy:',
  "'/api'",
  'http://127.0.0.1:8000',
  'changeOrigin: true',
])

requireIncludes('src/data/week1.ts', ['/api/analyze', '/api/simulate', '/api/review'])

function requireExists(relativePath) {
  const absolutePath = join(root, relativePath)
  if (!existsSync(absolutePath)) {
    failures.push(`Missing file: ${relativePath}`)
  }
}

function requireNoMarkdownFormatArtifacts(relativePath) {
  const content = read(relativePath)

  if (content.includes('\\n')) {
    failures.push(`${relativePath} should not include literal escaped newline markers`)
  }

  if (content.includes('\r')) {
    failures.push(`${relativePath} should use LF line endings`)
  }
}

const requiredFiles = [
  {
    path: 'docs/demo/phase3-frontend-fix-log.md',
    phrases: [
      'A3-1',
      'A3-2',
      '导航顺序',
      '首页入口',
      '记录页空描述',
      '动态压力环',
      '模拟复盘门禁',
      '后端不可用演示兜底',
    ],
  },
  {
    path: 'docs/demo/phase3-responsive-check.md',
    phrases: [
      'A3-3',
      '移动底部导航',
      '表单选项',
      '聊天气泡',
      '复盘报告',
      '无横向溢出',
    ],
  },
  {
    path: 'docs/demo/phase3-screenshot-materials.md',
    phrases: [
      'A3-4',
      '截图素材',
      'home.png',
      'record.png',
      'analysis.png',
      'simulate.png',
      'review.png',
      '首页',
      '事件记录',
      '压力分析',
      '沟通模拟',
      '沟通复盘',
    ],
  },
  {
    path: 'docs/demo/phase3-demo-runbook.md',
    phrases: [
      'A3-5',
      '夜间噪音冲突',
      'home -> record -> analysis -> simulate -> review',
      '可无后端兜底',
      '录制视频',
    ],
  },
]

for (const file of requiredFiles) {
  requireIncludes(file.path, file.phrases)
}

for (const screenshot of [
  'docs/demo/screenshots/home.png',
  'docs/demo/screenshots/record.png',
  'docs/demo/screenshots/analysis.png',
  'docs/demo/screenshots/simulate.png',
  'docs/demo/screenshots/review.png',
]) {
  requireExists(screenshot)
}

for (const markdownFile of [
  'docs/demo/phase3-frontend-fix-log.md',
  'docs/demo/phase3-responsive-check.md',
  'docs/demo/phase3-screenshot-materials.md',
  'docs/demo/phase3-demo-runbook.md',
]) {
  requireNoMarkdownFormatArtifacts(markdownFile)
}

if (failures.length > 0) {
  console.error('Phase 3 verification failed:')
  for (const failure of failures) {
    console.error(`- ${failure}`)
  }
  process.exit(1)
}

console.log('Phase 3 verification passed.')
