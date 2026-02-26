<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">📞 Customer Complaint Dashboard</h1>
        <p class="case-dashboard__subtitle">Customer Resolution • Complaint Tracking & SLA</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedRegion" class="form-select">
          <option value="all">All Regions</option>
          <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Complaint KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📞" :value="data.complaints" label="Customer Complaints" variant="warning" :loading="loading" />
        <KPICard icon="📆" :value="data.cases_this_month" label="Cases This Month" variant="info" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="primary" :loading="loading" />
        <KPICard icon="✅" :value="data.closed_this_month" label="Closed This Month" variant="success" :loading="loading" />
      </div>
    </section>

    <!-- Trend Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Customer Complaints Trend" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📋 Cases by Category" type="bar" :labels="categoryLabels" :datasets="categoryData" height="280px" :loading="loading" />
        <ChartCard title="🗺️ Cases by Region" type="pie" :labels="regionLabels" :datasets="regionData" height="280px" :loading="loading" />
      </div>
    </section>

    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Cases by Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
        <ChartCard title="📥 Cases by Source" type="bar" :labels="sourceLabels" :datasets="sourceData" height="280px" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'CustomerComplaintDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedRegion = ref('all')
    const regions = ref([])
    const data = ref({
      complaints: 0, cases_this_month: 0, under_investigation: 0, closed_this_month: 0,
      trend: [], by_category: [], by_region: [], by_status: [], by_source: []
    })

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'Complaints', data: data.value.trend?.map(t => t.total) || [], borderColor: '#00acc1', backgroundColor: 'rgba(0,172,193,0.1)', fill: true }])

    const categoryLabels = computed(() => data.value.by_category?.map(c => c.issue) || [])
    const categoryData = computed(() => [{ label: 'Cases', data: data.value.by_category?.map(c => c.count) || [], backgroundColor: '#00acc1' }])

    const regionLabels = computed(() => data.value.by_region?.map(r => r.region) || [])
    const regionData = computed(() => [{ data: data.value.by_region?.map(r => r.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#00acc1', '#e53935'] }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const sourceLabels = computed(() => data.value.by_source?.map(s => s.label) || [])
    const sourceData = computed(() => [{ label: 'Cases', data: data.value.by_source?.map(s => s.value) || [], backgroundColor: '#5c6bc0' }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [complaints, trend, byType] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_customer_complaint_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type')
        ])
        if (complaints.data.message) {
          data.value.complaints = complaints.data.message.complaints_received
          data.value.closed_this_month = complaints.data.message.complaints_resolved
          data.value.by_region = complaints.data.message.by_region
          data.value.by_category = complaints.data.message.recurring_issues
        }
        if (trend.data.message) data.value.trend = trend.data.message
        if (byType.data.message) data.value.by_source = byType.data.message
      } catch (e) { console.error('Failed to load customer complaint dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedRegion, regions, data, trendLabels, trendData, categoryLabels, categoryData, regionLabels, regionData, statusLabels, statusData, sourceLabels, sourceData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

