<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">✅ Case Closure Dashboard</h1>
        <p class="case-dashboard__subtitle">Post-Incident Review • Lessons Learned Tracking</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedPeriod" class="form-select">
          <option value="mtd">Month to Date</option>
          <option value="qtd">Quarter to Date</option>
          <option value="ytd">Year to Date</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Closure KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="✅" :value="data.closed_this_month" label="Closed This Month" variant="success" :loading="loading" />
        <KPICard icon="📁" :value="data.total_cases" label="Total Cases" variant="primary" :loading="loading" />
        <KPICard icon="📂" :value="data.open_cases" label="Open Cases" variant="warning" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- SLA Compliance Trend -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 SLA Compliance Trend" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Cases by Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
        <ChartCard title="📋 Cases by Type" type="bar" :labels="typeLabels" :datasets="typeData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Monthly Trend -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Case Trend (Monthly)" type="line" :labels="monthlyLabels" :datasets="monthlyData" height="300px" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'CaseClosureDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedPeriod = ref('mtd')
    const data = ref({
      closed_this_month: 0, total_cases: 0, open_cases: 0, under_investigation: 0,
      sla_trend: [], by_status: [], by_type: [], monthly_trend: []
    })

    const trendLabels = computed(() => data.value.sla_trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'SLA Compliance %', data: data.value.sla_trend?.map(t => t.compliance) || [], borderColor: '#43a047', backgroundColor: 'rgba(67,160,71,0.1)', fill: true }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const typeLabels = computed(() => data.value.by_type?.map(t => t.label) || [])
    const typeData = computed(() => [{ label: 'Cases', data: data.value.by_type?.map(t => t.value) || [], backgroundColor: '#5c6bc0' }])

    const monthlyLabels = computed(() => data.value.monthly_trend?.map(t => t.period) || [])
    const monthlyData = computed(() => [
      { label: 'Total', data: data.value.monthly_trend?.map(t => t.total) || [], borderColor: '#5c6bc0', fill: false },
      { label: 'Closed', data: data.value.monthly_trend?.map(t => t.closed) || [], borderColor: '#43a047', fill: false }
    ])

    const fetchData = async () => {
      loading.value = true
      try {
        const [closure, trend, byType] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_closure_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type')
        ])
        if (closure.data.message) {
          data.value.closed_this_month = closure.data.message.closed_this_month
        }
        if (trend.data.message) data.value.monthly_trend = trend.data.message
        if (byType.data.message) data.value.by_type = byType.data.message
      } catch (e) { console.error('Failed to load closure dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedPeriod, data, trendLabels, trendData, statusLabels, statusData, typeLabels, typeData, monthlyLabels, monthlyData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

