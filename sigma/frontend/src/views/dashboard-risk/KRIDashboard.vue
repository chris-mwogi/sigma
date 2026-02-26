<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">📈 Key Risk Indicator (KRI) Dashboard</h1>
        <p class="risk-dashboard__subtitle">Early Warning & Predictive Risk Monitoring • Risk & Operations Managers</p>
      </div>
      <div class="risk-dashboard__actions">
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- KRI Status KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="✅" :value="data.normal_count" label="Normal Status" variant="success" :loading="loading" />
        <KPICard icon="⚠️" :value="data.warning_count" label="Warning Status" variant="warning" :loading="loading" />
        <KPICard icon="🔴" :value="data.critical_count" label="Critical Status" variant="danger" :loading="loading" />
        <KPICard icon="📊" :value="data.total_active" label="Total Active KRIs" variant="primary" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 KRI Status Distribution" type="doughnut" :labels="['Normal', 'Warning', 'Critical']" :datasets="statusData" height="280px" :loading="loading" />
        <ChartCard title="📈 KRI Trend (6 Months)" type="line" :labels="trendLabels" :datasets="trendData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Active Alerts -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">🚨 Active KRI Alerts</h3>
        <div class="kri-alerts">
          <div v-for="kri in data.active_alerts" :key="kri.name" class="kri-alert" :class="'kri-alert--' + kri.current_status?.toLowerCase()">
            <div class="kri-alert__header">
              <span class="kri-alert__name">{{ kri.kri_name }}</span>
              <span class="kri-alert__status badge" :class="'badge--' + kri.current_status?.toLowerCase()">{{ kri.current_status }}</span>
            </div>
            <div class="kri-alert__body">
              <div class="kri-alert__metric">
                <span class="kri-alert__label">Current Value</span>
                <span class="kri-alert__value">{{ kri.current_value }}</span>
              </div>
              <div class="kri-alert__metric">
                <span class="kri-alert__label">Target</span>
                <span class="kri-alert__value">{{ kri.target_value }}</span>
              </div>
              <div class="kri-alert__metric">
                <span class="kri-alert__label">Trend</span>
                <span class="kri-alert__trend" :class="getTrendClass(kri.trend)">{{ getTrendIcon(kri.trend) }} {{ kri.trend }}</span>
              </div>
            </div>
            <div class="kri-alert__footer">
              <span class="kri-alert__category">{{ kri.kri_category }}</span>
              <span class="kri-alert__date">Last: {{ kri.last_reading_date }}</span>
            </div>
          </div>
        </div>
        <div v-if="!data.active_alerts?.length && !loading" class="empty-state">
          <div class="empty-state__icon">✅</div>
          <div class="empty-state__text">No active alerts - all KRIs are within normal thresholds</div>
        </div>
      </div>
    </section>

    <!-- Top Deviations -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">📊 Top 5 KRIs by Deviation</h3>
        <DataTable :columns="deviationColumns" :data="data.top_deviation" :loading="loading" emptyText="No deviation data available" />
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
  name: 'KRIDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const data = ref({ normal_count: 0, warning_count: 0, critical_count: 0, total_active: 0, by_status: [], active_alerts: [], top_deviation: [], trends: [] })

    const statusData = computed(() => [{ data: [data.value.normal_count, data.value.warning_count, data.value.critical_count], backgroundColor: ['#43a047', '#fb8c00', '#e53935'] }])
    
    const trendLabels = computed(() => data.value.trends?.map(t => t.period) || [])
    const trendData = computed(() => [
      { label: 'Normal', data: data.value.trends?.map(t => t.normal) || [], borderColor: '#43a047', fill: false },
      { label: 'Warning', data: data.value.trends?.map(t => t.warning) || [], borderColor: '#fb8c00', fill: false },
      { label: 'Critical', data: data.value.trends?.map(t => t.critical) || [], borderColor: '#e53935', fill: false }
    ])

    const deviationColumns = [
      { key: 'kri_name', label: 'KRI Name' },
      { key: 'kri_category', label: 'Category' },
      { key: 'current_value', label: 'Current' },
      { key: 'target_value', label: 'Target' },
      { key: 'deviation_pct', label: 'Deviation %', type: 'number' },
      { key: 'current_status', label: 'Status', type: 'badge' }
    ]

    const getTrendClass = (trend) => ({ 'Improving': 'trend--up', 'Stable': 'trend--stable', 'Deteriorating': 'trend--down' }[trend] || '')
    const getTrendIcon = (trend) => ({ 'Improving': '↗', 'Stable': '→', 'Deteriorating': '↘' }[trend] || '–')

    const fetchData = async () => {
      loading.value = true
      try {
        const [kriData, trends] = await Promise.all([
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_kri_dashboard_data'),
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_kri_trends', { months: 6 })
        ])
        if (kriData.data.message) Object.assign(data.value, kriData.data.message)
        if (trends.data.message) data.value.trends = trends.data.message
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, data, statusData, trendLabels, trendData, deviationColumns, getTrendClass, getTrendIcon, fetchData }
  }
}
</script>

<style scoped>
.kri-alerts { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.kri-alert { background: var(--rd-bg); border-radius: 8px; padding: 16px; border-left: 4px solid; }
.kri-alert--warning { border-left-color: #fb8c00; }
.kri-alert--critical { border-left-color: #e53935; }
.kri-alert__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.kri-alert__name { font-weight: 600; font-size: 14px; }
.kri-alert__body { display: flex; gap: 16px; margin-bottom: 12px; }
.kri-alert__metric { text-align: center; }
.kri-alert__label { font-size: 10px; color: var(--rd-muted); display: block; }
.kri-alert__value { font-size: 18px; font-weight: 700; }
.kri-alert__trend { font-size: 12px; font-weight: 600; }
.trend--up { color: #43a047; }
.trend--stable { color: #757575; }
.trend--down { color: #e53935; }
.kri-alert__footer { display: flex; justify-content: space-between; font-size: 11px; color: var(--rd-muted); }
.badge--warning { background: rgba(251, 140, 0, 0.15); color: #e65100; }
.badge--critical { background: rgba(229, 57, 53, 0.15); color: #c62828; }
</style>

