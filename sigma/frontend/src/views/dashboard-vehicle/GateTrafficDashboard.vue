<template>
  <div class="vehicle-dashboard">
    <header class="vehicle-dashboard__header">
      <div class="vehicle-dashboard__title-section">
        <h1 class="vehicle-dashboard__title">🔵 Unified Gate & Traffic Dashboard</h1>
        <p class="vehicle-dashboard__subtitle">Live vehicle entry/exit monitoring • Security Command Center</p>
      </div>
      <div class="vehicle-dashboard__actions">
        <select v-model="selectedGate" class="form-select">
          <option value="all">All Gates</option>
          <option v-for="gate in gates" :key="gate" :value="gate">{{ gate }}</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Live KPIs -->
    <section class="vehicle-dashboard__section">
      <div class="kpi-grid kpi-grid--7">
        <KPICard icon="🚙" :value="data.companyVehiclesOnsite" label="Company Vehicles Onsite" variant="primary" :loading="loading" />
        <KPICard icon="🚗" :value="data.staffVehiclesOnsite" label="Staff Vehicles Onsite" variant="success" :loading="loading" />
        <KPICard icon="🚕" :value="data.visitorVehiclesOnsite" label="Visitor Vehicles Onsite" variant="warning" :loading="loading" />
        <KPICard icon="📥" :value="data.entriesToday" label="Entries Today" variant="info" :loading="loading" />
        <KPICard icon="📤" :value="data.exitsToday" label="Exits Today" variant="info" :loading="loading" />
        <KPICard icon="🚫" :value="data.unauthorizedAttempts" label="Unauthorized Attempts" variant="danger" :loading="loading" />
        <KPICard icon="⏳" :value="data.awaitingApproval" label="Awaiting Approval" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Live Entry/Exit Feed -->
    <section class="vehicle-dashboard__section">
      <div class="live-feed">
        <div class="live-feed__header">
          <h3>📡 Live Entry/Exit Feed</h3>
          <span class="live-feed__indicator">LIVE</span>
        </div>
        <div class="live-feed__body">
          <DataTable :columns="feedColumns" :rows="data.liveFeed" :loading="loading" :show-header="true" />
        </div>
      </div>
    </section>

    <!-- Vehicle Segmentation & Charts -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <div class="vehicle-map">
          <div class="vehicle-map__header">
            <h3>🗺️ Vehicle Segmentation Map</h3>
            <div class="vehicle-map__legend">
              <span class="vehicle-map__legend-item"><span class="vehicle-map__legend-dot vehicle-map__legend-dot--company"></span> Company</span>
              <span class="vehicle-map__legend-item"><span class="vehicle-map__legend-dot vehicle-map__legend-dot--staff"></span> Staff</span>
              <span class="vehicle-map__legend-item"><span class="vehicle-map__legend-dot vehicle-map__legend-dot--visitor"></span> Visitor</span>
            </div>
          </div>
          <div class="vehicle-map__canvas">
            <ChartCard title="" type="doughnut" :labels="['Company', 'Staff', 'Visitor']" :datasets="segmentationData" height="280px" :loading="loading" />
          </div>
        </div>
        <ChartCard title="📊 Hourly Traffic Volume" type="bar" :labels="hourlyLabels" :datasets="hourlyTrafficData" height="320px" :loading="loading" />
      </div>
    </section>

    <!-- Gate Load Distribution -->
    <section class="vehicle-dashboard__section">
      <ChartCard title="🚦 Traffic by Gate" type="bar" :labels="gateLabels" :datasets="gateTrafficData" height="300px" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'GateTrafficDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedGate = ref('all')
    const gates = ref(['Main Gate', 'Staff Gate', 'Service Gate', 'Emergency Gate'])
    const refreshInterval = ref(null)
    
    const data = ref({
      companyVehiclesOnsite: 0, staffVehiclesOnsite: 0, visitorVehiclesOnsite: 0,
      entriesToday: 0, exitsToday: 0, unauthorizedAttempts: 0, awaitingApproval: 0,
      liveFeed: [], hourlyTraffic: [], gateTraffic: []
    })

    const feedColumns = [
      { key: 'plate_number', label: 'Plate Number' },
      { key: 'category', label: 'Category', type: 'badge' },
      { key: 'driver', label: 'Driver' },
      { key: 'gate', label: 'Gate' },
      { key: 'timestamp', label: 'Time' },
      { key: 'zone', label: 'Zone' },
      { key: 'alert', label: 'Alert', type: 'badge' }
    ]

    const segmentationData = computed(() => [{
      data: [data.value.companyVehiclesOnsite, data.value.staffVehiclesOnsite, data.value.visitorVehiclesOnsite],
      backgroundColor: ['#1976d2', '#43a047', '#fb8c00']
    }])

    const hourlyLabels = computed(() => data.value.hourlyTraffic?.map(h => h.hour) || [])
    const hourlyTrafficData = computed(() => [
      { label: 'Entries', data: data.value.hourlyTraffic?.map(h => h.entries) || [], backgroundColor: '#43a047' },
      { label: 'Exits', data: data.value.hourlyTraffic?.map(h => h.exits) || [], backgroundColor: '#e53935' }
    ])

    const gateLabels = computed(() => data.value.gateTraffic?.map(g => g.gate) || [])
    const gateTrafficData = computed(() => [
      { label: 'Company', data: data.value.gateTraffic?.map(g => g.company) || [], backgroundColor: '#1976d2' },
      { label: 'Staff', data: data.value.gateTraffic?.map(g => g.staff) || [], backgroundColor: '#43a047' },
      { label: 'Visitor', data: data.value.gateTraffic?.map(g => g.visitor) || [], backgroundColor: '#fb8c00' }
    ])

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_vehicle_management.api.vehicle_dashboard_api.get_gate_traffic_dashboard', { gate: selectedGate.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load gate traffic dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()

    onMounted(() => {
      fetchData()
      refreshInterval.value = setInterval(fetchData, 30000) // Refresh every 30 seconds
    })
    onUnmounted(() => { if (refreshInterval.value) clearInterval(refreshInterval.value) })

    return { loading, selectedGate, gates, data, feedColumns, segmentationData, hourlyLabels, hourlyTrafficData, gateLabels, gateTrafficData, refreshData }
  }
}
</script>

<style src="./dashboard-vehicle.css"></style>

