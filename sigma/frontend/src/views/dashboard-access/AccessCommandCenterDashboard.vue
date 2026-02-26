<template>
  <div class="access-dashboard">
    <header class="access-dashboard__header">
      <div class="access-dashboard__title-section">
        <h1 class="access-dashboard__title">🎛️ Access Control Command Center</h1>
        <p class="access-dashboard__subtitle">Real-time Monitoring • Live Event Feed • System Health</p>
      </div>
      <div class="access-dashboard__actions">
        <select v-model="selectedZone" class="form-select">
          <option value="all">All Zones</option>
          <option v-for="zone in zones" :key="zone" :value="zone">{{ zone }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Command Center KPIs -->
    <section class="access-dashboard__section">
      <div class="kpi-grid kpi-grid--8">
        <KPICard icon="👥" :value="kpis.employees_onsite" label="Employees Onsite" variant="primary" :loading="loading" />
        <KPICard icon="🎫" :value="kpis.visitors_onsite" label="Visitors Onsite" variant="info" :loading="loading" />
        <KPICard icon="🚧" :value="kpis.contractors_onsite" label="Contractors" variant="warning" :loading="loading" />
        <KPICard icon="🚗" :value="kpis.vehicles_in_parking" label="Vehicles" variant="success" :loading="loading" />
        <KPICard icon="🚨" :value="kpis.active_alarms" label="Active Alarms" variant="danger" :loading="loading" />
        <KPICard icon="⚠️" :value="kpis.open_incidents" label="Open Incidents" variant="warning" :loading="loading" />
        <KPICard icon="📊" :value="kpis.events_today" label="Events Today" variant="secondary" :loading="loading" />
        <KPICard icon="🚫" :value="kpis.denied_today" label="Denied Today" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Events Trend Chart -->
    <section class="access-dashboard__section">
      <ChartCard title="📈 Access Events Trend (7 Days)" type="line" :labels="trendLabels" :datasets="trendData" height="300px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="access-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="✅ Access by Result" type="pie" :labels="resultLabels" :datasets="resultData" height="280px" :loading="loading" />
        <ChartCard title="🏢 Access by Zone" type="bar" :labels="zoneLabels" :datasets="zoneData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Live Events Feed -->
    <section class="access-dashboard__section">
      <div class="live-feed">
        <div class="live-feed__header">
          <h3><span class="live-indicator"></span> Live Access Events</h3>
          <span class="text-muted">Last 20 events</span>
        </div>
        <div class="live-feed__body">
          <div v-if="loading" class="text-center p-3">Loading...</div>
          <div v-else-if="recentEvents.length === 0" class="text-center p-3 text-muted">No recent events</div>
          <div v-else v-for="event in recentEvents" :key="event.name" class="event-row">
            <div class="event-row__time">{{ formatTime(event.event_time) }}</div>
            <div class="event-row__icon">{{ event.result === 'Granted' ? '✅' : '🚫' }}</div>
            <div class="event-row__content">
              <div class="event-row__title">{{ event.person_name || event.holder_type || 'Unknown' }}</div>
              <div class="event-row__subtitle">{{ event.access_point_name || event.access_point }} • {{ event.zone || 'N/A' }}</div>
            </div>
            <span :class="['badge', event.result === 'Granted' ? 'badge--granted' : 'badge--denied']">{{ event.result }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'AccessCommandCenterDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedZone = ref('all')
    const zones = ref(['Main Entrance', 'Parking', 'Building A', 'Building B', 'Warehouse'])
    const kpis = ref({})
    const recentEvents = ref([])
    const trend = ref({ labels: [], datasets: [] })
    const byResult = ref({ labels: [], datasets: [] })
    const byZone = ref({ labels: [], datasets: [] })

    const trendLabels = computed(() => trend.value.labels || [])
    const trendData = computed(() => [{ label: 'Events', data: trend.value.datasets?.[0]?.values || [], borderColor: '#3f51b5', fill: false }])
    const resultLabels = computed(() => byResult.value.labels || [])
    const resultData = computed(() => [{ data: byResult.value.datasets?.[0]?.values || [], backgroundColor: ['#4caf50', '#f44336', '#ff9800', '#2196f3'] }])
    const zoneLabels = computed(() => byZone.value.labels || [])
    const zoneData = computed(() => [{ label: 'Events', data: byZone.value.datasets?.[0]?.values || [], backgroundColor: '#3f51b5' }])

    const formatTime = t => t ? new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'

    const fetchData = async () => {
      loading.value = true
      try {
        const [kpiRes, eventsRes, trendRes, resultRes, zoneRes] = await Promise.all([
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_command_center_kpis'),
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_recent_events', { limit: 20 }),
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_events_trend'),
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_access_by_result'),
          api.post('/api/method/sigma.sigma_access_control.api.dashboard_api.get_access_by_zone')
        ])
        if (kpiRes.data.message) kpis.value = kpiRes.data.message
        if (eventsRes.data.message) recentEvents.value = eventsRes.data.message
        if (trendRes.data.message) trend.value = trendRes.data.message
        if (resultRes.data.message) byResult.value = resultRes.data.message
        if (zoneRes.data.message) byZone.value = zoneRes.data.message
      } catch (e) { console.error('Failed to load command center data:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedZone, zones, kpis, recentEvents, trendLabels, trendData, resultLabels, resultData, zoneLabels, zoneData, formatTime, fetchData }
  }
}
</script>

<style src="./dashboard-access.css"></style>

