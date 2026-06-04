<script setup lang="ts">
import SlidevPressureMeterCard from './SlidevPressureMeterCard.vue'
</script>

<template>
  <section class="cover-layout">
    <div class="cover-copy">
      <h1 class="cover-title">舍友心晴</h1>
      <h2 class="cover-subtitle">大学生宿舍压力预警与沟通演练助手</h2>

      <p class="cover-positioning">
        记录宿舍事件，识别压力来源，通过 AI 多角色沟通演练，<br />
        在真实沟通前练习更温和、具体、可执行的表达方式。
      </p>

      <div class="cover-flow" aria-label="核心闭环">
        <span>事件记录</span>
        <b>→</b>
        <span>压力分析</span>
        <b>→</b>
        <span>AI 演练</span>
        <b>→</b>
        <span>沟通复盘</span>
      </div>

      <div class="cover-tech">Vue 3 · FastAPI · SQLite · LangChain / DeepSeek</div>

      <div class="cover-team" aria-label="团队分工">
        <div class="team-name-badge">大眼仔小分队</div>
        <div><strong>组长：</strong>朱春雯（后端开发）</div>
        <div><strong>队员：</strong>曹乐（前端开发与汇报）</div>
      </div>
    </div>

    <div class="cover-visual" aria-label="产品化预览卡片">
      <div class="cover-meter-frame">
        <SlidevPressureMeterCard class="cover-pressure-card" />
      </div>

      <article class="cover-chat-card pop-card">
        <div class="cover-card-label">AI 多角色沟通演练</div>
        <div class="cover-chat-line">
          <span>我</span>
          <p>能不能商量一下晚上外放声音的问题？</p>
        </div>
        <div class="cover-chat-line ai">
          <span>AI</span>
          <p>我知道会影响你，我们可以定一个共同时间。</p>
        </div>
      </article>

      <div class="cover-mini-row">
        <div class="cover-float cover-float-training">
          <strong>场景训练</strong>
          <span>常见宿舍冲突练习入口</span>
        </div>
        <div class="cover-float cover-float-review">
          <strong>沟通复盘</strong>
          <span>生成下一步表达建议</span>
        </div>
      </div>
    </div>
  </section>
</template>
