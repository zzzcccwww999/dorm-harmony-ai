# Page Design Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a new static page-design set that strictly aligns with the product plan while preserving the original visual style and leaving `frontend/页面设计/` unchanged.

**Architecture:** Build a separate `frontend/页面设计-策划书对齐/` directory by copying the original static design files as visual baselines, then make content-only and local structural adjustments required by the spec. Shared safety and navigation notes live under `shared/`; every page remains a static HTML design artifact, not Vue code.

**Tech Stack:** Static HTML, existing Tailwind CDN design files, Markdown design notes, Git verification commands.

---

## File Structure

Create:

```text
frontend/页面设计-策划书对齐/
frontend/页面设计-策划书对齐/首页/DESIGN.md
frontend/页面设计-策划书对齐/首页/code.html
frontend/页面设计-策划书对齐/事件记录/DESIGN.md
frontend/页面设计-策划书对齐/事件记录/code.html
frontend/页面设计-策划书对齐/压力分析/DESIGN.md
frontend/页面设计-策划书对齐/压力分析/code.html
frontend/页面设计-策划书对齐/沟通模拟/DESIGN.md
frontend/页面设计-策划书对齐/沟通模拟/code.html
frontend/页面设计-策划书对齐/沟通复盘报告/DESIGN.md
frontend/页面设计-策划书对齐/沟通复盘报告/code.html
frontend/页面设计-策划书对齐/shared/safety-modal.html
frontend/页面设计-策划书对齐/shared/navigation-notes.md
```

Do not create:

```text
frontend/页面设计-策划书对齐/**/screen.png
```

Do not modify:

```text
frontend/页面设计/**
frontend/src/**
```

---

### Task 1: Create the Aligned Design Directory

**Files:**
- Create: `frontend/页面设计-策划书对齐/**`
- Read-only source: `frontend/页面设计/**`

- [ ] **Step 1: Create page directories**

Run:

```bash
mkdir -p \
  'frontend/页面设计-策划书对齐/首页' \
  'frontend/页面设计-策划书对齐/事件记录' \
  'frontend/页面设计-策划书对齐/压力分析' \
  'frontend/页面设计-策划书对齐/沟通模拟' \
  'frontend/页面设计-策划书对齐/沟通复盘报告' \
  'frontend/页面设计-策划书对齐/shared'
```

Expected: command exits 0.

- [ ] **Step 2: Copy original HTML and design notes as visual baselines**

Run:

```bash
cp 'frontend/页面设计/首页/DESIGN.md' 'frontend/页面设计-策划书对齐/首页/DESIGN.md'
cp 'frontend/页面设计/首页/code.html' 'frontend/页面设计-策划书对齐/首页/code.html'
cp 'frontend/页面设计/事件记录/DESIGN.md' 'frontend/页面设计-策划书对齐/事件记录/DESIGN.md'
cp 'frontend/页面设计/事件记录/code.html' 'frontend/页面设计-策划书对齐/事件记录/code.html'
cp 'frontend/页面设计/压力分析/DESIGN.md' 'frontend/页面设计-策划书对齐/压力分析/DESIGN.md'
cp 'frontend/页面设计/压力分析/code.html' 'frontend/页面设计-策划书对齐/压力分析/code.html'
cp 'frontend/页面设计/沟通模拟/DESIGN.md' 'frontend/页面设计-策划书对齐/沟通模拟/DESIGN.md'
cp 'frontend/页面设计/沟通模拟/code.html' 'frontend/页面设计-策划书对齐/沟通模拟/code.html'
cp 'frontend/页面设计/沟通复盘报告/DESIGN.md' 'frontend/页面设计-策划书对齐/沟通复盘报告/DESIGN.md'
cp 'frontend/页面设计/沟通复盘报告/code.html' 'frontend/页面设计-策划书对齐/沟通复盘报告/code.html'
```

Expected: command exits 0 and copies only `DESIGN.md` and `code.html`.

- [ ] **Step 3: Verify no screenshots were copied**

Run:

```bash
find 'frontend/页面设计-策划书对齐' -name 'screen.png' -print
```

Expected: no output.

- [ ] **Step 4: Verify original design directory has no tracked changes**

Run:

```bash
git diff --name-only -- 'frontend/页面设计'
```

Expected: no output.

- [ ] **Step 5: Commit directory baseline**

Run:

