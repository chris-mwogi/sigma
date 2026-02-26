<template>
  <div class="dashboard gatehouse-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">🚪 Gatehouse / Access Control Dashboard</h1>
        <p class="dashboard__subtitle">Visitor and vehicle access monitoring</p>
      </div>
      <div class="dashboard__actions">
        <div class="realtime-indicator">
          <span class="realtime-indicator__dot"></span>
          <span>Live</span>
        </div>
        <select v-model="selectedGate" class="form-select">
          <option value="">All Gates</option>
          <option v-for="g in gates" :key="g" :value="g">{{ g }}</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Access KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--6">
        <KPICard icon="👥" :value="data.visitorsToday" label="Visitors Today" variant="primary" :loading="loading" />
        <KPICard icon="🚗" :value="data.vehiclesToday" label="Vehicles Today" variant="info" :loading="loading" />
        <KPICard icon="🚫" :value="data.unauthorizedEntries" label="Unauthorized Entries" variant="danger" :loading="loading" />
        <KPICard icon="⏱️" :value="data.avgProcessingTime" label="Avg Processing (sec)" variant="info" :loading="loading" />
        <KPICard icon="👤" :value="data.currentVisitors" label="On-Site Now" variant="success" :loading="loading" />
        <KPICard icon="⚠️" :value="data.idExceptions" label="ID Exceptions" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Real-time Monitor -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <AlertPanel title="📋 Gate Queue Status" icon="🚪" :alerts="gateQueueAlerts" :loading="loading" />
        <AlertPanel title="⚠️ Access Denials" icon="🚫" :alerts="denialAlerts" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Hourly Traffic Flow" type="line" :labels="trafficFlow.labels" :datasets="trafficFlow.datasets" :loading="loading" />
        <ChartCard title="🥧 Visitor Types" type="doughnut" :labels="visitorTypes.labels" :datasets="visitorTypes.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Visitor & Vehicle Logs -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="👥 Recent Visitors" :columns="visitorColumns" :rows="data.recentVisitors" :loading="loading" />
        <DataTable title="🚗 Vehicle Log" :columns="vehicleColumns" :rows="data.vehicleLog" :loading="loading" />
      </div>
    </section>

    <!-- Asset Movement -->
    <section class="dashboard__section">
      <DataTable title="📦 Asset Movement Approvals" :columns="assetColumns" :rows="data.assetMovements" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable, AlertPanel } from './components'

export default {
  name: 'GatehouseDashboard',
  components: { KPICard, ChartCard, DataTable, AlertPanel },
  setup() {
    const loading = ref(true)
    let refreshInterval = null
    const selectedGate = ref('')
    const gates = ref([])
    const data = ref({
      visitorsToday: 0, vehiclesToday: 0, unauthorizedEntries: 0, avgProcessingTime: 0,
      currentVisitors: 0, idExceptions: 0, gateQueue: [], denials: [],
      recentVisitors: [], vehicleLog: [], assetMovements: [], trafficData: [], visitorTypeData: []
    })

    const visitorColumns = [
      { key: 'name', label: 'Name' }, { key: 'company', label: 'Company' },
      { key: 'host', label: 'Host' }, { key: 'check_in', label: 'Check-In' }, { key: 'status', label: 'Status', type: 'badge' }
    ]
    const vehicleColumns = [
      { key: 'plate', label: 'Plate #' }, { key: 'type', label: 'Type' },
      { key: 'driver', label: 'Driver' }, { key: 'time', label: 'Time' }, { key: 'direction', label: 'Direction', type: 'badge' }
    ]
    const assetColumns = [
      { key: 'asset', label: 'Asset' }, { key: 'requestor', label: 'Requestor' },
      { key: 'destination', label: 'Destination' }, { key: 'approval', label: 'Approval', type: 'badge' }, { key: 'time', label: 'Time' }
    ]

    const gateQueueAlerts = computed(() => data.value.gateQueue?.map(g => ({
      title: g.gate, description: `${g.queue_length} in queue`, severity: g.queue_length > 10 ? 'high' : 'low',
      time: new Date()
    })) || [])
    const denialAlerts = computed(() => data.value.denials?.map(d => ({
      title: d.visitor, description: d.reason, severity: 'medium', location: d.gate, time: d.time
    })) || [])

    const trafficFlow = computed(() => ({
      labels: data.value.trafficData?.map(t => t.hour) || [],
      datasets: [
        { label: 'Entries', data: data.value.trafficData?.map(t => t.entries) || [] },
        { label: 'Exits', data: data.value.trafficData?.map(t => t.exits) || [] }
      ]
    }))
    const visitorTypes = computed(() => ({
      labels: data.value.visitorTypeData?.map(v => v.type) || [],
      datasets: [{ data: data.value.visitorTypeData?.map(v => v.count) || [] }]
    }))

    const fetchData = async () => {
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_gatehouse_dashboard', { gate: selectedGate.value })
        if (res.data.message) {
          data.value = res.data.message
          gates.value = res.data.message.gateList || []
        }
      } catch (e) { console.error('Failed to load gatehouse dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => { loading.value = true; fetchData() }

    onMounted(() => {
      fetchData()
      refreshInterval = setInterval(fetchData, 30000)
    })
    onUnmounted(() => { if (refreshInterval) clearInterval(refreshInterval) })

    return { loading, selectedGate, gates, data, visitorColumns, vehicleColumns, assetColumns, gateQueueAlerts, denialAlerts, trafficFlow, visitorTypes, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>

