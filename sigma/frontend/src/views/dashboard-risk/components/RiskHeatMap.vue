<template>
  <div class="risk-heatmap">
    <div class="risk-heatmap__header">
      <h3 class="risk-heatmap__title">{{ title }}</h3>
      <span v-if="subtitle" class="risk-heatmap__subtitle">{{ subtitle }}</span>
    </div>
    <div class="risk-heatmap__container">
      <div class="risk-heatmap__y-axis">
        <span v-for="(label, i) in yLabels" :key="'y'+i" class="risk-heatmap__y-label">{{ label }}</span>
      </div>
      <div class="risk-heatmap__grid">
        <div v-for="(row, ri) in matrix" :key="'row'+ri" class="risk-heatmap__row">
          <div 
            v-for="(cell, ci) in row" 
            :key="'cell'+ri+ci"
            :class="['risk-heatmap__cell', getCellClass(ri, ci)]"
            :title="getCellTooltip(ri, ci, cell)"
          >
            {{ cell || '' }}
          </div>
        </div>
        <div class="risk-heatmap__x-axis">
          <span v-for="(label, i) in xLabels" :key="'x'+i" class="risk-heatmap__x-label">{{ label }}</span>
        </div>
      </div>
    </div>
    <div class="risk-heatmap__legend">
      <div class="risk-heatmap__legend-item"><span class="legend-box legend-box--low"></span> Low</div>
      <div class="risk-heatmap__legend-item"><span class="legend-box legend-box--medium"></span> Medium</div>
      <div class="risk-heatmap__legend-item"><span class="legend-box legend-box--high"></span> High</div>
      <div class="risk-heatmap__legend-item"><span class="legend-box legend-box--critical"></span> Critical</div>
      <div class="risk-heatmap__legend-item"><span class="legend-box legend-box--extreme"></span> Extreme</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RiskHeatMap',
  props: {
    title: { type: String, default: 'Risk Heat Map' },
    subtitle: { type: String, default: '' },
    matrix: { type: Array, default: () => [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]] },
    xLabels: { type: Array, default: () => ['1-Insignificant', '2-Minor', '3-Moderate', '4-Major', '5-Catastrophic'] },
    yLabels: { type: Array, default: () => ['5-Almost Certain', '4-Likely', '3-Possible', '2-Unlikely', '1-Rare'] }
  },
  methods: {
    getCellClass(row, col) {
      // Calculate risk level based on position (likelihood × impact)
      const likelihood = 5 - row // Invert because row 0 = highest likelihood
      const impact = col + 1
      const score = likelihood * impact
      
      if (score >= 20) return 'risk-heatmap__cell--extreme'
      if (score >= 15) return 'risk-heatmap__cell--critical'
      if (score >= 10) return 'risk-heatmap__cell--high'
      if (score >= 5) return 'risk-heatmap__cell--medium'
      return 'risk-heatmap__cell--low'
    },
    getCellTooltip(row, col, count) {
      const likelihood = 5 - row
      const impact = col + 1
      return `Likelihood: ${likelihood}, Impact: ${impact}, Risks: ${count || 0}`
    }
  }
}
</script>

<style scoped>
.risk-heatmap { background: var(--rd-surface, #fff); border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.risk-heatmap__header { margin-bottom: 16px; }
.risk-heatmap__title { font-size: 16px; font-weight: 600; margin: 0; color: var(--rd-text, #333); }
.risk-heatmap__subtitle { font-size: 12px; color: var(--rd-muted, #666); }
.risk-heatmap__container { display: flex; gap: 8px; }
.risk-heatmap__y-axis { display: flex; flex-direction: column; justify-content: space-around; padding-right: 8px; }
.risk-heatmap__y-label { font-size: 10px; color: var(--rd-muted, #666); text-align: right; height: 48px; display: flex; align-items: center; justify-content: flex-end; }
.risk-heatmap__grid { flex: 1; }
.risk-heatmap__row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
.risk-heatmap__cell { aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; color: #fff; border-radius: 4px; min-height: 48px; cursor: default; transition: transform 0.2s; }
.risk-heatmap__cell:hover { transform: scale(1.05); z-index: 1; }
.risk-heatmap__cell--low { background: #66bb6a; }
.risk-heatmap__cell--medium { background: #fbc02d; color: #333; }
.risk-heatmap__cell--high { background: #ef6c00; }
.risk-heatmap__cell--critical { background: #e53935; }
.risk-heatmap__cell--extreme { background: #7b1fa2; }
.risk-heatmap__x-axis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; margin-top: 8px; }
.risk-heatmap__x-label { font-size: 10px; color: var(--rd-muted, #666); text-align: center; }
.risk-heatmap__legend { display: flex; justify-content: center; gap: 16px; margin-top: 16px; flex-wrap: wrap; }
.risk-heatmap__legend-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--rd-muted, #666); }
.legend-box { width: 16px; height: 16px; border-radius: 3px; }
.legend-box--low { background: #66bb6a; }
.legend-box--medium { background: #fbc02d; }
.legend-box--high { background: #ef6c00; }
.legend-box--critical { background: #e53935; }
.legend-box--extreme { background: #7b1fa2; }
</style>