```bash
git add 'frontend/页面设计-策划书对齐'
git commit -m "chore(frontend): 创建策划书对齐设计目录"
```

Expected: commit succeeds and does not include `screen.png`.

---

### Task 2: Add Shared Safety Modal and Navigation Notes

**Files:**
- Create: `frontend/页面设计-策划书对齐/shared/safety-modal.html`
- Create: `frontend/页面设计-策划书对齐/shared/navigation-notes.md`

- [ ] **Step 1: Create shared safety modal snippet**

Create `frontend/页面设计-策划书对齐/shared/safety-modal.html` with:

```html
<!-- 首次进入安全说明弹窗：静态设计稿片段，后续 Vue 实现时用 localStorage 控制只弹一次 -->
<div class="fixed inset-0 z-[100] flex items-center justify-center bg-on-surface/45 p-4">
  <section class="w-full max-w-2xl bg-card border-[3px] border-on-surface rounded-2xl shadow-[8px_8px_0px_0px] shadow-on-surface p-6 md:p-8">
    <div class="inline-flex items-center gap-2 rounded-full border-2 border-on-surface bg-tertiary px-4 py-2 text-label-bold font-label-bold text-on-surface shadow-[2px_2px_0px_0px] shadow-on-surface">
      <span class="material-symbols-outlined text-[18px]">verified_user</span>
      首次使用提示
    </div>
    <h2 class="mt-5 text-headline-md font-headline-md text-on-surface">使用前请了解安全边界</h2>
    <p class="mt-4 text-body-md font-body-md text-on-surface-variant">
      舍友心晴仅用于宿舍压力趋势提示和沟通练习，不进行心理疾病诊断，也不评价任何舍友的人格或心理状态。
    </p>
    <ul class="mt-5 space-y-3 text-body-md font-body-md text-on-surface">
      <li>压力值只用于关系压力趋势提示，不作为医学或心理诊断依据。</li>
      <li>如果出现高压力、严重冲突、持续失眠、强烈焦虑或暴力风险，请及时联系辅导员、心理老师、家人或可信任同学。</li>
      <li>Demo 阶段不采集真实身份信息，演示数据使用虚拟样例。</li>
    </ul>
    <div class="mt-6 flex flex-col gap-3 sm:flex-row">
      <button class="bg-primary text-on-primary border-2 border-on-surface rounded-full px-6 py-3 font-label-bold text-label-bold shadow-[4px_4px_0px_0px] shadow-on-surface">
        我已了解，开始使用
      </button>
      <button class="bg-surface text-on-surface border-2 border-on-surface rounded-full px-6 py-3 font-label-bold text-label-bold shadow-[4px_4px_0px_0px] shadow-on-surface">
        查看隐私原则
      </button>
    </div>
  </section>
</div>
```

- [ ] **Step 2: Create navigation notes**

Create `frontend/页面设计-策划书对齐/shared/navigation-notes.md` with:

```markdown
# 页面设计导航一致性说明

新设计沿用原 `frontend/页面设计/` 的侧边导航和移动端底部导航结构。

导航项统一为：

- 首页
- 事件记录
- 压力分析
- 沟通模拟
- 沟通复盘
- 安全说明

“安全说明”不是独立页面，而是首页弹窗的再次打开入口。静态设计稿中可以表现为按钮或导航项，后续 Vue 实现时由同一个安全弹窗组件处理。
```

- [ ] **Step 3: Verify safety copy exists**

Run:

```bash
rg -n "不进行心理疾病诊断|不评价任何舍友|辅导员|心理老师|Demo 阶段不采集真实身份信息" 'frontend/页面设计-策划书对齐/shared/safety-modal.html'
```

Expected: all five phrases are found.

- [ ] **Step 4: Commit shared files**

Run:

```bash
git add 'frontend/页面设计-策划书对齐/shared'
git commit -m "docs(frontend): 添加页面设计安全说明片段"
```

Expected: commit succeeds.

---

### Task 3: Align the Homepage

**Files:**
- Modify: `frontend/页面设计-策划书对齐/首页/code.html`
- Modify: `frontend/页面设计-策划书对齐/首页/DESIGN.md`
- Reference: `frontend/页面设计-策划书对齐/shared/safety-modal.html`

- [ ] **Step 1: Update homepage title and positioning copy**

In `frontend/页面设计-策划书对齐/首页/code.html`, keep the existing hero layout and replace the hero heading/copy with content equivalent to:

