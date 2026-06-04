<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client/context.ts'

const loopNodes = [
  {
    title: '事件记录',
    desc: '把“不舒服”转成结构化事件',
  },
  {
    title: '事件档案',
    desc: '沉淀历史矛盾与单条分析',
  },
  {
    title: '压力分析',
    desc: '识别总压力、趋势和主要来源',
  },
  {
    title: 'AI 心晴见解',
    desc: '生成沟通重点与照顾建议',
  },
  {
    title: '多角色演练',
    desc: '在低风险环境中练习表达',
  },
  {
    title: '沟通复盘',
    desc: '输出评分、改写建议和行动计划',
  },
]

const { $clicks } = useSlideContext()
const loopStep = computed(() => Math.min(Math.max($clicks.value, 0), loopNodes.length))
const trackProgress = computed(() => `${(loopStep.value / loopNodes.length) * 100}%`)
const showLoopNext = computed(() => $clicks.value >= loopNodes.length + 1)

function isLoopOpen(index: number) {
  return loopStep.value >= index + 1
}
</script>

<template>
  <section class="product-loop-content">
    <h1>从一次宿舍事件，到一次可复盘的沟通训练</h1>

    <h2>舍友心晴不是单点建议工具，而是围绕事件档案形成连续闭环。</h2>

    <div class="product-loop-orbit" aria-label="产品闭环轨道">
      <div class="product-loop-core">记录 · 分析 · 演练 · 复盘</div>
      <div class="product-loop-line" :style="{ '--product-loop-progress': trackProgress }" aria-hidden="true"></div>

      <div class="product-loop-track">
        <article
          v-for="(node, index) in loopNodes"
          :key="node.title"
          :class="['product-loop-node', { 'is-open': isLoopOpen(index) }]"
        >
          <span class="num">{{ String(index + 1).padStart(2, '0') }}</span>
          <h3>{{ node.title }}</h3>
          <div class="product-loop-desc-wrap">
            <p>{{ node.desc }}</p>
          </div>
        </article>
      </div>

    </div>

    <div :class="['product-loop-next', { 'is-visible': showLoopNext }]">
      接下来通过 50 秒视频展示完整使用流程
    </div>
  </section>
</template>
