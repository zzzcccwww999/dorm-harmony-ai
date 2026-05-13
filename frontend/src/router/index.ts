import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/record',
      name: 'record',
      component: () => import('@/views/RecordView.vue'),
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: () => import('@/views/AnalysisView.vue'),
    },
    {
      path: '/simulate',
      name: 'simulate',
      component: () => import('@/views/SimulationView.vue'),
    },
    {
      path: '/review',
      name: 'review',
      component: () => import('@/views/ReviewView.vue'),
    },
  ],
})

export default router