```html
<h2 class="text-headline-xl font-headline-xl text-on-surface leading-tight">
  舍友心晴：<br />
  <span class="text-primary relative inline-block">
    宿舍压力预警与沟通演练助手
  </span>
</h2>
<p class="text-body-lg font-body-lg text-on-surface-variant max-w-2xl mt-4">
  记录宿舍事件，识别压力来源，通过 AI 多角色沟通演练，在真实沟通前练习更温和、具体、可执行的表达方式。
</p>
```

Expected: visual structure remains the original hero section; only text changes.

- [ ] **Step 2: Replace unsafe AI analysis wording**

Replace the original homepage feature-card wording:

```text
利用先进模型拆解冲突核心，客观评估责任分配，提供不带偏见的矛盾解决视角。
```

with:

```text
识别宿舍事件中的压力来源，生成非诊断性的趋势提示和温和沟通建议。
```

Expected: no `责任分配` text remains in the new homepage.

- [ ] **Step 3: Add safety modal to static homepage state**

Insert the safety modal markup from `shared/safety-modal.html` before `</body>` in `frontend/页面设计-策划书对齐/首页/code.html`.

Expected: the static homepage shows the first-entry safety modal state.

- [ ] **Step 4: Add safety re-open entry**

Add a small button in the homepage navigation or hero action area:

```html
<button class="bg-surface text-on-surface border-2 border-on-surface rounded-full py-3 px-5 font-label-bold text-label-bold shadow-[4px_4px_0px_0px] shadow-on-surface">
  安全说明
</button>
```

Expected: users can see a future entry point to reopen the safety modal.

- [ ] **Step 5: Add homepage design note**

Append to `frontend/页面设计-策划书对齐/首页/DESIGN.md`:

```markdown
## 策划书对齐说明

本页沿用原首页的 Playful Geometric 视觉风格和主要布局，仅调整产品定位、安全边界和功能闭环文案。首次进入安全说明以弹窗形态呈现，不新增独立安全说明页面。
```

- [ ] **Step 6: Verify homepage alignment**

Run:

```bash
rg -n "舍友心晴|宿舍压力预警与沟通演练助手|不进行心理疾病诊断|安全说明" 'frontend/页面设计-策划书对齐/首页/code.html'
```

Expected: all four phrases are present.

Run:

```bash
rg -n "责任分配" 'frontend/页面设计-策划书对齐/首页/code.html'
```

Expected: no output.

- [ ] **Step 7: Commit homepage changes**

Run:

```bash
git add 'frontend/页面设计-策划书对齐/首页'
git commit -m "docs(frontend): 对齐首页设计与安全弹窗"
```

Expected: commit succeeds.

---

### Task 4: Align the Event Record Page

**Files:**
- Modify: `frontend/页面设计-策划书对齐/事件记录/code.html`
- Modify: `frontend/页面设计-策划书对齐/事件记录/DESIGN.md`

- [ ] **Step 1: Keep event type cards but ensure exact labels**

Verify the event type labels in `code.html` are:

```text
作息冲突
卫生冲突
噪音冲突
费用冲突
隐私边界
情绪冲突
```

If the copied design uses shortened labels like `作息` or `隐私`, update visible text only. Keep the existing card grid, icons, borders, colors, and hard shadows.

- [ ] **Step 2: Rename severity label**

Change visible label `影响程度` to:

```text
严重程度
```

Keep the existing 1-5 slider.

- [ ] **Step 3: Replace frequency options**

Replace the frequency radio choices with:

```html
<label class="cursor-pointer">
  <input checked class="peer sr-only" name="frequency" type="radio" value="occasional" />
  <div class="px-6 py-3 rounded-full bg-white card-border peer-checked:bg-accent peer-checked:text-white font-bold transition-colors shadow-[2px_2px_0px_0px_rgba(30,41,59,1)]">偶尔</div>
</label>
<label class="cursor-pointer">
  <input class="peer sr-only" name="frequency" type="radio" value="weekly_multiple" />
  <div class="px-6 py-3 rounded-full bg-white card-border peer-checked:bg-accent peer-checked:text-white font-bold transition-colors shadow-[2px_2px_0px_0px_rgba(30,41,59,1)]">每周多次</div>
</label>
<label class="cursor-pointer">
  <input class="peer sr-only" name="frequency" type="radio" value="daily" />
  <div class="px-6 py-3 rounded-full bg-white card-border peer-checked:bg-accent peer-checked:text-white font-bold transition-colors shadow-[2px_2px_0px_0px_rgba(30,41,59,1)]">几乎每天</div>
</label>
```

