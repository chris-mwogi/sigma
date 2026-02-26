<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">🦺 Safety Incident Dashboard</h1>
        <p class="case-dashboard__subtitle">HSE / OSHA / ISO 45001 • Safety Case Tracking</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedRegion" class="form-select">
          <option value="all">All Regions</option>
          <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Safety KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="🦺" :value="data.safety_cases" label="Safety Cases" variant="warning" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_severity" label="High Severity" variant="danger" :loading="loading" />
        <KPICard icon="📆" :value="data.cases_this_month" label="Cases This Month" variant="info" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="primary" :loading="loading" />
      </div>
    </section>

    <!-- Trend Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Safety Incidents Trend" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="⚠️ Cases by Severity" type="pie" :labels="severityLabels" :datasets="severityData" height="280px" :loading="loading" />
        <ChartCard title="🗺️ Cases by Region" type="bar" :labels="regionLabels" :datasets="regionData" height="280px" :loading="loading" />
      </div>
    </section>

    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📋 Cases by Category" type="doughnut" :labels="categoryLabels" :datasets="categoryData" height="280px" :loading="loading" />
        <ChartCard title="📊 Cases by Status" type="bar" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'SafetyIncidentDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedRegion = ref('all')
    const regions = ref([])
    const data = ref({
      safety_cases: 0, high_severity: 0, cases_this_month: 0, under_investigation: 0,
      trend: [], by_severity: [], by_region: [], by_category: [], by_status: []
    })

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'Safety Incidents', data: data.value.trend?.map(t => t.total) || [], borderColor: '#fb8c00', backgroundColor: 'rgba(251,140,0,0.1)', fill: true }])

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity) || [])
    const severityData = computed(() => [{ data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#c62828', '#ef6c00', '#fbc02d', '#66bb6a'] }])

    const regionLabels = computed(() => data.value.by_region?.map(r => r.region) || [])
    const regionData = computed(() => [{ label: 'Cases', data: data.value.by_region?.map(r => r.count) || [], backgroundColor: '#fb8c00' }])

    const categoryLabels = computed(() => data.value.by_category?.map(c => c.label) || [])
    const categoryData = computed(() => [{ data: data.value.by_category?.map(c => c.value) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#00acc1', '#e53935'] }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ label: 'Cases', data: data.value.by_status?.map(s => s.count) || [], backgroundColor: '#5c6bc0' }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [safety, trend] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_safety_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' })
        ])
        if (safety.data.message) {
          data.value.safety_cases = safety.data.message.safety_incidents
          data.value.by_region = safety.data.message.by_region
          data.value.by_severity = safety.data.message.severity_pyramid
        }
        if (trend.data.message) data.value.trend = trend.data.message
      } catch (e) { console.error('Failed to load safety dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedRegion, regions, data, trendLabels, trendData, severityLabels, severityData, regionLabels, regionData, categoryLabels, categoryData, statusLabels, statusData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

