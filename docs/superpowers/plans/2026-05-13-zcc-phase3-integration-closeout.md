# 朱春雯第三阶段联调收尾 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Zhu Chunwen's phase-3 integration closeout by making local frontend-backend calls stable, normalizing known review payload mismatches, and recording the phase-3 backend/documentation evidence.

**Architecture:** Keep FastAPI as the source of backend contract truth, add narrow compatibility normalization in Pydantic schemas, add CORS middleware for local demo origins, and let Vite proxy `/api/*` to the backend in development. Documentation records current implementation versus remaining demo/material limits.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, pytest, Vue/Vite static configuration, Node.js script-based static verification.

---

## File Structure

Create:

- `frontend/scripts/verify-phase3.mjs`: static verifier for Vite proxy and phase-3 script registration.
- `docs/phase3-status.md`: phase-3 Zhu Chunwen status, integration results, fixes, technical notes, and limits.

Modify:

- `backend/app/main.py`: add configurable CORS middleware.
- `backend/app/schemas.py`: normalize known frontend review speaker and original event aliases.
- `backend/tests/test_api.py`: add failing tests for CORS and frontend-compatible review payloads.
- `frontend/vite.config.ts`: add `/api` dev proxy to backend.
- `frontend/package.json`: add `verify:phase3` script.
- `README.md`: update current status and local full-demo startup notes.
- `docs/backend-api-contract.md`: document local integration config and accepted compatibility aliases.
- `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`: add phase-3 current status evidence for B3-1 to B3-5.
- `docs/sheyou-xinqing-planning.md`: align final planning document with current implementation and limits.

Do not modify:

- Frontend page UI/layout files.
- Video, poster, screenshot, or final online submission assets.
- History/storage runtime endpoints.

---

### Task 1: Backend Integration Compatibility

**Files:**
- Modify: `backend/tests/test_api.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/schemas.py`

- [ ] **Step 1: Write failing tests**

Append these tests to `backend/tests/test_api.py`:

```python
def test_cors_preflight_allows_local_vite_frontend():
    response = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_review_endpoint_accepts_frontend_display_payload_until_ai_config_check():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "舍友晚上打游戏太吵",
            "dialogue": [
                {"speaker": "你", "message": "晚上能不能小声一点？"},
                {"speaker": "舍友 A（直接型）", "message": "我也没开很大声吧。"},
                {"speaker": "舍友 C（调和型）", "message": "我们一起定个安静时间吧。"},
            ],
            "original_event": {
                "event_type": "noise_conflict",
                "frequency": "weekly_multiple",
                "risk_level": "high",
                "pressure_score": 76,
                "description": "舍友晚上打游戏声音比较大。",
            },
        },
    )

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_review_endpoint_ignores_analysis_only_event_alias_until_ai_config_check():
    app.dependency_overrides[get_ai_service] = lambda: MissingKeyService()

    response = client.post(
        "/api/review",
        json={
            "scenario": "沟通复盘场景",
            "dialogue": [{"speaker": "用户", "message": "我想先说清楚我的睡眠受影响了。"}],
            "original_event": {
                "event_type": "risk-high",
                "risk_level": "high",
                "pressure_score": 76,
            },
        },
    )

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
```

- [ ] **Step 2: Verify RED**

Run:

```bash
cd backend
python3 -m pytest tests/test_api.py::test_cors_preflight_allows_local_vite_frontend tests/test_api.py::test_review_endpoint_accepts_frontend_display_payload_until_ai_config_check tests/test_api.py::test_review_endpoint_ignores_analysis_only_event_alias_until_ai_config_check -q
```

Expected: FAIL. Current app has no CORS middleware, and current schema rejects display speaker aliases / `risk-high` event aliases before reaching the AI configuration check.

- [ ] **Step 3: Implement CORS**

In `backend/app/main.py`, import `os` and `CORSMiddleware`, then add:

```python
DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def load_cors_origins() -> list[str]:
    raw_origins = os.getenv("DORM_HARMONY_CORS_ORIGINS", "").strip()
    if not raw_origins:
        return list(DEFAULT_CORS_ORIGINS)

    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or list(DEFAULT_CORS_ORIGINS)
```

