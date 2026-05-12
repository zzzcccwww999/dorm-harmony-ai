<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

const navItems = [
  { name: 'home', label: 'Home', text: '首页', icon: 'dashboard' },
  { name: 'record', label: 'Record', text: '记录', icon: 'edit_note' },
  { name: 'analysis', label: 'Analysis', text: '分析', icon: 'analytics' },
]

const futureItems = [
  { label: 'AI Sandbox', text: '演练', icon: 'psychology' },
  { label: 'Performance', text: '表现', icon: 'assessment' },
  { label: 'Report', text: '复盘', icon: 'summarize' },
]
</script>

<template>
  <div class="app-layout dot-grid">
    <aside class="sidebar card-border pop-shadow" aria-label="桌面主导航">
      <RouterLink class="brand-lockup" :to="{ name: 'home' }" aria-label="回到舍友心晴首页">
        <span class="brand-mascot material-symbol" aria-hidden="true">晴</span>
        <span>
          <strong>舍友心晴</strong>
          <small>Harmony Hub</small>
        </span>
      </RouterLink>

      <nav class="sidebar-links">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          class="nav-pill"
          :to="{ name: item.name }"
        >
          <span class="material-symbol" aria-hidden="true">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </RouterLink>

        <button v-for="item in futureItems" :key="item.label" class="nav-pill nav-pill-muted" disabled>
          <span class="material-symbol" aria-hidden="true">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <RouterLink class="sidebar-cta" :to="{ name: 'record' }">
        <span class="material-symbol" aria-hidden="true">add</span>
        Log Incident
      </RouterLink>
    </aside>

    <div class="content-shell">
      <header class="mobile-header card-border" aria-label="移动端页头">
        <RouterLink class="mobile-title" :to="{ name: 'home' }">DormHarmony</RouterLink>
        <div class="mobile-actions" aria-label="移动端快捷入口">
          <button class="mobile-badge material-symbol" type="button" aria-label="通知">
            notifications
          </button>
          <button class="mobile-badge material-symbol" type="button" aria-label="设置">
            settings
          </button>
          <span class="mobile-avatar" aria-label="用户头像" role="img"></span>
        </div>
      </header>

      <span class="shape-confetti shape-confetti-pink" aria-hidden="true"></span>
      <span class="shape-confetti shape-confetti-yellow" aria-hidden="true"></span>
      <span class="shape-confetti shape-confetti-green" aria-hidden="true"></span>

      <RouterView />
    </div>

    <nav class="mobile-nav card-border" aria-label="移动端主导航">
      <RouterLink v-for="item in navItems" :key="item.name" :to="{ name: item.name }">
        <span class="material-symbol" aria-hidden="true">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </RouterLink>
      <button disabled>
        <span class="material-symbol" aria-hidden="true">forum</span>
        <span>AI Sandbox</span>
      </button>
      <button class="mobile-report" disabled>
        <span class="material-symbol" aria-hidden="true">assessment</span>
        <span>Performance</span>
      </button>
    </nav>
  </div>
</template>