Expected: `首次` and `频繁` no longer appear as frequency options.

- [ ] **Step 4: Replace emotion options with plan-aligned labels**

Keep the existing horizontal emotion selector shape, but add visible text labels for:

```text
烦躁
焦虑
委屈
愤怒
无奈
压抑
```

Expected: all six emotion labels are visible.

- [ ] **Step 5: Add communication-state radio group**

Add a fieldset before the description field:

```html
<fieldset class="bg-surface-container-low p-6 rounded-xl card-border">
  <legend class="text-label-bold font-label-bold text-on-surface uppercase tracking-wider mb-4 flex items-center gap-2">
    是否已经沟通
  </legend>
  <div class="flex flex-wrap gap-4">
    <label class="cursor-pointer">
      <input class="peer sr-only" name="has_communicated" type="radio" value="yes" />
      <div class="px-6 py-3 rounded-full bg-white card-border peer-checked:bg-quaternary font-bold">是</div>
    </label>
    <label class="cursor-pointer">
      <input checked class="peer sr-only" name="has_communicated" type="radio" value="no" />
      <div class="px-6 py-3 rounded-full bg-white card-border peer-checked:bg-secondary peer-checked:text-white font-bold">否</div>
    </label>
  </div>
</fieldset>
```

- [ ] **Step 6: Add conflict-escalation radio group**

Add another fieldset before the description field:

```html
<fieldset class="bg-surface-container-low p-6 rounded-xl card-border">
  <legend class="text-label-bold font-label-bold text-on-surface uppercase tracking-wider mb-4 flex items-center gap-2">
    是否出现争吵或冷战
  </legend>
  <div class="flex flex-wrap gap-4">
    <label class="cursor-pointer">
      <input class="peer sr-only" name="has_conflict" type="radio" value="yes" />
      <div class="px-6 py-3 rounded-full bg-white card-border peer-checked:bg-error peer-checked:text-white font-bold">是</div>
    </label>
    <label class="cursor-pointer">
      <input checked class="peer sr-only" name="has_conflict" type="radio" value="no" />
      <div class="px-6 py-3 rounded-full bg-white card-border peer-checked:bg-quaternary font-bold">否</div>
    </label>
  </div>
</fieldset>
```

- [ ] **Step 7: Add event-record design note**

Append to `frontend/页面设计-策划书对齐/事件记录/DESIGN.md`:

```markdown
## 策划书对齐说明

本页保留原事件记录页的卡片化表单和趣味几何视觉，仅补齐策划书要求的沟通状态、争吵/冷战状态、频率枚举和负面情绪标签。
```

- [ ] **Step 8: Verify event record fields**

Run:

```bash
rg -n "作息冲突|卫生冲突|噪音冲突|费用冲突|隐私边界|情绪冲突|严重程度|偶尔|每周多次|几乎每天|烦躁|焦虑|委屈|愤怒|无奈|压抑|是否已经沟通|是否出现争吵或冷战" 'frontend/页面设计-策划书对齐/事件记录/code.html'
```

Expected: all phrases are present.

Run:

```bash
rg -n "首次|频繁" 'frontend/页面设计-策划书对齐/事件记录/code.html'
```

Expected: no output for frequency option text.

- [ ] **Step 9: Commit event record changes**

Run:

```bash
git add 'frontend/页面设计-策划书对齐/事件记录'
git commit -m "docs(frontend): 对齐事件记录页面字段"
```

Expected: commit succeeds.

---

### Task 5: Align the Pressure Analysis Page

**Files:**
- Modify: `frontend/页面设计-策划书对齐/压力分析/code.html`
- Modify: `frontend/页面设计-策划书对齐/压力分析/DESIGN.md`

- [ ] **Step 1: Update pressure value and risk label**

Ensure the main metric shows:

```text
76 / 100
状态：冲突风险较高
```

Replace `中度偏高` with `冲突风险较高`.

- [ ] **Step 2: Add plan-aligned result blocks**

Add or update visible result blocks to include:

