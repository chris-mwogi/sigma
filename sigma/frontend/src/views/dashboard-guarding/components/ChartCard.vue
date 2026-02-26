<template>
  <div class="chart-card">
    <div class="chart-card__header">
      <h3 class="chart-card__title">{{ title }}</h3>
      <div v-if="$slots.actions" class="chart-card__actions">
        <slot name="actions"></slot>
      </div>
    </div>
    <div class="chart-card__body" :style="{ height: height }">
      <div v-if="loading" class="chart-card__loading">
        <div class="spinner"></div>
        <span>Loading chart...</span>
      </div>
      <div v-else-if="!hasData" class="chart-card__empty">
        <span class="chart-card__empty-icon">📊</span>
        <span>No data available</span>
      </div>
      <canvas v-else ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'ChartCard',
  props: {
    title: { type: String, required: true },
    type: { type: String, default: 'bar' },
    labels: { type: Array, default: () => [] },
    datasets: { type: Array, default: () => [] },
    options: { type: Object, default: () => ({}) },
    height: { type: String, default: '300px' },
    loading: { type: Boolean, default: false }
  },
  setup(props) {
    const chartCanvas = ref(null)
    let chartInstance = null

    const hasData = computed(() => props.labels.length > 0 && props.datasets.length > 0)

    const defaultColors = [
      '#003366', '#00A651', '#F39200', '#dc3545', '#17a2b8',
      '#6f42c1', '#fd7e14', '#20c997', '#e83e8c', '#6c757d'
    ]

    const createChart = async () => {
      if (!chartCanvas.value || !hasData.value) return

      const { Chart, registerables } = await import('chart.js')
      Chart.register(...registerables)

      if (chartInstance) chartInstance.destroy()

      const datasets = props.datasets.map((ds, i) => ({
        ...ds,
        backgroundColor: ds.backgroundColor || (props.type === 'line' ? 'transparent' : defaultColors),
        borderColor: ds.borderColor || defaultColors[i % defaultColors.length],
        borderWidth: ds.borderWidth || 2,
        tension: ds.tension || 0.4
      }))

      const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: props.type === 'pie' || props.type === 'doughnut' ? 'right' : 'top' }
        },
        scales: props.type === 'pie' || props.type === 'doughnut' ? {} : {
          y: { beginAtZero: true }
        }
      }

      chartInstance = new Chart(chartCanvas.value, {
        type: props.type,
        data: { labels: props.labels, datasets },
        options: { ...defaultOptions, ...props.options }
      })
    }

    watch(() => [props.labels, props.datasets, props.type], createChart, { deep: true })
    onMounted(createChart)
    onUnmounted(() => { if (chartInstance) chartInstance.destroy() })

    return { chartCanvas, hasData }
  }
}
</script>

<style scoped>
.chart-card { background: var(--kp-surface, #fff); border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.chart-card__header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--kp-border, #e0e0e0); }
.chart-card__title { margin: 0; font-size: 16px; font-weight: 600; color: var(--kp-text, #1a1a1a); }
.chart-card__body { padding: 20px; position: relative; }
.chart-card__loading, .chart-card__empty { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; color: var(--kp-muted, #666); }
.chart-card__empty-icon { font-size: 32px; }
.spinner { width: 24px; height: 24px; border: 3px solid var(--kp-border); border-top-color: var(--kp-primary, #003366); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>

