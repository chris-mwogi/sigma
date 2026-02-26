<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">📢 Whistleblower Dashboard</h1>
        <p class="case-dashboard__subtitle">Ethics Hotline • Anonymous Reporting Analytics</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedChannel" class="form-select">
          <option value="all">All Channels</option>
          <option v-for="channel in channels" :key="channel" :value="channel">{{ channel }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Whistleblower KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📁" :value="data.total_cases" label="Total Cases" variant="primary" :loading="loading" />
        <KPICard icon="📂" :value="data.open_cases" label="Open Cases" variant="warning" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_severity" label="High Severity" variant="danger" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Trend Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Case Trend (Monthly)" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📥 Cases by Source" type="pie" :labels="sourceLabels" :datasets="sourceData" height="280px" :loading="loading" />
        <ChartCard title="📋 Cases by Type" type="bar" :labels="typeLabels" :datasets="typeData" height="280px" :loading="loading" />
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
  name: 'WhistleblowerDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedChannel = ref('all')
    const channels = ref([])
    const data = ref({
      total_cases: 0, open_cases: 0, high_severity: 0, under_investigation: 0,
      trend: [], by_source: [], by_type: [], by_status: [], by_severity: []
    })

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'Reports', data: data.value.trend?.map(t => t.total) || [], borderColor: '#9c27b0', backgroundColor: 'rgba(156,39,176,0.1)', fill: true }])

    const sourceLabels = computed(() => data.value.by_source?.map(s => s.channel) || [])
    const sourceData = computed(() => [{ data: data.value.by_source?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#00acc1', '#9c27b0'] }])

    const typeLabels = computed(() => data.value.by_type?.map(t => t.label) || [])
    const typeData = computed(() => [{ label: 'Cases', data: data.value.by_type?.map(t => t.value) || [], backgroundColor: '#5c6bc0' }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity_level) || [])
    const severityData = computed(() => [{ label: 'Cases', data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#c62828', '#ef6c00', '#fbc02d', '#66bb6a'] }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [whistle, trend, byType, bySeverity] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_whistleblower_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_severity_heatmap')
        ])
        if (whistle.data.message) {
          data.value.total_cases = whistle.data.message.anonymous_reports
          data.value.high_severity = whistle.data.message.high_severity_anonymous
          data.value.by_source = whistle.data.message.by_channel
          data.value.trend = whistle.data.message.reports_trend
        }
        if (trend.data.message && !data.value.trend?.length) data.value.trend = trend.data.message
        if (byType.data.message) data.value.by_type = byType.data.message
        if (bySeverity.data.message) data.value.by_severity = bySeverity.data.message
      } catch (e) { console.error('Failed to load whistleblower dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedChannel, channels, data, trendLabels, trendData, sourceLabels, sourceData, typeLabels, typeData, statusLabels, statusData, severityLabels, severityData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

