<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type WeatherKey = 'sunny' | 'cloudy' | 'rainy'

interface WeatherProfile {
  key: WeatherKey
  min: number
  max: number
}

const weatherProfiles: WeatherProfile[] = [
  { key: 'sunny', min: 8, max: 30 },
  { key: 'cloudy', min: 31, max: 60 },
  { key: 'rainy', min: 61, max: 92 },
]

const animatedMeterPercent = ref(76)
let animationFrameId = 0
let weatherIntervalId = 0
let activeWeatherKey: WeatherKey = 'rainy'

const homeMeterWeatherIcon = computed(() => {
  const score = animatedMeterPercent.value

  if (score <= 30) {
    return {
      key: 'sunny',
      icon: 'wb_sunny',
      label: '晴天',
      tone: 'sunny',
    }
  }

  if (score <= 60) {
    return {
      key: 'cloudy',
      icon: 'cloud',
      label: '阴天',
      tone: 'cloudy',
    }
  }

  return {
    key: 'rainy',
    icon: 'rainy',
    label: '雨天',
    tone: 'rainy',
  }
})

const riskLabel = computed(() => {
  const score = animatedMeterPercent.value

  if (score <= 30) {
    return '关系平稳'
  }

  if (score <= 60) {
    return '存在压力'
  }

  if (score <= 80) {
    return '冲突风险较高'
  }

  return '高压力状态'
})

const trendMessage = computed(() => {
  const score = animatedMeterPercent.value

  if (score <= 30) {
    return '当前关系状态较平稳，可以继续保留已经有效的沟通方式。'
  }

  if (score <= 60) {
    return '近期事件有一定摩擦，建议在情绪平稳时提前沟通。'
  }

  return '近期压力来源集中在作息和边界问题，建议先进行沟通演练。'
})

const meterStatusLabel = computed(() => {
  const score = animatedMeterPercent.value

  if (score <= 30) {
    return '和谐融洽'
  }

  if (score <= 60) {
    return '需要关注'
  }

  return '需干预'
})

const meterFillStyle = computed<Record<string, string>>(() => ({
  '--home-meter-percent': `${animatedMeterPercent.value}%`,
}))

function randomInteger(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function pickNextWeather() {
  const candidates = weatherProfiles.filter((profile) => profile.key !== activeWeatherKey)
  const profile = candidates[randomInteger(0, candidates.length - 1)] ?? weatherProfiles[0]!
  activeWeatherKey = profile.key
  return randomInteger(profile.min, profile.max)
}

function easeOutCubic(progress: number) {
  return 1 - Math.pow(1 - progress, 3)
}

function animateMeterTo(target: number) {
  window.cancelAnimationFrame(animationFrameId)

  const start = animatedMeterPercent.value
  const distance = target - start
  const startedAt = window.performance.now()
  const duration = 2200

  function tick(now: number) {
    const progress = Math.min((now - startedAt) / duration, 1)
    animatedMeterPercent.value = Math.round(start + distance * easeOutCubic(progress))

    if (progress < 1) {
      animationFrameId = window.requestAnimationFrame(tick)
    }
  }

  animationFrameId = window.requestAnimationFrame(tick)
}

function randomizeWeather() {
  animateMeterTo(pickNextWeather())
}

onMounted(() => {
  weatherIntervalId = window.setInterval(randomizeWeather, 6000)
})

onBeforeUnmount(() => {
  window.cancelAnimationFrame(animationFrameId)
  window.clearInterval(weatherIntervalId)
})
</script>

<template>
  <section class="dashboard-card pop-card pop-shadow" aria-label="压力晴雨表示例">
    <div class="dashboard-main">
      <span
        :class="['floating-icon', `floating-icon-${homeMeterWeatherIcon.tone}`]"
        :aria-label="`当前压力天气：${homeMeterWeatherIcon.label}`"
        role="img"
      >
        <Transition name="weather-icon-flip" mode="out-in">
          <span :key="homeMeterWeatherIcon.key" class="material-symbol">
            {{ homeMeterWeatherIcon.icon }}
          </span>
        </Transition>
      </span>
      <div class="meter-header">
        <span>宿舍压力晴雨表</span>
        <strong>{{ riskLabel }}</strong>
      </div>
      <div class="meter-score">
        <span>当前环境氛围评估</span>
        <strong>Index: {{ animatedMeterPercent }}/100</strong>
      </div>
      <div class="meter-track">
        <span class="meter-fill" :style="meterFillStyle"></span>
      </div>
      <div class="meter-labels">
        <Transition name="weather-icon-flip" mode="out-in">
          <span :key="meterStatusLabel">{{ meterStatusLabel }}</span>
        </Transition>
      </div>
    </div>
    <aside class="recent-note card-border">
      <strong>档案汇总</strong>
      <p>{{ trendMessage }}</p>
      <p>共 4 条事件，近 30 天 3 条。</p>
      <a href="/analysis" @click.prevent>查看分析 →</a>
    </aside>
  </section>
</template>

<style scoped>
.dashboard-card {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 0.36fr);
  gap: 24px;
  align-items: center;
  min-height: 296px;
  margin-top: 0;
  overflow: hidden;
  border: 2px solid var(--ink);
  border-radius: 16px;
  background: var(--card);
  box-shadow: 4px 4px 0 0 var(--shadow-dark);
  padding: 28px 30px;
}

