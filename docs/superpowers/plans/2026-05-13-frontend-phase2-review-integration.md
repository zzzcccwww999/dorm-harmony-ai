# Frontend Phase 2 Review Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the frontend truly call the phase-2 `/api/review` contract instead of falling back to demo data because of invalid request payloads.

**Architecture:** Keep API request normalization in `frontend/src/data/week1.ts` where existing backend enum mapping already lives. Keep `ReviewView.vue` responsible for composing page context, but make its dialogue lines and original event summaries use backend-safe values. Add a Vite dev proxy so local frontend/backend split-port development can call `/api/*`.

**Tech Stack:** Vue 3, Vite, TypeScript, Node verification script.

---

### Task 1: Phase 2 Verification Coverage

**Files:**
- Modify: `frontend/scripts/verify-phase2.mjs`

- [x] **Step 1: Write failing verification checks**

Require the phase-2 verification script to check for:
- backend-safe review dialogue speaker mapping
- backend-safe review original event enum mapping
- `/api` Vite dev proxy

- [ ] **Step 2: Run verification and confirm RED**

Run:

```bash
cd frontend
npm run verify:phase2
```

Expected before implementation: FAIL with messages for the missing review payload mapping and missing Vite proxy.

### Task 2: Review Payload Mapping and Dev Proxy

**Files:**
- Modify: `frontend/src/data/week1.ts`
- Modify: `frontend/src/views/ReviewView.vue`
- Modify: `frontend/vite.config.ts`

- [ ] **Step 1: Add shared frontend-to-backend enum mapping helpers**

Expose helpers for frontend legacy event values to backend event values, and for simulation replies to backend review speakers.

- [ ] **Step 2: Use backend speaker enums in review request payloads**

`ReviewView.vue` must send `user`, `roommate_a`, `roommate_b`, `roommate_c`, or `system`, not display labels like `你` or `舍友 A（直接型）`.

- [ ] **Step 3: Use backend event enums in `original_event`**

`ReviewView.vue` must send `noise`, `schedule`, `hygiene`, `cost`, `privacy`, or `emotion` when `original_event.event_type` is present.

- [ ] **Step 4: Add Vite `/api` proxy**

`frontend/vite.config.ts` should proxy `/api` to `http://127.0.0.1:8000` for local split-port development.

- [ ] **Step 5: Run verification and confirm GREEN**

Run:

```bash
cd frontend
npm run verify:phase2
npm run build
```

Expected after implementation: both pass.

### Task 3: Review Gates

**Files:**
- Read-only review across the changed files.

- [ ] **Step 1: Spec compliance review**

Confirm the implementation satisfies the plan and does not expand scope beyond the three frontend integration fixes.

- [ ] **Step 2: Code quality review**

Confirm the implementation follows existing frontend patterns, keeps display labels separate from API values, and does not introduce broad visual or routing changes.