```text
主要压力来源：作息冲突、噪音问题
情绪关键词：烦躁、压抑、无奈
冲突风险趋势提示：该问题发生频率较高，且尚未进行有效沟通。建议先通过 AI 沟通模拟练习表达方式，再选择舍友情绪较平稳的时间进行现实沟通。
系统建议：先表达自己的感受，再提出具体可执行请求。
是否推荐进入 AI 沟通模拟：推荐
```

Keep the original card grid and chart-like visual style.

- [ ] **Step 3: Add non-diagnostic note**

Add a small bordered note near the bottom of the analysis content:

```html
<p class="text-body-md font-body-md text-on-surface-variant bg-surface-container-low border-2 border-on-surface rounded-xl p-4">
  本结果仅用于压力趋势提示，不作为心理诊断依据。
</p>
```

- [ ] **Step 4: Keep simulation CTA**

Ensure the primary action still says:

```text
进入沟通演练
```

- [ ] **Step 5: Add pressure-analysis design note**

Append to `frontend/页面设计-策划书对齐/压力分析/DESIGN.md`:

```markdown
## 策划书对齐说明

本页保留原压力分析页的指标卡、来源条形图和建议卡布局，将风险等级、趋势提示、情绪关键词和非诊断提示对齐策划书。
```

- [ ] **Step 6: Verify pressure analysis content**

Run:

```bash
rg -n "76|冲突风险较高|作息冲突|噪音问题|烦躁|压抑|无奈|冲突风险趋势提示|推荐|不作为心理诊断依据|进入沟通演练" 'frontend/页面设计-策划书对齐/压力分析/code.html'
```

Expected: all phrases are present.

Run:

```bash
rg -n "中度偏高|责任分配" 'frontend/页面设计-策划书对齐/压力分析/code.html'
```

Expected: no output.

- [ ] **Step 7: Commit pressure analysis changes**

Run:

```bash
git add 'frontend/页面设计-策划书对齐/压力分析'
git commit -m "docs(frontend): 对齐压力分析页面结果"
```

Expected: commit succeeds.

---

### Task 6: Align the Communication Simulation Page

**Files:**
- Modify: `frontend/页面设计-策划书对齐/沟通模拟/code.html`
- Modify: `frontend/页面设计-策划书对齐/沟通模拟/DESIGN.md`

- [ ] **Step 1: Add scenario selector**

Near the top of the main content, add a card or segmented selector with these visible options:

```text
舍友晚上打游戏太吵
公共卫生长期无人打扫
舍友未经允许使用私人物品
水电费或公共费用分摊不均
作息差异导致互相影响
宿舍冷战或误会修复
```

Keep the existing page layout and Playful Geometric card style.

- [ ] **Step 2: Rename role cards to A/B/C model**

Update role card visible names to:

```text
舍友 A（直接型）
舍友 B（回避型）
舍友 C（调和型）
```

Keep the avatar/card visual treatment.

- [ ] **Step 3: Add user utterance sample**

Ensure the user input/sample message visibly contains:

```text
你晚上能不能小声点？
```

- [ ] **Step 4: Show three AI replies at once**

In the conversation area, show three response cards or message bubbles:

```text
舍友 A：我也没多大声吧，你是不是太敏感了？
舍友 B：这个事情之后再说吧。
舍友 C：要不我们一起定一个晚上安静时间？
```

Expected: all three roles respond to the same user utterance.

- [ ] **Step 5: Add system tip**

Add a highlighted tip:

```text
建议先表达感受，再提出具体请求。
```

- [ ] **Step 6: Add simulation design note**

Append to `frontend/页面设计-策划书对齐/沟通模拟/DESIGN.md`:

```markdown
## 策划书对齐说明

本页保留原沟通模拟页的角色卡片和聊天界面结构，补充场景选择，并将交互状态调整为三位 AI 舍友基于同一句用户话术分别回应。
```

- [ ] **Step 7: Verify simulation content**

Run:

```bash
rg -n "舍友晚上打游戏太吵|公共卫生长期无人打扫|舍友未经允许使用私人物品|水电费或公共费用分摊不均|作息差异导致互相影响|宿舍冷战或误会修复|舍友 A|舍友 B|舍友 C|你晚上能不能小声点|我也没多大声吧|这个事情之后再说吧|一起定一个晚上安静时间|建议先表达感受" 'frontend/页面设计-策划书对齐/沟通模拟/code.html'
```

Expected: all phrases are present.

- [ ] **Step 8: Commit simulation changes**

Run:

