# Cao Le Phase 2 Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Cao Le's Phase 2 frontend tasks A2-1 through A2-6: connect analyze, add communication simulation, display role replies, add review report, and wire the page flow.

**Architecture:** Keep the existing Vue 3 + Router single-page structure and playful geometric design system. Treat `frontend/页面设计-策划书对齐/沟通模拟/code.html` and `frontend/页面设计-策划书对齐/沟通复盘报告/code.html` as the visual source of truth; Vue implementation must restore their layout, section hierarchy, key copy, card/bubble styling, and hard-shadow geometric treatment while only replacing static values with stateful data bindings. Add a small frontend API/data layer for Phase 2 contracts, persist demo flow state in `localStorage`, and add two routed pages: `/simulate` and `/review`.

**Tech Stack:** Vue 3, Vue Router, TypeScript, Vite, existing CSS in `frontend/src/styles/main.css`, native `fetch`, local `verify:phase2` script.

---

## Task 1: A2-1 Analyze API Wiring

**Files:**
- Modify: `frontend/src/data/week1.ts`
- Modify: `frontend/src/views/RecordView.vue`
- Modify: `frontend/src/views/AnalysisView.vue`
- Test: `frontend/scripts/verify-phase2.mjs`

- [x] Run `npm run verify:phase2` and confirm it fails because Phase 2 flow is missing.
- [x] Map frontend option values to backend contract values for `/api/analyze`.
- [x] Submit the event form to `/api/analyze`, store the request and normalized response, and navigate to `analysis`.
- [x] On analysis, render stored API data, loading/error states, and a link to `simulate`.
- [x] If the backend endpoint is unavailable, store the local demo fallback and label it as demo fallback so the page flow remains demonstrable.
- [x] Run `npm run verify:phase2` and `npm run build`.

## Task 2: A2-2 to A2-4 Simulation Page

**Files:**
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/App.vue`
- Create: `frontend/src/views/SimulationView.vue`
- Modify: `frontend/src/data/week1.ts`
- Modify: `frontend/src/styles/main.css`
- Test: `frontend/scripts/verify-phase2.mjs`

- [x] Add route `/simulate` named `simulate`.
- [x] Add sidebar and mobile navigation entries for `沟通模拟`.
- [x] Restore the static design structure: `夜间噪音冲突` header chip, `选择演练场景`, `AI 舍友库`, `对话模拟器`, character cards, chat message area, input bar, reset button, hard borders, hard shadows, and geometric decorations.
- [x] Call `/api/simulate` with `scenario`, `user_message`, `risk_level`, and `context`.
- [x] Render role cards and chat bubbles for `舍友 A（直接型）`, `舍友 B（回避型）`, and `舍友 C（调和型）` with the same visual hierarchy as the static design.
- [x] Store the simulation request/replies for review and provide a route action to `review`.
- [x] If `/api/simulate` is unavailable, show structured demo fallback replies and keep the flow usable.
- [x] Run `npm run verify:phase2` and `npm run build`.

## Task 3: A2-5 to A2-6 Review Report Page

**Files:**
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/App.vue`
- Create: `frontend/src/views/ReviewView.vue`
- Modify: `frontend/src/data/week1.ts`
- Modify: `frontend/src/styles/main.css`
- Test: `frontend/scripts/verify-phase2.mjs`

- [x] Add route `/review` named `review`.
- [x] Add sidebar and mobile navigation entries for `沟通复盘`.
- [x] Restore the static report structure: oversized `沟通复盘报告` header with yellow underline block, decorative circle/square, `表现总结` score cards (`Clarity`, `Empathy`, `Resolution`), `复盘维度`, `优化后的沟通话术`, before/after speech cards, `后续行动建议`, `安全提示`, and bottom action buttons.
- [x] Call `/api/review` using the stored simulation dialogue and original event summary.
- [x] Store and render the review response; if the endpoint is unavailable, render a structured demo fallback.
- [x] Ensure the path `record -> analysis -> simulate -> review` is visible and stable.
- [x] Run `npm run verify:phase2`, `npm run build`, and request final review.
