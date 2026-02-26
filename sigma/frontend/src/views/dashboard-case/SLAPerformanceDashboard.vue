<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">⏱️ SLA Performance Dashboard</h1>
        <p class="case-dashboard__subtitle">Service Level Compliance • Case Resolution Tracking</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedDepartment" class="form-select">
          <option value="all">All Departments</option>
          <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- SLA KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📂" :value="data.open_cases" label="Open Cases" variant="warning" :loading="loading" />
        <KPICard icon="⚠️" :value="data.sla_breached" label="SLA Breached" variant="danger" :loading="loading" />
        <KPICard icon="✅" :value="data.closed_this_month" label="Closed This Month" variant="success" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="primary" :loading="loading" />
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
  name: 'SLAPerformanceDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedDepartment = ref('all')
    const departments = ref([])
    const data = ref({
      open_cases: 0, sla_breached: 0, closed_this_month: 0, under_investigation: 0,
      sla_trend: [], by_status: [], by_type: [], monthly_trend: []
    })

    const trendLabels = computed(() => data.value.sla_trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'SLA Compliance %', data: data.value.sla_trend?.map(t => t.compliance) || [], borderColor: '#43a047', backgroundColor: 'rgba(67,160,71,0.1)', fill: true }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const typeLabels = computed(() => data.value.by_type?.map(t => t.label) || [])
    const typeData = computed(() => [{ label: 'Cases', data: data.value.by_type?.map(t => t.value) || [], backgroundColor: '#5c6bc0' }])

    const monthlyLabels = computed(() => data.value.monthly_trend?.map(t => t.period) || [])
    const monthlyData = computed(() => [{ label: 'Total Cases', data: data.value.monthly_trend?.map(t => t.total) || [], borderColor: '#5c6bc0', fill: false }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [sla, trend, byType] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_sla_performance_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type')
        ])
        if (sla.data.message) {
          data.value.sla_breached = sla.data.message.overdue_cases
          data.value.by_status = sla.data.message.by_department
        }
        if (trend.data.message) data.value.monthly_trend = trend.data.message
        if (byType.data.message) data.value.by_type = byType.data.message
      } catch (e) { console.error('Failed to load SLA dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedDepartment, departments, data, trendLabels, trendData, statusLabels, statusData, typeLabels, typeData, monthlyLabels, monthlyData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

