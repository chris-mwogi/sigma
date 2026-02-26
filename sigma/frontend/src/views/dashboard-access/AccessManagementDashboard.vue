<template>
  <div class="access-dashboard">
    <header class="access-dashboard__header">
      <div class="access-dashboard__title-section">
        <h1 class="access-dashboard__title">📊 Access Control Management</h1>
        <p class="access-dashboard__subtitle">Credentials • Compliance • Device Health • Analytics</p>
      </div>
      <div class="access-dashboard__actions">
        <select v-model="selectedPeriod" class="form-select">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Management KPIs -->
    <section class="access-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📊" :value="kpis.events_this_month" label="Events This Month" variant="primary" :loading="loading" />
        <KPICard icon="🎫" :value="kpis.active_credentials" label="Active Credentials" variant="success" :loading="loading" />
        <KPICard icon="⏰" :value="kpis.expiring_soon" label="Expiring Soon (30d)" variant="warning" :loading="loading" />
        <KPICard icon="🚨" :value="kpis.high_risk_events" label="High Risk Events" variant="danger" :loading="loading" />
      </div>
    </section>

    <section class="access-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="🔧" :value="kpis.device_issues" label="Device Issues" variant="warning" :loading="loading" />
        <KPICard icon="🚪" :value="kpis.total_access_points" label="Total Access Points" variant="info" :loading="loading" />
        <KPICard icon="🆘" :value="kpis.active_emergency" label="Emergency Rules" variant="danger" :loading="loading" />
        <KPICard icon="✅" :value="complianceRate" label="Compliance Rate" variant="success" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="access-dashboard__section">
      <ChartCard title="📈 Access Events Trend" type="line" :labels="trendLabels" :datasets="trendData" height="300px" :loading="loading" />
    </section>

    <section class="access-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="🏢 Access by Zone" type="bar" :labels="zoneLabels" :datasets="zoneData" height="280px" :loading="loading" />
        <ChartCard title="✅ Access by Result" type="doughnut" :labels="resultLabels" :datasets="resultData" height="280px" :loading="loading" />
      </div>
    </section>

    <section class="access-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="💳 Credential Types" type="pie" :labels="credentialLabels" :datasets="credentialData" height="280px" :loading="loading" />
        <ChartCard title="🔧 Device Health" type="pie" :labels="healthLabels" :datasets="healthData" height="280px" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'AccessManagementDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedPeriod = ref('month')
    const kpis = ref({})
    const trend = ref({ labels: [], datasets: [] })
    const byZone = ref({ labels: [], datasets: [] })
    const byResult = ref({ labels: [], datasets: [] })
    const deviceHealth = ref({ labels: [], datasets: [] })

    const complianceRate = computed(() => {
      const total = (kpis.value.events_this_month || 0)
      const issues = (kpis.value.high_risk_events || 0) + (kpis.value.device_issues || 0)
      if (total === 0) return '100%'
      return Math.round(((total - issues) / total) * 100) + '%'
    })

    const trendLabels = computed(() => trend.value.labels || [])
    const trendData = computed(() => [{ label: 'Events', data: trend.value.datasets?.[0]?.values || [], borderColor: '#3f51b5', fill: false }])
    const zoneLabels = computed(() => byZone.value.labels || [])
    const zoneData = computed(() => [{ label: 'Events', data: byZone.value.datasets?.[0]?.values || [], backgroundColor: '#3f51b5' }])
    const resultLabels = computed(() => byResult.value.labels || [])
    const resultData = computed(() => [{ data: byResult.value.datasets?.[0]?.values || [], backgroundColor: ['#4caf50', '#f44336', '#ff9800'] }])
    const healthLabels = computed(() => deviceHealth.value.labels || [])
    const healthData = computed(() => [{ data: deviceHealth.value.datasets?.[0]?.values || [], backgroundColor: ['#4caf50', '#ff9800', '#f44336'] }])
    const credentialLabels = computed(() => ['Card', 'Biometric', 'Mobile', 'PIN'])
    const credentialData = computed(() => [{ data: [45, 30, 15, 10], backgroundColor: ['#3f51b5', '#9c27b0', '#00bcd4', '#ff9800'] }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [kpiRes, trendRes, zoneRes, resultRes, healthRes] = await Promise.all([
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_management_kpis'),
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_events_trend'),
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_access_by_zone'),
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_access_by_result'),
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_device_health')
        ])
        if (kpiRes.data.message) kpis.value = kpiRes.data.message
        if (trendRes.data.message) trend.value = trendRes.data.message
        if (zoneRes.data.message) byZone.value = zoneRes.data.message
        if (resultRes.data.message) byResult.value = resultRes.data.message
        if (healthRes.data.message) deviceHealth.value = healthRes.data.message
      } catch (e) { console.error('Failed to load management dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedPeriod, kpis, complianceRate, trendLabels, trendData, zoneLabels, zoneData, resultLabels, resultData, healthLabels, healthData, credentialLabels, credentialData, fetchData }
  }
}
</script>

<style src="./dashboard-access.css"></style>