After creating `app = FastAPI(...)`, add:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=load_cors_origins(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

- [ ] **Step 4: Implement schema normalization**

In `backend/app/schemas.py`, add alias maps near the response/request type aliases:

```python
_DIALOGUE_SPEAKER_ALIASES = {
    "你": "user",
    "用户": "user",
    "我": "user",
    "舍友 A": "roommate_a",
    "舍友A": "roommate_a",
    "舍友 A（直接型）": "roommate_a",
    "舍友 B": "roommate_b",
    "舍友B": "roommate_b",
    "舍友 B（回避型）": "roommate_b",
    "舍友 C": "roommate_c",
    "舍友C": "roommate_c",
    "舍友 C（调和型）": "roommate_c",
    "系统": "system",
}

_EVENT_TYPE_ALIASES = {
    "noise_conflict": EventType.NOISE,
    "schedule_conflict": EventType.SCHEDULE,
    "hygiene_conflict": EventType.HYGIENE,
    "expense_conflict": EventType.COST,
    "privacy_boundary": EventType.PRIVACY,
    "emotional_conflict": EventType.EMOTION,
}
```

Add a before validator to `DialogueMessage.speaker`:

```python
    @field_validator("speaker", mode="before")
    @classmethod
    def normalize_speaker_alias(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("speaker must be a string")

        speaker = value.strip()
        return _DIALOGUE_SPEAKER_ALIASES.get(speaker, speaker)
```

Add a before validator to `ReviewOriginalEvent.event_type`:

```python
    @field_validator("event_type", mode="before")
    @classmethod
    def normalize_optional_event_type(cls, value: str | None) -> str | EventType | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("event_type must be a string")

        event_type = value.strip()
        if not event_type or event_type.startswith("risk-"):
            return None

        return _EVENT_TYPE_ALIASES.get(event_type, event_type)
```

- [ ] **Step 5: Verify GREEN**

Run:

```bash
cd backend
python3 -m pytest tests/test_api.py::test_cors_preflight_allows_local_vite_frontend tests/test_api.py::test_review_endpoint_accepts_frontend_display_payload_until_ai_config_check tests/test_api.py::test_review_endpoint_ignores_analysis_only_event_alias_until_ai_config_check -q
```

Expected: PASS.

---

### Task 2: Frontend Local Proxy Verification

**Files:**
- Create: `frontend/scripts/verify-phase3.mjs`
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.ts`

- [ ] **Step 1: Write failing static verifier**

Create `frontend/scripts/verify-phase3.mjs`:

```javascript
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
```

- [ ] **Step 2: Verify RED**

Run:

```bash
cd frontend
node scripts/verify-phase3.mjs
```

Expected: FAIL because the script is not registered and `vite.config.ts` has no `/api` proxy.

- [ ] **Step 3: Add Vite proxy and script**

In `frontend/package.json`, add:

```json
"verify:phase3": "node scripts/verify-phase3.mjs"
```

In `frontend/vite.config.ts`, add:

```typescript
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
cd frontend
node scripts/verify-phase3.mjs
```

Expected: PASS.

---

### Task 3: Phase-3 Documentation Closeout

**Files:**
- Create: `docs/phase3-status.md`
- Modify: `README.md`
- Modify: `docs/backend-api-contract.md`
- Modify: `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`
- Modify: `docs/sheyou-xinqing-planning.md`

- [ ] **Step 1: Draft status document**

Create `docs/phase3-status.md` with sections for scope, integration result, fixed issues, technical notes, final planning status, and limits. Include B3-1 through B3-5 table and explicitly state that video/poster/screenshots remain outside Zhu Chunwen backend closeout.

- [ ] **Step 2: Update existing docs**

Update:

- `README.md`: current status, local full-demo commands, CORS env variable, phase3 status link.
- `docs/backend-api-contract.md`: local integration config and compatibility aliases.
- `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`: B3-1 to B3-5 current status table.
- `docs/sheyou-xinqing-planning.md`: final implementation state and development limits.

- [ ] **Step 3: Review docs for stale claims**

Search for claims that third stage is still wholly future:

```bash
rg -n "第三阶段完整 Demo|前端完整联调仍属后续范围|当前第二阶段" README.md docs/backend-api-contract.md docs/phase3-status.md DEVELOPMENT_PLAN_AND_DELIVERABLES.md docs/sheyou-xinqing-planning.md
```

Expected: any remaining references should be deliberately scoped as remaining limits, not stale current status.

---

### Task 4: Final Verification and Review

**Files:**
- All changed files from Tasks 1-3

- [ ] **Step 1: Run backend tests**

```bash
cd backend
python3 -m pytest
```

Expected: all tests pass.

- [ ] **Step 2: Run frontend static verifiers**

```bash
cd frontend
node scripts/verify-phase2.mjs
node scripts/verify-phase3.mjs
```

Expected: both scripts pass.

- [ ] **Step 3: Check dependency-limited frontend build**

```bash
ls frontend/node_modules
```

Expected in current workspace: directory missing. Record that full `npm run build` requires installing frontend dependencies first.

- [ ] **Step 4: Request subagent reviews**

Dispatch one spec-compliance reviewer and one code-quality reviewer with the changed-file list, phase-3 requirements, and verification results. Fix Critical/Important findings before final response.

- [ ] **Step 5: Final status**

Report branch name, files changed, verification commands, any unrun checks, and remind that the branch was not pushed or published.
