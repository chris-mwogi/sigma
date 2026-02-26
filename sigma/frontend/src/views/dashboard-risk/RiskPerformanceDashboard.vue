<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">📊 Risk Performance & Maturity Dashboard</h1>
        <p class="risk-dashboard__subtitle">Measure Effectiveness of Risk Management Framework • CRO, Governance Committees</p>
      </div>
      <div class="risk-dashboard__actions">
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Performance KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="📈" :value="data.closure_rate + '%'" label="Risk Closure Rate" variant="success" :loading="loading" />
        <KPICard icon="📉" :value="data.avg_reduction_percentage + '%'" label="Avg Risk Reduction" variant="info" :loading="loading" />
        <KPICard icon="✅" :value="data.review_compliance_rate + '%'" label="Review Compliance" variant="primary" :loading="loading" />
        <KPICard icon="🎯" :value="data.treatment_completed" label="Treatments Completed" variant="success" :loading="loading" />
        <KPICard icon="⏱️" :value="data.treatment_on_time" label="On-Time Completions" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Performance Meters -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--3">
        <div class="data-card">
          <h3 class="data-card__title">📈 Risk Closure Rate</h3>
          <div class="perf-meter">
            <svg viewBox="0 0 100 50" class="perf-meter__gauge">
              <path d="M5,50 A45,45 0 0,1 95,50" fill="none" stroke="#e0e0e0" stroke-width="10" stroke-linecap="round"/>
              <path d="M5,50 A45,45 0 0,1 95,50" fill="none" :stroke="getGaugeColor(data.closure_rate)" stroke-width="10" stroke-linecap="round" :stroke-dasharray="getGaugeDash(data.closure_rate)"/>
            </svg>
            <div class="perf-meter__value">{{ data.closure_rate }}%</div>
            <div class="perf-meter__label">{{ data.closed_risks }} of {{ data.total_risks }} risks</div>
          </div>
        </div>
        <div class="data-card">
          <h3 class="data-card__title">📉 Risk Reduction</h3>
          <div class="perf-meter">
            <svg viewBox="0 0 100 50" class="perf-meter__gauge">
              <path d="M5,50 A45,45 0 0,1 95,50" fill="none" stroke="#e0e0e0" stroke-width="10" stroke-linecap="round"/>
              <path d="M5,50 A45,45 0 0,1 95,50" fill="none" :stroke="getGaugeColor(data.avg_reduction_percentage)" stroke-width="10" stroke-linecap="round" :stroke-dasharray="getGaugeDash(data.avg_reduction_percentage)"/>
            </svg>
            <div class="perf-meter__value">{{ data.avg_reduction_percentage }}%</div>
            <div class="perf-meter__label">Avg score reduction</div>
          </div>
        </div>
        <div class="data-card">
          <h3 class="data-card__title">✅ Review Compliance</h3>
          <div class="perf-meter">
            <svg viewBox="0 0 100 50" class="perf-meter__gauge">
              <path d="M5,50 A45,45 0 0,1 95,50" fill="none" stroke="#e0e0e0" stroke-width="10" stroke-linecap="round"/>
              <path d="M5,50 A45,45 0 0,1 95,50" fill="none" :stroke="getGaugeColor(data.review_compliance_rate)" stroke-width="10" stroke-linecap="round" :stroke-dasharray="getGaugeDash(data.review_compliance_rate)"/>
            </svg>
            <div class="perf-meter__value">{{ data.review_compliance_rate }}%</div>
            <div class="perf-meter__label">On-time reviews</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Quarterly Trend -->
    <section class="risk-dashboard__section">
      <ChartCard title="📈 Risk Score Trend (Quarter-on-Quarter)" type="line" :labels="quarterLabels" :datasets="quarterData" height="300px" :loading="loading" />
    </section>

    <!-- Maturity Indicators -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">🎯 Risk Management Maturity Indicators</h3>
        <div class="maturity-grid">
          <div class="maturity-item">
            <span class="maturity-item__label">Risk Identification</span>
            <div class="maturity-item__bar"><div class="maturity-item__fill" :style="{ width: '80%' }"></div></div>
            <span class="maturity-item__score">4/5</span>
          </div>
          <div class="maturity-item">
            <span class="maturity-item__label">Risk Assessment</span>
            <div class="maturity-item__bar"><div class="maturity-item__fill" :style="{ width: Math.min(100, data.coverage_percentage || 0) + '%' }"></div></div>
            <span class="maturity-item__score">{{ Math.round((data.coverage_percentage || 0) / 20) }}/5</span>
          </div>
          <div class="maturity-item">
            <span class="maturity-item__label">Risk Treatment</span>
            <div class="maturity-item__bar"><div class="maturity-item__fill" :style="{ width: Math.min(100, data.closure_rate || 0) + '%' }"></div></div>
            <span class="maturity-item__score">{{ Math.round((data.closure_rate || 0) / 20) }}/5</span>
          </div>
          <div class="maturity-item">
            <span class="maturity-item__label">Monitoring & Review</span>
            <div class="maturity-item__bar"><div class="maturity-item__fill" :style="{ width: Math.min(100, data.review_compliance_rate || 0) + '%' }"></div></div>
            <span class="maturity-item__score">{{ Math.round((data.review_compliance_rate || 0) / 20) }}/5</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'
import './dashboard-risk.css'

export default {
  name: 'RiskPerformanceDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const data = ref({ total_risks: 0, closed_risks: 0, closure_rate: 0, avg_risk_reduction: 0, avg_reduction_percentage: 0, review_compliance_rate: 0, quarterly_trend: [], treatment_completed: 0, treatment_on_time: 0, coverage_percentage: 0 })

    const quarterLabels = computed(() => data.value.quarterly_trend?.map(t => t.quarter) || [])
    const quarterData = computed(() => [
      { label: 'Avg Inherent', data: data.value.quarterly_trend?.map(t => Math.round(t.avg_inherent || 0)) || [], borderColor: '#ef6c00', fill: false },
      { label: 'Avg Residual', data: data.value.quarterly_trend?.map(t => Math.round(t.avg_residual || 0)) || [], borderColor: '#43a047', fill: false }
    ])

    const getGaugeColor = (pct) => { if (pct >= 80) return '#43a047'; if (pct >= 50) return '#fb8c00'; return '#e53935' }
    const getGaugeDash = (pct) => { const arc = 141.37; return `${(pct / 100) * arc} ${arc}` }

    const fetchData = async () => {
      loading.value = true
      try {
        const response = await api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_risk_performance_data')
        if (response.data.message) Object.assign(data.value, response.data.message)
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, data, quarterLabels, quarterData, getGaugeColor, getGaugeDash, fetchData }
  }
}
</script>

<style scoped>
.perf-meter { text-align: center; }
.perf-meter__gauge { width: 120px; height: 60px; margin-bottom: 8px; }
.perf-meter__value { font-size: 28px; font-weight: 700; color: var(--rd-text); }
.perf-meter__label { font-size: 12px; color: var(--rd-muted); }
.maturity-grid { display: flex; flex-direction: column; gap: 16px; }
.maturity-item { display: flex; align-items: center; gap: 16px; }
.maturity-item__label { width: 160px; font-size: 14px; font-weight: 500; }
.maturity-item__bar { flex: 1; height: 12px; background: #e0e0e0; border-radius: 6px; overflow: hidden; }
.maturity-item__fill { height: 100%; background: linear-gradient(90deg, #5c6bc0, #7986cb); border-radius: 6px; transition: width 0.5s; }
.maturity-item__score { width: 40px; font-weight: 700; color: var(--rd-primary); }
</style>

