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

function requireRegex(relativePath, pattern, description) {
  const content = read(relativePath)

  if (!pattern.test(content)) {
    failures.push(`${relativePath} is missing ${description}`)
  }
}

function requireCssRuleIncludes(relativePath, selector, declarations) {
  const content = read(relativePath)
  const rule = content.match(new RegExp(`${selector.replaceAll('.', '\\.')}\\s*\\{([^}]*)\\}`))

  if (!rule) {
    failures.push(`${relativePath} is missing ${selector} rule`)
    return
  }

  const ruleDeclarations = rule[1]
    .split(';')
    .map((declaration) => declaration.trim())
    .filter(Boolean)

  for (const declaration of declarations) {
    if (!ruleDeclarations.includes(declaration)) {
      failures.push(`${relativePath} ${selector} rule is missing "${declaration}"`)
    }
  }
}

function requireCssRuleExcludes(relativePath, selector, declarations) {
  const content = read(relativePath)
  const rule = content.match(new RegExp(`${selector.replaceAll('.', '\\.')}\\s*\\{([^}]*)\\}`))

  if (!rule) {
    failures.push(`${relativePath} is missing ${selector} rule`)
    return
  }

  const ruleDeclarations = rule[1]
    .split(';')
    .map((declaration) => declaration.trim())
    .filter(Boolean)

  for (const declaration of declarations) {
    if (ruleDeclarations.includes(declaration)) {
      failures.push(`${relativePath} ${selector} rule should not include "${declaration}"`)
    }
  }
}

requireIncludes('src/router/index.ts', ['/', '/record', '/analysis', 'HomeView', 'RecordView', 'AnalysisView'])
requireIncludes('index.html', [
  'fonts.googleapis.com/css2',
  'Material Symbols Outlined',
  'Outfit',
  'Plus Jakarta Sans',
])
requireIncludes('src/App.vue', ['RouterLink', 'RouterView'])
requireIncludes('src/App.vue', [
  'app-layout',
  'sidebar',
  'mobile-nav',
  'mobile-report',
  'material-symbol',
  'Report',
  'Performance',
  'AI Sandbox',
  'summarize',
  'settings',
  'mobile-avatar',
])
requireExcludes('src/App.vue', ['<span class="mobile-nav-cn">复盘</span>'])
requireIncludes('src/styles/main.css', [
  'dot-grid',
  'bg-diagonal-stripes',
  'pop-card',
  'pop-shadow',
  'card-border',
  'shape-confetti',
  'record-decoration',
  'dashboard-card',
  'feature-card-visual',
  'flow-section',
  'mobile-nav',
  'analysis-bento',
])
requireRegex(
  'src/styles/main.css',
  /\.sidebar\.pop-shadow:hover[\s\S]*transform:\s*none/,
  'sidebar hover override that prevents whole-sidebar movement',
)
requireCssRuleIncludes('src/styles/main.css', '.sidebar', ['position: relative', 'min-height: 100vh'])
requireCssRuleExcludes('src/styles/main.css', '.sidebar', [
  'position: sticky',
  'position: fixed',
  'top: 0',
  'height: 100vh',
])

requireIncludes('src/views/HomeView.vue', [
  '舍友心晴',
  '大学生宿舍压力预警与沟通演练助手',
  '开始记录',
  'hero-squiggle',
  'dashboard-card',
  'AI 深度分析',
  '沟通模拟器',
  '关系改善趋势',
  '开启分析',
  '进入沙盒',
  '查看报告',
  'pop-card',
  'pop-shadow',
  'feature-card-visual',
  'safety-modal-overlay',
  'safety-modal',
  '首次使用提示',
  '使用前请了解安全边界',
  '不进行心理疾病诊断',
  '不评价任何舍友的人格或心理状态',
  'Demo 阶段不采集真实身份信息',
  '我已了解，开始使用',
])
requireExcludes('src/views/HomeView.vue', ['flow-section', 'flowSteps', '开始记录宿舍事件'])

requireIncludes('src/views/RecordView.vue', [
  '事件类型',
  '严重程度',
  '发生频率',
  '当前情绪',
  '是否已经沟通',
  '是否出现争吵或冷战',
  '简要描述',
  '写下当时的具体情况...',
  'range-tick-list',
  '保存并分析',
  'record-option',
  'pop-card',
  'field-icon',
  'record-decoration',
])

requireIncludes('src/views/AnalysisView.vue', [
  '压力分数',
  '风险等级',
  '主要压力来源',
  '卫生 (Hygiene)',
  '情绪关键词',
  '是否推荐进入 AI 沟通模拟',
  '系统建议',
  '安全提示',
  '76',
  '冲突风险较高',
  '进入沟通演练',
  'bg-diagonal-stripes',
  'score-ring',
  'insight-card',
])
requireExcludes('src/views/AnalysisView.vue', ['disabled', '第二阶段接入', '沟通缺口'])

requireIncludes('docs/api/analyze-field-map.md', [
  '/api/analyze',
  'event_type',
  'severity',
  'frequency',
  'emotion',
  'has_communicated',
  'has_conflict',
  'description',
  'pressure_score',
  'risk_level',
  'main_reasons',
  'suggestions',
  'safety_notice',
])

if (failures.length > 0) {
  console.error('Week 1 verification failed:')
  for (const failure of failures) {
    console.error(`- ${failure}`)
  }
  process.exit(1)
}

console.log('Week 1 verification passed.')
