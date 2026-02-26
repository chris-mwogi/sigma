<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">🔍 Case Investigation Dashboard</h1>
        <p class="case-dashboard__subtitle">Investigation Management • Evidence & Case Tracking</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedInvestigator" class="form-select">
          <option value="all">All Investigators</option>
          <option v-for="inv in investigators" :key="inv" :value="inv">{{ inv }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Investigation KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📂" :value="data.open_cases" label="Open Cases" variant="warning" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="primary" :loading="loading" />
        <KPICard icon="👤" :value="data.pending_assignments" label="Pending Assignments" variant="danger" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_severity" label="High Severity" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Investigation Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
        <ChartCard title="📋 Cases by Category" type="bar" :labels="categoryLabels" :datasets="categoryData" height="280px" :loading="loading" />
      </div>
    </section>

    <section class="case-dashboard__section">
      <ChartCard title="📈 Case Trend (Monthly)" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
    </section>

    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📥 Cases by Source" type="pie" :labels="sourceLabels" :datasets="sourceData" height="280px" :loading="loading" />
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
  name: 'CaseInvestigationDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedInvestigator = ref('all')
    const investigators = ref([])
    const data = ref({
      open_cases: 0, under_investigation: 0, pending_assignments: 0, high_severity: 0,
      by_status: [], by_category: [], trend: [], by_source: [], by_severity: []
    })

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const categoryLabels = computed(() => data.value.by_category?.map(c => c.label) || [])
    const categoryData = computed(() => [{ label: 'Cases', data: data.value.by_category?.map(c => c.value) || [], backgroundColor: '#5c6bc0' }])

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [
      { label: 'Total', data: data.value.trend?.map(t => t.total) || [], borderColor: '#5c6bc0', fill: false },
      { label: 'Closed', data: data.value.trend?.map(t => t.closed) || [], borderColor: '#43a047', fill: false }
    ])

    const sourceLabels = computed(() => data.value.by_source?.map(s => s.label) || [])
    const sourceData = computed(() => [{ data: data.value.by_source?.map(s => s.value) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#00acc1', '#e53935'] }])

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity_level) || [])
    const severityData = computed(() => [{ label: 'Cases', data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#c62828', '#ef6c00', '#fbc02d', '#66bb6a'] }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [investigation, trend, byCategory, bySeverity] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_investigation_overview'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_severity_heatmap')
        ])
        if (investigation.data.message) Object.assign(data.value, investigation.data.message)
        if (trend.data.message) data.value.trend = trend.data.message
        if (byCategory.data.message) data.value.by_category = byCategory.data.message
        if (bySeverity.data.message) data.value.by_severity = bySeverity.data.message
      } catch (e) { console.error('Failed to load investigation dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedInvestigator, investigators, data, statusLabels, statusData, categoryLabels, categoryData, trendLabels, trendData, sourceLabels, sourceData, severityLabels, severityData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

