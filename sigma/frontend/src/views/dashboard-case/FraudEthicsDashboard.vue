<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">🚨 Fraud & Ethics Dashboard</h1>
        <p class="case-dashboard__subtitle">ACFE Standards • Fraud Detection & Ethics Monitoring</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedRegion" class="form-select">
          <option value="all">All Regions</option>
          <option v-for="region in regions" :key="region" :value="region">{{ region }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Fraud KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="🚨" :value="data.fraud_cases" label="Fraud Cases" variant="danger" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_severity" label="High Severity" variant="danger" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="warning" :loading="loading" />
        <KPICard icon="📆" :value="data.cases_this_month" label="Cases This Month" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Fraud Trend Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Fraud Cases Trend" type="line" :labels="trendLabels" :datasets="trendData" height="320px" :loading="loading" />
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
        <ChartCard title="📥 Cases by Source" type="doughnut" :labels="sourceLabels" :datasets="sourceData" height="280px" :loading="loading" />
        <ChartCard title="📊 Cases by Status" type="bar" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'FraudEthicsDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedRegion = ref('all')
    const regions = ref([])
    const data = ref({
      fraud_cases: 0, high_severity: 0, under_investigation: 0, cases_this_month: 0,
      trend: [], by_category: [], by_region: [], by_source: [], by_status: []
    })

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'Fraud Cases', data: data.value.trend?.map(t => t.total) || [], borderColor: '#e53935', backgroundColor: 'rgba(229,57,53,0.1)', fill: true }])

    const categoryLabels = computed(() => data.value.by_category?.map(c => c.label) || [])
    const categoryData = computed(() => [{ label: 'Cases', data: data.value.by_category?.map(c => c.value) || [], backgroundColor: '#e53935' }])

    const regionLabels = computed(() => data.value.by_region?.map(r => r.region) || [])
    const regionData = computed(() => [{ data: data.value.by_region?.map(r => r.count) || [], backgroundColor: ['#e53935', '#fb8c00', '#fbc02d', '#43a047', '#00acc1'] }])

    const sourceLabels = computed(() => data.value.by_source?.map(s => s.label) || [])
    const sourceData = computed(() => [{ data: data.value.by_source?.map(s => s.value) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#00acc1'] }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ label: 'Cases', data: data.value.by_status?.map(s => s.count) || [], backgroundColor: '#5c6bc0' }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [fraud, trend, byType] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_fraud_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' }),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_case_distribution_by_type')
        ])
        if (fraud.data.message) {
          data.value.fraud_cases = fraud.data.message.total_fraud_cases
          data.value.by_region = fraud.data.message.fraud_by_region
          data.value.by_category = fraud.data.message.fraud_schemes
        }
        if (trend.data.message) data.value.trend = trend.data.message
        if (byType.data.message) data.value.by_source = byType.data.message
      } catch (e) { console.error('Failed to load fraud dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedRegion, regions, data, trendLabels, trendData, categoryLabels, categoryData, regionLabels, regionData, sourceLabels, sourceData, statusLabels, statusData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

