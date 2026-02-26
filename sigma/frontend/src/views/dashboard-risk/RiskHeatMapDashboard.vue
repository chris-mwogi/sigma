<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">🔥 Risk Heat Map Dashboard</h1>
        <p class="risk-dashboard__subtitle">Likelihood vs Impact Visualization • Risk Managers & Internal Audit</p>
      </div>
      <div class="risk-dashboard__actions">
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Heat Maps Row -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <RiskHeatMap 
          title="🔴 Inherent Risk Heat Map" 
          subtitle="Risk exposure before controls" 
          :matrix="data.heatmap?.inherent || defaultMatrix"
          :loading="loading"
        />
        <RiskHeatMap 
          title="🟢 Residual Risk Heat Map" 
          subtitle="Risk exposure after controls" 
          :matrix="data.heatmap?.residual || defaultMatrix"
          :loading="loading"
        />
      </div>
    </section>

    <!-- Risk Movement Analysis -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">📊 Risk Movement Analysis (Inherent → Residual)</h3>
        <p class="risk-dashboard__subtitle" style="margin-bottom: 16px">Shows the reduction in risk score from inherent to residual</p>
        <div class="movement-grid">
          <div v-for="risk in data.movements" :key="risk.risk_id" class="movement-card">
            <div class="movement-card__header">
              <span class="movement-card__title">{{ risk.risk_title }}</span>
            </div>
            <div class="movement-card__scores">
              <div class="movement-score movement-score--inherent">
                <span class="movement-score__label">Inherent</span>
                <span class="movement-score__value" :class="getRatingClass(risk.inherent_risk_rating)">{{ risk.inherent_risk_score }}</span>
                <span class="movement-score__rating">{{ risk.inherent_risk_rating }}</span>
              </div>
              <div class="movement-arrow">→</div>
              <div class="movement-score movement-score--residual">
                <span class="movement-score__label">Residual</span>
                <span class="movement-score__value" :class="getRatingClass(risk.residual_risk_rating)">{{ risk.residual_risk_score }}</span>
                <span class="movement-score__rating">{{ risk.residual_risk_rating }}</span>
              </div>
              <div class="movement-reduction" :class="risk.reduction > 0 ? 'positive' : 'neutral'">
                {{ risk.reduction > 0 ? '↓' : '–' }} {{ Math.abs(risk.reduction) }}
              </div>
            </div>
          </div>
        </div>
        <div v-if="!data.movements?.length && !loading" class="empty-state">
          <div class="empty-state__icon">📭</div>
          <div class="empty-state__text">No risk movement data available</div>
        </div>
      </div>
    </section>

    <!-- Risk Distribution Summary -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📈 Inherent Risk Distribution" type="bar" :labels="['Low', 'Medium', 'High', 'Critical', 'Extreme']" :datasets="inherentDistData" height="280px" :loading="loading" />
        <ChartCard title="📉 Residual Risk Distribution" type="bar" :labels="['Low', 'Medium', 'High', 'Critical', 'Extreme']" :datasets="residualDistData" height="280px" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, RiskHeatMap } from './components'
import './dashboard-risk.css'

export default {
  name: 'RiskHeatMapDashboard',
  components: { KPICard, ChartCard, RiskHeatMap },
  setup() {
    const loading = ref(true)
    const defaultMatrix = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    const data = ref({ heatmap: { inherent: defaultMatrix, residual: defaultMatrix }, movements: [] })

    const getRatingClass = (rating) => {
      const r = (rating || '').toLowerCase()
      if (r.includes('extreme')) return 'score--extreme'
      if (r.includes('critical')) return 'score--critical'
      if (r.includes('high')) return 'score--high'
      if (r.includes('medium')) return 'score--medium'
      return 'score--low'
    }

    const countByLevel = (matrix) => {
      const counts = { low: 0, medium: 0, high: 0, critical: 0, extreme: 0 }
      if (!matrix) return counts
      matrix.forEach((row, ri) => {
        row.forEach((val, ci) => {
          const likelihood = 5 - ri, impact = ci + 1, score = likelihood * impact
          if (score >= 20) counts.extreme += val
          else if (score >= 15) counts.critical += val
          else if (score >= 10) counts.high += val
          else if (score >= 5) counts.medium += val
          else counts.low += val
        })
      })
      return counts
    }

    const inherentDistData = computed(() => {
      const c = countByLevel(data.value.heatmap?.inherent)
      return [{ label: 'Risks', data: [c.low, c.medium, c.high, c.critical, c.extreme], backgroundColor: ['#66bb6a', '#fbc02d', '#ef6c00', '#c62828', '#7b1fa2'] }]
    })
    const residualDistData = computed(() => {
      const c = countByLevel(data.value.heatmap?.residual)
      return [{ label: 'Risks', data: [c.low, c.medium, c.high, c.critical, c.extreme], backgroundColor: ['#66bb6a', '#fbc02d', '#ef6c00', '#c62828', '#7b1fa2'] }]
    })

    const fetchData = async () => {
      loading.value = true
      try {
        const [heatmap, movements] = await Promise.all([
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_residual_risk_heatmap'),
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_risk_movement_data')
        ])
        if (heatmap.data.message) data.value.heatmap = heatmap.data.message
        if (movements.data.message) data.value.movements = movements.data.message
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, defaultMatrix, data, getRatingClass, inherentDistData, residualDistData, fetchData }
  }
}
</script>

<style scoped>
.movement-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.movement-card { background: var(--rd-bg); border-radius: 8px; padding: 16px; }
.movement-card__title { font-size: 13px; font-weight: 600; color: var(--rd-text); }
.movement-card__scores { display: flex; align-items: center; gap: 12px; margin-top: 12px; }
.movement-score { text-align: center; }
.movement-score__label { font-size: 10px; color: var(--rd-muted); display: block; }
.movement-score__value { font-size: 24px; font-weight: 700; display: block; }
.movement-score__rating { font-size: 10px; text-transform: uppercase; }
.movement-arrow { font-size: 20px; color: var(--rd-muted); }
.movement-reduction { padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
.movement-reduction.positive { background: rgba(67, 160, 71, 0.15); color: #43a047; }
.movement-reduction.neutral { background: rgba(158, 158, 158, 0.15); color: #757575; }
</style>

