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

if (failures.length > 0) {
  console.error('Phase 3 verification failed:')
  for (const failure of failures) {
    console.error(`- ${failure}`)
  }
  process.exit(1)
}

console.log('Phase 3 verification passed.')