```bash
git add 'frontend/页面设计-策划书对齐/沟通模拟'
git commit -m "docs(frontend): 对齐沟通模拟页面角色回应"
```

Expected: commit succeeds.

---

### Task 7: Align the Communication Review Page

**Files:**
- Modify: `frontend/页面设计-策划书对齐/沟通复盘报告/code.html`
- Modify: `frontend/页面设计-策划书对齐/沟通复盘报告/DESIGN.md`

- [ ] **Step 1: Keep existing report layout and add required report sections**

Ensure visible sections cover:

```text
本次表达的优点
可能引发防御心理的表述
感受表达
具体请求
沟通空间
优化后的沟通话术
后续行动建议
安全提示
```

Keep the original score cards, sticker cards, and suggested scripting area where possible.

- [ ] **Step 2: Use plan-aligned optimized expression**

Ensure the optimized wording appears:

```text
我最近睡眠状态不太好，晚上声音比较容易影响我。我们能不能约定 12 点以后戴耳机？
```

- [ ] **Step 3: Add next action**

Add:

```text
建议选择双方情绪平稳的时间进行单独沟通。
```

- [ ] **Step 4: Add safety note**

Add:

```text
本建议仅用于沟通练习，不作为心理诊断依据。
```

- [ ] **Step 5: Add review design note**

Append to `frontend/页面设计-策划书对齐/沟通复盘报告/DESIGN.md`:

```markdown
## 策划书对齐说明

本页保留原复盘报告页的评分卡、闪光点与注意点、建议话术布局，补齐策划书要求的感受表达、具体请求、沟通空间、后续行动建议和安全提示。
```

- [ ] **Step 6: Verify review content**

Run:

```bash
rg -n "本次表达的优点|可能引发防御心理的表述|感受表达|具体请求|沟通空间|优化后的沟通话术|后续行动建议|安全提示|我最近睡眠状态不太好|建议选择双方情绪平稳的时间|不作为心理诊断依据" 'frontend/页面设计-策划书对齐/沟通复盘报告/code.html'
```

Expected: all phrases are present.

- [ ] **Step 7: Commit review changes**

Run:

```bash
git add 'frontend/页面设计-策划书对齐/沟通复盘报告'
git commit -m "docs(frontend): 对齐沟通复盘报告内容"
```

Expected: commit succeeds.

---

### Task 8: Final Verification

**Files:**
- Verify: `frontend/页面设计-策划书对齐/**`
- Verify unchanged: `frontend/页面设计/**`

- [ ] **Step 1: Verify original design directory was not modified**

Run:

```bash
git diff --name-only -- 'frontend/页面设计'
```

Expected: no output.

- [ ] **Step 2: Verify no screenshots exist in new design directory**

Run:

```bash
find 'frontend/页面设计-策划书对齐' -name 'screen.png' -print
```

Expected: no output.

- [ ] **Step 3: Verify all expected new design files exist**

Run:

```bash
find 'frontend/页面设计-策划书对齐' -maxdepth 2 -type f | sort
```

Expected output includes exactly the five page `DESIGN.md` files, five page `code.html` files, and two shared files.

- [ ] **Step 4: Verify forbidden boundary-breaking phrases are absent**

Run:

```bash
rg -n "责任分配|人格评价|人格判断|心理异常|某位舍友有问题" 'frontend/页面设计-策划书对齐'
```

Expected: no output.

- [ ] **Step 5: Verify safety boundary phrases are present**

Run:

```bash
rg -n "不进行心理疾病诊断|不作为心理诊断依据|不评价任何舍友|辅导员|心理老师|Demo 阶段不采集真实身份信息" 'frontend/页面设计-策划书对齐'
```

Expected: phrases appear in homepage/shared safety modal and relevant analysis/review pages.

- [ ] **Step 6: Verify current Git status**

Run:

```bash
git status --short --ignored
```

Expected: no unstaged tracked files. Ignored entries may include:

```text
!! .superpowers/
!! frontend/node_modules/
!! frontend/dist/
!! frontend/页面设计/
```

- [ ] **Step 7: Final commit if verification adjustments were needed**

If Task 8 produced any small verification-only fixes, commit them:

```bash
git add 'frontend/页面设计-策划书对齐'
git commit -m "docs(frontend): 完成页面设计对齐验收"
```

Expected: commit succeeds only if there were final fixes; otherwise there is nothing to commit.
