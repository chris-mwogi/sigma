<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">📊 Case Executive Dashboard</h1>
        <p class="case-dashboard__subtitle">Board-Level Overview • Strategic Case Management Insights</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedPeriod" class="form-select" @change="fetchData">
          <option value="ytd">Year to Date</option>
          <option value="mtd">Month to Date</option>
          <option value="quarterly">This Quarter</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Executive KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--6">
        <KPICard icon="📁" :value="data.total_cases_ytd" label="Total Cases (YTD)" variant="primary" :loading="loading" />
        <KPICard icon="📂" :value="data.open_cases" label="Open Cases" variant="warning" :loading="loading" />
        <KPICard icon="📆" :value="data.total_cases_mtd" label="Cases This Month" variant="info" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_severity_cases" label="High Severity" variant="danger" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="warning" :loading="loading" />
        <KPICard icon="✅" :value="data.closed_cases" label="Closed This Month" variant="success" :loading="loading" />
      </div>
    </section>

    <!-- Charts Section -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Case Trend (Monthly)" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
    </section>

    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Cases by Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
        <ChartCard title="📋 Cases by Type" type="bar" :labels="typeLabels" :datasets="typeData" height="280px" :loading="loading" />
      </div>
    </section>

    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="⚠️ Cases by Severity" type="pie" :labels="severityLabels" :datasets="severityData" height="280px" :loading="loading" />
        <ChartCard title="🗺️ Cases by Region" type="bar" :labels="regionLabels" :datasets="regionData" height="280px" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'CaseExecutiveDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedPeriod = ref('ytd')
    const data = ref({
      total_cases_ytd: 0, open_cases: 0, total_cases_mtd: 0,
      high_severity_cases: 0, under_investigation: 0, closed_cases: 0,
      trend: [], by_status: [], by_type: [], by_severity: [], by_region: []
    })

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [
      { label: 'Total', data: data.value.trend?.map(t => t.total) || [], borderColor: '#5c6bc0', fill: false },
      { label: 'Closed', data: data.value.trend?.map(t => t.closed) || [], borderColor: '#43a047', fill: false }
    ])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const typeLabels = computed(() => data.value.by_type?.map(t => t.case_type) || [])
    const typeData = computed(() => [{ label: 'Cases', data: data.value.by_type?.map(t => t.count) || [], backgroundColor: '#5c6bc0' }])

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity_level) || [])
    const severityData = computed(() => [{ data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#c62828', '#ef6c00', '#fbc02d', '#66bb6a'] }])

    const regionLabels = computed(() => data.value.by_region?.map(r => r.region) || [])
    const regionData = computed(() => [{ label: 'Cases', data: data.value.by_region?.map(r => r.count) || [], backgroundColor: '#00acc1' }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [overview, trend, byStatus, byType, bySeverity, byRegion] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_executive_overview'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_severity_heatmap'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_by_business_unit')
        ])
        if (overview.data.message) Object.assign(data.value, overview.data.message)
        if (trend.data.message) data.value.trend = trend.data.message
        if (byStatus.data.message) data.value.by_status = byStatus.data.message
        if (byType.data.message) data.value.by_type = byType.data.message
        if (bySeverity.data.message) data.value.by_severity = bySeverity.data.message
        if (byRegion.data.message) data.value.by_region = byRegion.data.message
      } catch (e) { console.error('Failed to load case executive dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedPeriod, data, trendLabels, trendData, statusLabels, statusData, typeLabels, typeData, severityLabels, severityData, regionLabels, regionData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

