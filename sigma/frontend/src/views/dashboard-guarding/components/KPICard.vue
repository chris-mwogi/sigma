<template>
  <div :class="['kpi-card', `kpi-card--${variant}`, { 'kpi-card--clickable': clickable }]" @click="handleClick">
    <div class="kpi-card__icon">
      <span>{{ icon }}</span>
    </div>
    <div class="kpi-card__content">
      <div class="kpi-card__value">
        <span v-if="loading" class="kpi-card__loading">...</span>
        <span v-else>{{ formattedValue }}</span>
        <span v-if="unit && !loading" class="kpi-card__unit">{{ unit }}</span>
      </div>
      <div class="kpi-card__label">{{ label }}</div>
      <div v-if="trend !== null" :class="['kpi-card__trend', trendClass]">
        <span class="kpi-card__trend-icon">{{ trendIcon }}</span>
        <span>{{ Math.abs(trend) }}%</span>
      </div>
    </div>
    <div v-if="subtitle" class="kpi-card__subtitle">{{ subtitle }}</div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'KPICard',
  props: {
    value: { type: [Number, String], default: 0 },
    label: { type: String, required: true },
    icon: { type: String, default: '📊' },
    unit: { type: String, default: '' },
    variant: { type: String, default: 'default' },
    trend: { type: Number, default: null },
    subtitle: { type: String, default: '' },
    loading: { type: Boolean, default: false },
    clickable: { type: Boolean, default: false },
    format: { type: String, default: 'number' }
  },
  emits: ['click'],
  setup(props, { emit }) {
    const formattedValue = computed(() => {
      if (props.loading) return '...'
      const val = Number(props.value) || 0
      switch (props.format) {
        case 'percent': return `${val.toFixed(1)}%`
        case 'currency': return val.toLocaleString('en-KE', { style: 'currency', currency: 'KES' })
        default: return val.toLocaleString()
      }
    })

    const trendClass = computed(() => {
      if (props.trend === null) return ''
      return props.trend >= 0 ? 'kpi-card__trend--up' : 'kpi-card__trend--down'
    })

    const trendIcon = computed(() => props.trend >= 0 ? '↑' : '↓')
    const handleClick = () => { if (props.clickable) emit('click') }

    return { formattedValue, trendClass, trendIcon, handleClick }
  }
}
</script>

<style scoped>
.kpi-card {
  background: var(--kp-surface, #fff);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border-left: 4px solid var(--kp-border, #e0e0e0);
  transition: all 0.3s ease;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
.kpi-card--clickable { cursor: pointer; }
.kpi-card--primary { border-left-color: #003366; }
.kpi-card--success { border-left-color: #28a745; }
.kpi-card--warning { border-left-color: #ffc107; }
.kpi-card--danger { border-left-color: #dc3545; }
.kpi-card--info { border-left-color: #17a2b8; }

.kpi-card__icon { font-size: 28px; }
.kpi-card__content { display: flex; flex-direction: column; gap: 4px; }
.kpi-card__value { font-size: 28px; font-weight: 700; color: var(--kp-text, #1a1a1a); display: flex; align-items: baseline; gap: 4px; }
.kpi-card__unit { font-size: 14px; color: var(--kp-muted, #666); }
.kpi-card__label { font-size: 13px; color: var(--kp-muted, #666); font-weight: 500; }
.kpi-card__subtitle { font-size: 11px; color: var(--kp-muted, #999); }
.kpi-card__trend { display: flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 600; }
.kpi-card__trend--up { color: #28a745; }
.kpi-card__trend--down { color: #dc3545; }
.kpi-card__loading { animation: pulse 1.5s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>

