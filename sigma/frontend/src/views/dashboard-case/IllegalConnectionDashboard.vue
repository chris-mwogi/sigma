<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">⚡ Illegal Connection Dashboard</h1>
        <p class="case-dashboard__subtitle">Revenue Protection • Illegal Connection Tracking</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedRegion" class="form-select">
          <option value="all">All Regions</option>
          <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Illegal Connection KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="⚡" :value="data.total_connections" label="Total Illegal Connections" variant="danger" :loading="loading" />
        <KPICard icon="📁" :value="data.total_cases" label="Total Cases" variant="primary" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_severity" label="High Severity" variant="danger" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Trend Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Illegal Connection Trend" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📋 Illegal Connection by Type" type="pie" :labels="typeLabels" :datasets="typeData" height="280px" :loading="loading" />
        <ChartCard title="🗺️ Cases by Region" type="bar" :labels="regionLabels" :datasets="regionData" height="280px" :loading="loading" />
      </div>
    </section>

    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Cases by Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
        <ChartCard title="⚠️ Cases by Severity" type="bar" :labels="severityLabels" :datasets="severityData" height="280px" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'IllegalConnectionDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedRegion = ref('all')
    const regions = ref([])
    const data = ref({
      total_connections: 0, total_cases: 0, high_severity: 0, under_investigation: 0,
      trend: [], by_type: [], by_region: [], by_status: [], by_severity: []
    })

    const trendLabels = computed(() => data.value.trend?.map(t => t.month) || [])
    const trendData = computed(() => [{ label: 'Illegal Connections', data: data.value.trend?.map(t => t.count) || [], borderColor: '#ff5722', backgroundColor: 'rgba(255,87,34,0.1)', fill: true }])

    const typeLabels = computed(() => data.value.by_type?.map(t => t.connection_type) || [])
    const typeData = computed(() => [{ data: data.value.by_type?.map(t => t.count) || [], backgroundColor: ['#ff5722', '#fb8c00', '#fbc02d', '#43a047', '#00acc1'] }])

    const regionLabels = computed(() => data.value.by_region?.map(r => r.region) || [])
    const regionData = computed(() => [{ label: 'Cases', data: data.value.by_region?.map(r => r.count) || [], backgroundColor: '#ff5722' }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity_level) || [])
    const severityData = computed(() => [{ label: 'Cases', data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#c62828', '#ef6c00', '#fbc02d', '#66bb6a'] }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [illegal, bySeverity] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_illegal_connection_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_severity_heatmap')
        ])
        if (illegal.data.message) {
          data.value.total_connections = illegal.data.message.total_connections
          data.value.by_type = illegal.data.message.by_type
          data.value.by_region = illegal.data.message.by_region
          data.value.trend = illegal.data.message.trend
        }
        if (bySeverity.data.message) data.value.by_severity = bySeverity.data.message
      } catch (e) { console.error('Failed to load illegal connection dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedRegion, regions, data, trendLabels, trendData, typeLabels, typeData, regionLabels, regionData, statusLabels, statusData, severityLabels, severityData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

