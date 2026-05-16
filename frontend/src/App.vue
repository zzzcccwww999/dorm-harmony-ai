<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

const navItems = [
  { name: 'home', label: '首页', icon: 'dashboard', mobileIcon: 'dashboard' },
  { name: 'record', label: '事件记录', icon: 'edit_note', mobileIcon: 'edit_note' },
  { name: 'archive', label: '事件档案', icon: 'history', mobileIcon: 'history' },
  { name: 'analysis', label: '压力分析', icon: 'analytics', mobileIcon: 'analytics' },
  { name: 'simulate', label: '沟通模拟', icon: 'forum', mobileIcon: 'forum' },
  { name: 'review', label: '沟通复盘', icon: 'assignment', mobileIcon: 'assignment' },
]

const brandAvatarSrc =
  'https://lh3.googleusercontent.com/aida-public/AB6AXuDoIeE3fuGST0i8AH2TVFnjVGh_ghmeHMgRw6uUv0F6XHs-tGfTxBIOxOxQ9caVd2NzLnFXtlExYdqzmzWd5bDU1m65ZFQH1vroL-ebUGb6tEbeJ4yl3p6alHBVf0b4XtMOtvzRdRPCQAlFENmTXT0sOQQ_bDMWNAO2d13Qkg81Bnv4wY6WsSXjTKLxhv5act4Ak_2Q0Sj7xQ1lkpf4Bu7GCRJrqmQ1UAJr6F_hmuC0ZPir2-Z1lCASlOr_EmvP01FgTRlACAuJzXo'
</script>

<template>
  <div class="app-layout dot-grid">
    <aside class="sidebar card-border pop-shadow" aria-label="桌面主导航">
      <RouterLink class="brand-lockup" :to="{ name: 'home' }" aria-label="回到舍友心晴首页">
        <img :src="brandAvatarSrc" class="brand-mascot" alt="" aria-hidden="true" />
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
      </nav>

      <RouterLink class="sidebar-cta" :to="{ name: 'record' }">
        <span class="material-symbol" aria-hidden="true">add</span>
        记录事件
      </RouterLink>
    </aside>

    <div class="content-shell">
      <header class="mobile-header card-border" aria-label="移动端页头">
        <RouterLink class="mobile-title" :to="{ name: 'home' }">舍友心晴</RouterLink>
        <div class="mobile-actions" aria-label="移动端快捷入口">
          <button class="mobile-badge material-symbol" type="button" aria-label="通知">
            notifications
          </button>
          <button class="mobile-badge material-symbol" type="button" aria-label="设置">
            settings
          </button>
          <img class="mobile-avatar" :src="brandAvatarSrc" alt="" aria-hidden="true" />
        </div>
      </header>

      <RouterView />
    </div>

    <nav class="mobile-nav card-border" aria-label="移动端主导航">
      <RouterLink v-for="item in navItems" :key="item.name" :to="{ name: item.name }">
        <span class="material-symbol" aria-hidden="true">{{ item.mobileIcon }}</span>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>
  </div>
</template>
