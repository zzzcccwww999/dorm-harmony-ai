# Cao Le Phase 3 Frontend Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Cao Le's Phase 3 frontend closure tasks A3-1 through A3-5 with stable demo flow, responsive checks, screenshot materials, and runbook documentation.

**Architecture:** Keep the current Vue 3 + Router implementation and existing playful geometric CSS. Add only small frontend behavior hardening, cumulative verification scripts, and demo documentation under `frontend/docs/demo/`. Do not change backend code or make new product features beyond the Phase 3 closure scope.

**Tech Stack:** Vue 3, Vue Router, TypeScript, Vite, native browser `localStorage`, Node verification scripts.

---

### Task 1: Phase 3 Verification Harness

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/scripts/verify-week1.mjs`
- Create: `frontend/scripts/verify-phase3.mjs`

- [x] Add `verify:phase3` to `package.json`.
- [x] Update `verify-week1.mjs` so it validates the current accepted first-stage baseline instead of stale three-page English navigation text.
- [x] Create `verify-phase3.mjs` to check five routes, flow hardening markers, responsive CSS markers, and demo documentation files.
- [x] Run `npm run verify:phase3` before implementation and confirm it fails on missing Phase 3 markers.

### Task 2: Flow And UI Hardening

**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/views/HomeView.vue`
- Modify: `frontend/src/views/RecordView.vue`
- Modify: `frontend/src/views/AnalysisView.vue`
- Modify: `frontend/src/views/SimulationView.vue`
- Modify: `frontend/src/views/ReviewView.vue`
- Modify: `frontend/src/styles/main.css`
- Modify: `frontend/scripts/verify-phase3.mjs`

- [x] Keep desktop and mobile navigation in the demo flow order: home, record, analysis, simulate, review.
- [x] Make homepage feature card actions route to the corresponding real pages instead of disabled or mismatched destinations.
- [x] Add client-side record description validation and keep submit loading/error visible.
- [x] Improve analysis-to-simulation context so the simulation request carries useful risk, source, emotion, trend and suggestion details.
- [x] Make the pressure score ring reflect the current `pressure_score` instead of a static visual value.
- [x] Prevent the simulation page from sending users to review before at least one simulation response has been generated or restored from cache.
- [x] Keep simulation and review pages usable when localStorage contains malformed or missing data.
- [x] Add responsive CSS constraints for mobile bottom navigation, long labels, simulation input, chat replies, and review rewrite rows.
- [x] Run `npm run verify:week1`, `npm run verify:phase2`, `npm run verify:phase3`, and `npm run build`.

### Task 3: Demo Materials And Closure Notes

**Files:**
- Create: `frontend/docs/demo/phase3-frontend-fix-log.md`
- Create: `frontend/docs/demo/phase3-responsive-check.md`
- Create: `frontend/docs/demo/phase3-screenshot-materials.md`
- Create: `frontend/docs/demo/phase3-demo-runbook.md`
- Modify: `DEVELOPMENT_PLAN_AND_DELIVERABLES.md`

- [x] Document A3-1/A3-2 fixes and remaining non-blocking limits.
- [x] Document desktop/tablet/mobile responsive check points.
- [x] Document screenshot filenames, pages, and capture notes.
- [x] Document the stable noise-conflict demo path from home through review.
- [x] Add a short Cao Le Phase 3 status table to the development plan.
- [x] Run all frontend verification commands again.

### Task 4: Screenshot Materials And Final Review

**Files:**
- Create: `frontend/docs/demo/screenshots/home.png`
- Create: `frontend/docs/demo/screenshots/record.png`
- Create: `frontend/docs/demo/screenshots/analysis.png`
- Create: `frontend/docs/demo/screenshots/simulate.png`
- Create: `frontend/docs/demo/screenshots/review.png`

- [x] Retain the five existing page screenshot PNG files in `frontend/docs/demo/screenshots/`.
- [x] Verify screenshot files exist and are non-empty through `verify:phase3`.
- [x] Complete final integration review against the accepted Phase 3 scope.
- [x] Run final `npm run verify:week1`, `npm run verify:phase2`, `npm run verify:phase3`, and `npm run build`.
