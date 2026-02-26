<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">📋 Audit Case Dashboard</h1>
        <p class="case-dashboard__subtitle">IIA Standards • Internal Audit Case Tracking</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedPeriod" class="form-select">
          <option value="ytd">Year to Date</option>
          <option value="mtd">Month to Date</option>
          <option value="quarterly">This Quarter</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Audit KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📁" :value="data.total_cases" label="Total Cases" variant="primary" :loading="loading" />
        <KPICard icon="📂" :value="data.open_cases" label="Open Cases" variant="warning" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="info" :loading="loading" />
        <KPICard icon="✅" :value="data.closed_this_month" label="Closed This Month" variant="success" :loading="loading" />
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
        <ChartCard title="📋 Cases by Category" type="bar" :labels="categoryLabels" :datasets="categoryData" height="280px" :loading="loading" />
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
  name: 'AuditCaseDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedPeriod = ref('ytd')
    const data = ref({
      total_cases: 0, open_cases: 0, under_investigation: 0, closed_this_month: 0,
      trend: [], by_source: [], by_category: [], by_status: [], by_severity: []
    })

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'Audit Cases', data: data.value.trend?.map(t => t.total) || [], borderColor: '#5c6bc0', fill: false }])

    const sourceLabels = computed(() => data.value.by_source?.map(s => s.label) || [])
    const sourceData = computed(() => [{ data: data.value.by_source?.map(s => s.value) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#00acc1'] }])

    const categoryLabels = computed(() => data.value.by_category?.map(c => c.label) || [])
    const categoryData = computed(() => [{ label: 'Cases', data: data.value.by_category?.map(c => c.value) || [], backgroundColor: '#5c6bc0' }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const severityLabels = computed(() => data.value.by_severity?.map(s => s.severity_level) || [])
    const severityData = computed(() => [{ label: 'Cases', data: data.value.by_severity?.map(s => s.count) || [], backgroundColor: ['#c62828', '#ef6c00', '#fbc02d', '#66bb6a'] }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [audit, trend, byType, bySeverity] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_audit_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_severity_heatmap')
        ])
        if (audit.data.message) {
          data.value.total_cases = audit.data.message.audit_triggered_cases
          data.value.by_source = audit.data.message.audit_ratio
        }
        if (trend.data.message) data.value.trend = trend.data.message
        if (byType.data.message) data.value.by_category = byType.data.message
        if (bySeverity.data.message) data.value.by_severity = bySeverity.data.message
      } catch (e) { console.error('Failed to load audit dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedPeriod, data, trendLabels, trendData, sourceLabels, sourceData, categoryLabels, categoryData, statusLabels, statusData, severityLabels, severityData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

