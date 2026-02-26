<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">⚖️ Legal Case Dashboard</h1>
        <p class="case-dashboard__subtitle">Legal & Regulatory • Litigation Tracking</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedCourt" class="form-select">
          <option value="all">All Courts</option>
          <option v-for="court in courts" :key="court" :value="court">{{ court }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Legal KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="⚖️" :value="data.active_legal" label="Active Legal Cases" variant="primary" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_severity" label="High Severity" variant="danger" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="warning" :loading="loading" />
        <KPICard icon="📆" :value="data.cases_this_month" label="Cases This Month" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Trend Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Case Trend (Monthly)" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📋 Cases by Type" type="bar" :labels="typeLabels" :datasets="typeData" height="280px" :loading="loading" />
        <ChartCard title="📊 Cases by Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Region Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="🗺️ Cases by Region" type="bar" :labels="regionLabels" :datasets="regionData" height="300px" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'LegalCaseDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedCourt = ref('all')
    const courts = ref([])
    const data = ref({
      active_legal: 0, high_severity: 0, under_investigation: 0, cases_this_month: 0,
      trend: [], by_type: [], by_status: [], by_region: []
    })

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'Legal Cases', data: data.value.trend?.map(t => t.total) || [], borderColor: '#5c6bc0', fill: false }])

    const typeLabels = computed(() => data.value.by_type?.map(t => t.label) || [])
    const typeData = computed(() => [{ label: 'Cases', data: data.value.by_type?.map(t => t.value) || [], backgroundColor: '#5c6bc0' }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const regionLabels = computed(() => data.value.by_region?.map(r => r.region) || [])
    const regionData = computed(() => [{ label: 'Cases', data: data.value.by_region?.map(r => r.total) || [], backgroundColor: '#00acc1' }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [legal, trend, byType, byRegion] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_legal_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_by_business_unit')
        ])
        if (legal.data.message) {
          data.value.active_legal = legal.data.message.active_legal_cases
          data.value.by_status = legal.data.message.by_court_type
        }
        if (trend.data.message) data.value.trend = trend.data.message
        if (byType.data.message) data.value.by_type = byType.data.message
        if (byRegion.data.message) data.value.by_region = byRegion.data.message
      } catch (e) { console.error('Failed to load legal dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedCourt, courts, data, trendLabels, trendData, typeLabels, typeData, statusLabels, statusData, regionLabels, regionData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

