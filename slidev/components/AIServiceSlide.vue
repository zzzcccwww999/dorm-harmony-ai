<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client/context.ts'

const flowNodes = [
  {
    title: '用户表达',
    desc: '场景 + 舍友画像 + 上下文',
    tone: 'input',
  },
  {
    title: '读取会话记忆',
    desc: '短期对话状态',
    tone: 'memory',
  },
  {
    title: 'Speaker Planner',
    desc: '规划谁发言、按什么顺序',
    tone: 'planner',
  },
  {
    title: '发言计划',
    desc: 'A → C → A → B',
    tone: 'plan',
  },
  {
    title: 'Per-roommate Generator',
    desc: '逐个生成舍友回复',
    tone: 'generator',
  },
  {
    title: '结构化校验',
    desc: '角色合法 / JSON 合法 / 次数限制',
    tone: 'validation',
  },
  {
    title: '写入会话记忆',
    desc: 'LangGraph / SQLite',
    tone: 'memory',
  },
  {
    title: '前端逐条展示',
    desc: '进入沟通复盘',
    tone: 'frontend',
  },
]

const explainCards = [
  {
    title: 'Speaker Planner',
    label: '先判断谁该说话',
    desc: '根据用户表达、历史对话、舍友画像和事件档案摘要，动态规划本轮发言顺序。',
    tone: 'planner',
  },
  {
    title: 'Per-roommate Generator',
    label: '再逐个生成回复',
    desc: '每次只生成一个舍友的一条回复，后发言的舍友可以参考前面舍友刚说过的话。',
    tone: 'generator',
  },
  {
    title: 'Memory & Validation',
    label: '最后写入记忆',
    desc: '校验角色 ID、发言次数和输出结构，再写入 LangGraph / SQLite 会话记忆。',
    tone: 'memory',
  },
]

const { $clicks } = useSlideContext()
const flowStep = computed(() => Math.min(Math.max($clicks.value, 0), flowNodes.length))

function getFlowState(index: number) {
  const order = index + 1

  if (flowStep.value === order) {
    return 'is-current'
  }

  if (flowStep.value > order) {
    return 'is-done'
  }

  return 'is-muted'
}
</script>

<template>
  <section class="ai-service-content">
    <h1>AI 服务层设计：规划器驱动的多角色沟通模拟</h1>

    <h2>不是一次性生成整段聊天，而是先规划发言顺序，再逐个生成舍友回复。</h2>

    <div class="ai-service-layout">
      <section class="ai-flow-board" aria-label="AI 多角色编排流程">
        <div class="ai-flow-grid">
          <article
            v-for="(node, index) in flowNodes"
            :key="node.title"
            :class="[
              'ai-flow-node',
              `ai-flow-node-${index + 1}`,
              `tone-${node.tone}`,
              getFlowState(index),
            ]"
          >
            <span class="num">{{ String(index + 1).padStart(2, '0') }}</span>
            <strong>{{ node.title }}</strong>
            <p>{{ node.desc }}</p>
          </article>
        </div>

        <span
          v-for="step in flowNodes.length"
          :key="`ai-flow-click-${step}`"
          v-click
          class="ai-flow-click-marker"
          aria-hidden="true"
        />
      </section>

      <aside class="ai-explain-stack" aria-label="AI 服务层说明">
        <article
          v-for="card in explainCards"
          :key="card.title"
          v-click
          :class="['ai-explain-card', `tone-${card.tone}`]"
        >
          <span>{{ card.label }}</span>
          <strong>{{ card.title }}</strong>
          <p>{{ card.desc }}</p>
        </article>
      </aside>
    </div>

    <div v-click class="ai-safety-note">
      安全边界：只用于宿舍沟通演练，不代表真实舍友想法，不进行心理诊断或人格评价。
    </div>
  </section>
</template>