.dashboard-card::before {
  position: absolute;
  top: -54px;
  right: -42px;
  width: 170px;
  height: 170px;
  border-radius: 999px;
  background: var(--surface-container);
  content: '';
  opacity: 0.72;
}

.dashboard-main,
.dashboard-card .recent-note {
  position: relative;
  z-index: 1;
}

.floating-icon {
  position: absolute;
  top: -24px;
  left: 50%;
  display: grid;
  width: 52px;
  height: 52px;
  place-items: center;
  border: 2px solid var(--ink);
  border-radius: 999px;
  background: var(--secondary);
  box-shadow: 2px 2px 0 0 var(--shadow-dark);
  color: #ffffff;
  perspective: 240px;
  transform: translateX(-50%);
  transition: background-color 220ms ease;
}

.floating-icon .material-symbol {
  display: grid;
  place-items: center;
  font-size: 1.55rem;
  line-height: 1;
}

.floating-icon-sunny {
  background: var(--secondary);
}

.floating-icon-cloudy {
  background: var(--tertiary);
  color: var(--ink);
}

.floating-icon-rainy {
  background: var(--primary);
}

.weather-icon-flip-enter-active,
.weather-icon-flip-leave-active {
  transition:
    opacity 180ms ease,
    transform 260ms cubic-bezier(0.2, 0, 0, 1);
  transform-style: preserve-3d;
}

.weather-icon-flip-enter-from {
  opacity: 0;
  transform: rotateY(-90deg) scale(0.82);
}

.weather-icon-flip-enter-to,
.weather-icon-flip-leave-from {
  opacity: 1;
  transform: rotateY(0deg) scale(1);
}

.weather-icon-flip-leave-to {
  opacity: 0;
  transform: rotateY(90deg) scale(0.82);
}

.meter-header {
  display: grid;
  gap: 4px;
  margin-top: 12px;
}

.meter-header span {
  color: var(--ink-soft);
  font-size: var(--font-body-lg);
  font-weight: 700;
}

.meter-header strong {
  color: var(--ink);
  font-family: Outfit, 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  font-size: 42px;
  font-weight: 900;
  line-height: 1.1;
}

.meter-score {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 16px 0 12px;
}

.meter-score span,
.meter-labels {
  color: var(--ink-soft);
  font-size: var(--font-chart-label);
  font-weight: 700;
}

.meter-score strong {
  border: 2px solid var(--ink);
  border-radius: 999px;
  background: var(--surface-variant);
  color: var(--ink);
  padding: 6px 12px;
  font-size: var(--font-label-bold);
  font-weight: 900;
}

.meter-track {
  position: relative;
  overflow: hidden;
  height: 24px;
  border: 2px solid var(--ink);
  border-radius: 999px;
  background: var(--surface-variant);
}

.meter-fill {
  display: block;
  width: var(--home-meter-percent, 0%);
  height: 100%;
  border-right: 2px solid var(--ink);
  background: var(--tertiary);
}

.meter-labels {
  display: flex;
  justify-content: flex-start;
  margin-top: 8px;
}

.recent-note {
  margin-top: 18px;
  border: 2px solid var(--ink);
  border-radius: 16px;
  background: var(--surface-low);
  box-shadow: 2px 2px 0 0 var(--shadow-dark);
  padding: 14px;
}

.recent-note strong,
.recent-note a {
  font-weight: 700;
}

.recent-note p {
  margin: 6px 0 8px;
  color: var(--ink-soft);
  line-height: 1.45;
}

.recent-note a {
  color: var(--primary);
  transition:
    color 160ms ease,
    text-decoration-color 160ms ease,
    transform 160ms ease;
}
</style>
