<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">⚠️ Incident & Loss Events Dashboard</h1>
        <p class="risk-dashboard__subtitle">Monitor Realised Risks & Operational Incidents • Operations, Security, Compliance</p>
      </div>
      <div class="risk-dashboard__actions">
        <select v-model="selectedPeriod" class="form-select" @change="fetchData">
          <option value="12">Last 12 Months</option>
          <option value="6">Last 6 Months</option>
          <option value="3">Last 3 Months</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Incident KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📊" :value="data.total_incidents" label="Total Incidents" variant="primary" :loading="loading" />
        <KPICard icon="🔴" :value="criticalCount" label="Critical/High Severity" variant="danger" :loading="loading" />
        <KPICard icon="📅" :value="thisMonthCount" label="This Month" variant="warning" :loading="loading" />
        <KPICard icon="📈" :value="avgPerMonth" label="Avg per Month" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Charts Row 1 -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Incidents by Severity" type="bar" :labels="severityLabels" :datasets="severityData" height="280px" :loading="loading" />
        <ChartCard title="📋 Incidents by Risk Category" type="doughnut" :labels="categoryLabels" :datasets="categoryData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Trend Chart -->
    <section class="risk-dashboard__section">
      <ChartCard title="📈 Incidents Over Time" type="line" :labels="trendLabels" :datasets="trendData" height="300px" :loading="loading" />
    </section>

    <!-- Top Risks with Incidents -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">🔝 Top Risks with Most Incidents</h3>
        <DataTable :columns="topRiskColumns" :data="data.top_risks_by_incidents" :loading="loading" emptyText="No incident data available">
          <template #cell-incident_count="{ value }">
            <span class="incident-count">{{ value }}</span>
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
  name: 'IncidentLossDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedPeriod = ref('12')
    const data = ref({ total_incidents: 0, by_severity: [], by_category: [], over_time: [], top_risks_by_incidents: [] })

    const criticalCount = computed(() => {
      return data.value.by_severity?.filter(s => ['Critical', 'High'].includes(s.severity)).reduce((sum, s) => sum + s.count, 0) || 0
    })
    const thisMonthCount = computed(() => {
      const currentMonth = new Date().toISOString().slice(0, 7)
      return data.value.over_time?.find(t => t.period === currentMonth)?.count || 0
    })
    const avgPerMonth = computed(() => {
      const total = data.value.over_time?.reduce((sum, t) => sum + t.count, 0) || 0
      const months = data.value.over_time?.length || 1
      return Math.round(total / months)
    })

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity) || [])
    const severityData = computed(() => [{ label: 'Incidents', data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#c62828', '#ef6c00', '#fbc02d', '#66bb6a', '#9e9e9e'] }])

    const categoryLabels = computed(() => data.value.by_category?.map(c => c.category) || [])
    const categoryData = computed(() => [{ data: data.value.by_category?.map(c => c.count) || [], backgroundColor: ['#5c6bc0', '#00acc1', '#43a047', '#fb8c00', '#e53935', '#7b1fa2', '#607d8b'] }])

    const trendLabels = computed(() => data.value.over_time?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'Incidents', data: data.value.over_time?.map(t => t.count) || [], borderColor: '#5c6bc0', backgroundColor: 'rgba(92, 107, 192, 0.1)', fill: true }])

    const topRiskColumns = [
      { key: 'risk_title', label: 'Risk Title' },
      { key: 'incident_count', label: 'Incident Count' }
    ]

    const fetchData = async () => {
      loading.value = true
      try {
        const response = await api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_incident_dashboard_data')
        if (response.data.message) Object.assign(data.value, response.data.message)
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, selectedPeriod, data, criticalCount, thisMonthCount, avgPerMonth, severityLabels, severityData, categoryLabels, categoryData, trendLabels, trendData, topRiskColumns, fetchData }
  }
}
</script>

<style scoped>
.incident-count { display: inline-flex; align-items: center; justify-content: center; min-width: 32px; height: 32px; background: rgba(92, 107, 192, 0.15); color: #5c6bc0; font-weight: 700; border-radius: 6px; }
</style>

