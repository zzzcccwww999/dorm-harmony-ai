<script setup lang="ts">
import EmotionDistributionCard from '../../frontend/src/components/analysis/EmotionDistributionCard.vue'
import TrainingRecommendationCard from '../../frontend/src/components/analysis/TrainingRecommendationCard.vue'

const emotions = [
  { emotion: 'anxious', label: '焦虑', count: 4, percent: 44, tone: 'danger' },
  { emotion: 'frustrated', label: '委屈', count: 3, percent: 33, tone: 'warning' },
  { emotion: 'calm', label: '平稳', count: 2, percent: 22, tone: 'fresh' },
]

const recommendation = {
  scenario_id: 'noise-boundary',
  scenario_title: '作息噪音边界沟通',
  category_label: '生活习惯',
  target_label: '表达边界',
  difficulty_label: '进阶',
  difficulty_description: '存在情绪压力，需要先组织表达顺序。',
  reason: '近期压力来源集中在作息干扰，适合先做低风险表达演练。',
  opening_suggestion: '我想和你聊一下晚上的声音问题，不是指责，只是希望我们能一起调一个都舒服的方式。',
  safety_note: '训练建议仅用于沟通准备，现实冲突升级时应优先寻求线下支持。',
}
</script>

<template>
  <div class="analysis-component-preview">
    <EmotionDistributionCard :emotions="emotions" range-label="近 30 天" />
    <TrainingRecommendationCard :recommendation="recommendation" />
  </div>
</template>

<style scoped>
.analysis-component-preview {
  display: grid;
  grid-template-columns: 0.82fr 1fr;
  gap: 14px;
  align-items: stretch;
  min-width: 0;
}

:deep(.analysis-emotion-panel),
:deep(.analysis-training-panel) {
  min-height: 0;
  padding: 16px;
}

:deep(.analysis-training-panel) {
  gap: 10px;
}

:deep(.analysis-training-panel h2),
:deep(.analysis-emotion-panel h2) {
  font-size: 1.15rem;
}

:deep(.analysis-training-panel h2 .material-symbol) {
  width: 34px;
  height: 34px;
  font-size: 1rem;
}

:deep(.analysis-training-meta),
:deep(.analysis-training-safety),
:deep(.analysis-training-panel button) {
  display: none;
}

:deep(.analysis-training-heading h3) {
  font-size: 1rem;
  line-height: 1.25;
}

:deep(.analysis-training-panel p),
:deep(.analysis-training-panel blockquote) {
  font-size: 0.72rem;
  line-height: 1.45;
}
</style>
