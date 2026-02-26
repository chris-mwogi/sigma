<template>
  <div class="dashboard soc-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">🎯 Security Operations Center (SOC)</h1>
        <p class="dashboard__subtitle">Real-time monitoring of security operations</p>
      </div>
      <div class="dashboard__actions">
        <div class="realtime-indicator">
          <span class="realtime-indicator__dot"></span>
          <span>Live Updates</span>
        </div>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Real-time KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--6">
        <KPICard icon="👮" :value="data.guardsOnDuty" label="Guards on Duty Now" variant="success" :loading="loading" />
        <KPICard icon="🚫" :value="data.unmannedPosts" label="Posts Not Manned" variant="danger" :loading="loading" />
        <KPICard icon="🚶" :value="data.patrolsInProgress" label="Patrols In Progress" variant="info" :loading="loading" />
        <KPICard icon="✅" :value="data.patrolCompletion" label="Patrol Completion %" format="percent" :variant="data.patrolCompletion >= 80 ? 'success' : 'warning'" :loading="loading" />
        <KPICard icon="⏰" :value="data.lateCheckIns" label="Late Check-ins Today" variant="warning" :loading="loading" />
        <KPICard icon="🔴" :value="data.activeIncidents" label="Active Incidents" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Real-time Panels -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--3">
        <AlertPanel title="🚨 Emergency Alerts" icon="🚨" :alerts="data.emergencyAlerts" :loading="loading" @alert-click="handleAlertClick" />
        <AlertPanel title="📋 Live Incident Feed" icon="⚠️" :alerts="data.liveIncidents" :loading="loading" @alert-click="handleIncidentClick" />
        <AlertPanel title="🔄 Shift Changes" icon="👥" :alerts="data.shiftChanges" :loading="loading" />
      </div>
    </section>

    <!-- Charts Row -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Patrol Status (Real-time)" type="doughnut" :labels="patrolStatus.labels" :datasets="patrolStatus.datasets" :loading="loading" />
        <ChartCard title="📈 Hourly Activity" type="line" :labels="hourlyActivity.labels" :datasets="hourlyActivity.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Guard & Post Status -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="👮 Guard Status Overview" :columns="guardColumns" :rows="data.guardStatus" :loading="loading" />
        <DataTable title="🏢 Unmanned Post Alerts" :columns="postColumns" :rows="data.unmannedPostsList" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable, AlertPanel } from './components'

export default {
  name: 'SOCDashboard',
  components: { KPICard, ChartCard, DataTable, AlertPanel },
  setup() {
    const loading = ref(true)
    let refreshInterval = null
    const data = ref({
      guardsOnDuty: 0, unmannedPosts: 0, patrolsInProgress: 0, patrolCompletion: 0,
      lateCheckIns: 0, activeIncidents: 0, emergencyAlerts: [], liveIncidents: [],
      shiftChanges: [], guardStatus: [], unmannedPostsList: [], patrolStatusData: [], hourlyData: []
    })

    const guardColumns = [
      { key: 'guard', label: 'Guard' },
      { key: 'post', label: 'Post' },
      { key: 'status', label: 'Status', type: 'badge' },
      { key: 'last_seen', label: 'Last Seen' }
    ]

    const postColumns = [
      { key: 'post', label: 'Post' },
      { key: 'location', label: 'Location' },
      { key: 'unmanned_since', label: 'Unmanned Since' },
      { key: 'priority', label: 'Priority', type: 'badge' }
    ]

    const patrolStatus = computed(() => ({
      labels: data.value.patrolStatusData?.map(s => s.status) || [],
      datasets: [{ data: data.value.patrolStatusData?.map(s => s.count) || [] }]
    }))

    const hourlyActivity = computed(() => ({
      labels: data.value.hourlyData?.map(h => h.hour) || [],
      datasets: [
        { label: 'Check-ins', data: data.value.hourlyData?.map(h => h.checkins) || [] },
        { label: 'Incidents', data: data.value.hourlyData?.map(h => h.incidents) || [] }
      ]
    }))

    const fetchData = async () => {
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_soc_dashboard')
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load SOC dashboard:', e) }
      finally { loading.value = false }
    }

    const handleAlertClick = (alert) => console.log('Alert clicked:', alert)
    const handleIncidentClick = (incident) => console.log('Incident clicked:', incident)
    const refreshData = () => { loading.value = true; fetchData() }

    onMounted(() => {
      fetchData()
      refreshInterval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    })
    onUnmounted(() => { if (refreshInterval) clearInterval(refreshInterval) })

    return { loading, data, guardColumns, postColumns, patrolStatus, hourlyActivity, handleAlertClick, handleIncidentClick, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>

