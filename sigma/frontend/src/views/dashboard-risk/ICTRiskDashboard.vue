<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">💻 ICT / Cyber Risk Dashboard</h1>
        <p class="risk-dashboard__subtitle">Technology & Cyber Risk Visibility • ICT Security, Infrastructure Teams</p>
      </div>
      <div class="risk-dashboard__actions">
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- ICT KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="💻" :value="data.total_ict_risks" label="ICT Risks" variant="primary" :loading="loading" />
        <KPICard icon="🔴" :value="criticalCount" label="Critical/High" variant="danger" :loading="loading" />
        <KPICard icon="📊" :value="data.ict_kris?.length || 0" label="ICT KRIs" variant="info" :loading="loading" />
        <KPICard icon="⚠️" :value="alertingKRIs" label="KRIs in Alert" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 ICT Risks by Severity" type="doughnut" :labels="severityLabels" :datasets="severityData" height="280px" :loading="loading" />
        <div class="data-card">
          <h3 class="data-card__title">🔐 Cyber Risk Categories</h3>
          <div class="cyber-categories">
            <div class="cyber-category" v-for="cat in cyberCategories" :key="cat.name">
              <span class="cyber-category__icon">{{ cat.icon }}</span>
              <span class="cyber-category__name">{{ cat.name }}</span>
              <span class="cyber-category__count">{{ cat.count }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ICT KRIs -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">📈 ICT Key Risk Indicators</h3>
        <div class="kri-grid" v-if="data.ict_kris?.length">
          <div v-for="kri in data.ict_kris" :key="kri.name" class="kri-card" :class="'kri-card--' + kri.current_status?.toLowerCase()">
            <div class="kri-card__header">
              <span class="kri-card__name">{{ kri.kri_name }}</span>
              <span class="kri-card__status badge" :class="getStatusClass(kri.current_status)">{{ kri.current_status }}</span>
            </div>
            <div class="kri-card__values">
              <div class="kri-card__current">
                <span class="kri-card__label">Current</span>
                <span class="kri-card__value">{{ kri.current_value }}</span>
              </div>
              <div class="kri-card__target">
                <span class="kri-card__label">Target</span>
                <span class="kri-card__value">{{ kri.target_value }}</span>
              </div>
              <div class="kri-card__trend">
                <span class="kri-card__label">Trend</span>
                <span class="kri-card__value" :class="getTrendClass(kri.trend)">{{ getTrendIcon(kri.trend) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-state__icon">📊</div>
          <div class="empty-state__text">No ICT KRIs configured</div>
        </div>
      </div>
    </section>

    <!-- ICT Risks List -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">🔒 ICT Risk Register</h3>
        <DataTable :columns="riskColumns" :data="data.ict_risks" :loading="loading" emptyText="No ICT risks found">
          <template #cell-residual_risk_rating="{ value }">
            <span class="badge" :class="getRatingClass(value)">{{ value || 'Not Assessed' }}</span>
          </template>
        </DataTable>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'
import './dashboard-risk.css'

export default {
  name: 'ICTRiskDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const data = ref({ by_severity: [], ict_risks: [], ict_kris: [], total_ict_risks: 0 })

    const criticalCount = computed(() => data.value.by_severity?.filter(s => ['Critical', 'High', 'Extreme'].includes(s.severity)).reduce((sum, s) => sum + s.count, 0) || 0)
    const alertingKRIs = computed(() => data.value.ict_kris?.filter(k => ['Warning', 'Critical'].includes(k.current_status)).length || 0)

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity) || [])
    const severityData = computed(() => [{ data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#7b1fa2', '#c62828', '#ef6c00', '#fbc02d', '#66bb6a', '#9e9e9e'] }])

    const cyberCategories = [
      { name: 'Data Breach', icon: '🔓', count: 0 },
      { name: 'Malware', icon: '🦠', count: 0 },
      { name: 'Phishing', icon: '🎣', count: 0 },
      { name: 'System Failure', icon: '💥', count: 0 },
      { name: 'Access Control', icon: '🔐', count: 0 }
    ]

    const riskColumns = [
      { key: 'risk_title', label: 'Risk' },
      { key: 'risk_category', label: 'Category' },
      { key: 'status', label: 'Status' },
      { key: 'residual_risk_rating', label: 'Rating' }
    ]

    const getStatusClass = (status) => ({ 'Normal': 'badge--success', 'Warning': 'badge--warning', 'Critical': 'badge--danger' }[status] || 'badge--info')
    const getTrendClass = (trend) => ({ 'Improving': 'trend--up', 'Stable': 'trend--stable', 'Deteriorating': 'trend--down' }[trend] || '')
    const getTrendIcon = (trend) => ({ 'Improving': '↗', 'Stable': '→', 'Deteriorating': '↘' }[trend] || '–')
    const getRatingClass = (rating) => {
      const r = (rating || '').toLowerCase()
      if (r.includes('extreme')) return 'badge--extreme'
      if (r.includes('critical')) return 'badge--critical'
      if (r.includes('high')) return 'badge--high'
      if (r.includes('medium')) return 'badge--medium'
      return 'badge--low'
    }

    const fetchData = async () => {
      loading.value = true
      try {
        const response = await api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_ict_risk_dashboard_data')
        if (response.data.message) Object.assign(data.value, response.data.message)
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, data, criticalCount, alertingKRIs, severityLabels, severityData, cyberCategories, riskColumns, getStatusClass, getTrendClass, getTrendIcon, getRatingClass, fetchData }
  }
}
</script>

<style scoped>
.cyber-categories { display: flex; flex-direction: column; gap: 8px; }
.cyber-category { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--rd-bg); border-radius: 6px; }
.cyber-category__icon { font-size: 20px; }
.cyber-category__name { flex: 1; font-weight: 500; }
.cyber-category__count { font-weight: 700; color: var(--rd-primary); }
.kri-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.kri-card { padding: 16px; background: var(--rd-bg); border-radius: 8px; border-left: 4px solid #5c6bc0; }
.kri-card--warning { border-left-color: #fb8c00; }
.kri-card--critical { border-left-color: #e53935; }
.kri-card__header { display: flex; justify-content: space-between; margin-bottom: 12px; }
.kri-card__name { font-weight: 600; font-size: 13px; }
.kri-card__values { display: flex; gap: 16px; }
.kri-card__label { font-size: 10px; color: var(--rd-muted); display: block; }
.kri-card__value { font-size: 16px; font-weight: 700; }
.trend--up { color: #43a047; }
.trend--stable { color: #757575; }
.trend--down { color: #e53935; }
</style>

