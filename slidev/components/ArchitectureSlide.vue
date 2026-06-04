<script setup lang="ts">
const serviceModules = [
  {
    title: '压力评分',
    desc: '总分、趋势、主要来源',
  },
  {
    title: '事件档案分析',
    desc: '历史矛盾与单条分析',
  },
  {
    title: 'AI 服务编排',
    desc: '提示词、演练、复盘',
  },
]

const techTags = ['Vue 3 前端', 'FastAPI API', 'SQLite 存储', 'LangChain / DeepSeek AI']
</script>

<template>
  <section class="architecture-content">
    <h1>架构设计</h1>

    <h2>前端负责记录与演练体验，后端统一完成档案存储、压力分析和 AI 服务编排。</h2>

    <div class="architecture-board" aria-label="系统架构图">
      <div class="architecture-flow">
        <div class="architecture-stage architecture-stage-user">
          <article class="architecture-node architecture-user">
            <span class="architecture-layer">用户侧</span>
            <strong>用户 / 浏览器</strong>
            <p>记录事件、查看分析、进入演练</p>
          </article>
        </div>

        <div v-click class="architecture-stage">
          <article class="architecture-node architecture-frontend">
            <span class="architecture-layer">交互层</span>
            <strong>Vue 前端</strong>
            <p>页面、路由、组件与交互状态</p>
          </article>
        </div>

        <div v-click class="architecture-stage">
          <article class="architecture-node architecture-backend">
            <span class="architecture-layer">接口层</span>
            <strong>FastAPI 后端</strong>
            <p>接口契约、请求校验与业务入口</p>
          </article>
        </div>

        <div v-click class="architecture-stage architecture-stage-service">
          <section class="architecture-service-hub">
            <span class="architecture-layer">业务层</span>
            <strong>业务服务层</strong>
            <div class="architecture-service-grid">
              <article v-for="module in serviceModules" :key="module.title">
                <b>{{ module.title }}</b>
                <span>{{ module.desc }}</span>
              </article>
            </div>
          </section>
        </div>

        <div v-click class="architecture-stage">
          <section class="architecture-store-stack">
            <article class="architecture-node architecture-db">
              <span class="architecture-layer">存储层</span>
              <strong>SQLite</strong>
              <p>事件档案 / 会话记忆 / 复盘历史</p>
            </article>
            <article class="architecture-node architecture-ai">
              <span class="architecture-layer">模型调用</span>
              <strong>外部 AI 服务</strong>
              <p>LangChain / DeepSeek<br />生成见解、对话与复盘建议</p>
            </article>
          </section>
        </div>
      </div>
    </div>

    <div v-click class="architecture-tech-tags" aria-label="技术栈">
      <span v-for="tag in techTags" :key="tag">{{ tag }}</span>
    </div>
  </section>
</template>
