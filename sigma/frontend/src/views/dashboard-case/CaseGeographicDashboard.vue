<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">🗺️ Case Geographic Dashboard</h1>
        <p class="case-dashboard__subtitle">Regional Analysis • Case Heatmap & Distribution</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedRegion" class="form-select">
          <option value="all">All Regions</option>
          <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Geographic KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📁" :value="data.total_cases" label="Total Cases" variant="primary" :loading="loading" />
        <KPICard icon="📂" :value="data.open_cases" label="Open Cases" variant="warning" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_severity" label="High Severity" variant="danger" :loading="loading" />
        <KPICard icon="📆" :value="data.cases_this_month" label="Cases This Month" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Region Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="🗺️ Cases by Region" type="bar" :labels="regionLabels" :datasets="regionData" height="350px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📋 Cases by Type" type="pie" :labels="typeLabels" :datasets="typeData" height="280px" :loading="loading" />
        <ChartCard title="⚠️ Cases by Severity" type="doughnut" :labels="severityLabels" :datasets="severityData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Trend Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Case Trend (Monthly)" type="line" :labels="trendLabels" :datasets="trendData" height="300px" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'CaseGeographicDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedRegion = ref('all')
    const regions = ref([])
    const data = ref({
      total_cases: 0, open_cases: 0, high_severity: 0, cases_this_month: 0,
      by_region: [], by_type: [], by_severity: [], trend: []
    })

    const regionLabels = computed(() => data.value.by_region?.map(r => r.region) || [])
    const regionData = computed(() => [
      { label: 'Total', data: data.value.by_region?.map(r => r.total) || [], backgroundColor: '#5c6bc0' },
      { label: 'Open', data: data.value.by_region?.map(r => r.open_count) || [], backgroundColor: '#fb8c00' }
    ])

    const typeLabels = computed(() => data.value.by_type?.map(t => t.label) || [])
    const typeData = computed(() => [{ data: data.value.by_type?.map(t => t.value) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#00acc1', '#e53935'] }])

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity_level) || [])
    const severityData = computed(() => [{ data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#c62828', '#ef6c00', '#fbc02d', '#66bb6a'] }])

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'Total Cases', data: data.value.trend?.map(t => t.total) || [], borderColor: '#5c6bc0', fill: false }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [geo, trend, byType, bySeverity] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_geo_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_severity_heatmap')
        ])
        if (geo.data.message) data.value.by_region = geo.data.message.by_region
        if (trend.data.message) data.value.trend = trend.data.message
        if (byType.data.message) data.value.by_type = byType.data.message
        if (bySeverity.data.message) data.value.by_severity = bySeverity.data.message
      } catch (e) { console.error('Failed to load geographic dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedRegion, regions, data, regionLabels, regionData, typeLabels, typeData, severityLabels, severityData, trendLabels, trendData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

