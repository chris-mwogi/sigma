<template>
  <div class="vehicle-dashboard">
    <header class="vehicle-dashboard__header">
      <div class="vehicle-dashboard__title-section">
        <h1 class="vehicle-dashboard__title">🚨 Vehicle Security & Incident Dashboard</h1>
        <p class="vehicle-dashboard__subtitle">Corporate Security & Risk Unit • All vehicle types</p>
      </div>
      <div class="vehicle-dashboard__actions">
        <select v-model="dateRange" class="form-select">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
        <button class="btn btn--danger" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Security KPIs -->
    <section class="vehicle-dashboard__section">
      <div class="kpi-grid kpi-grid--6">
        <KPICard icon="🚧" :value="data.restrictedZoneEntries" label="Restricted Zone Entries" variant="danger" :loading="loading" />
        <KPICard icon="🌙" :value="data.nightEntries" label="Night Entries" variant="warning" :loading="loading" />
        <KPICard icon="🔗" :value="data.humanVehicleIncidents" label="Human-Vehicle Incidents" variant="danger" :loading="loading" />
        <KPICard icon="🚔" :value="data.stolenPlates" label="Stolen/Mismatched Plates" variant="danger" :loading="loading" />
        <KPICard icon="🛤️" :value="data.routeViolations" label="Route Violations" variant="warning" :loading="loading" />
        <KPICard icon="⚠️" :value="data.totalAlerts" label="Total Alerts" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Special Alerts Panel -->
    <section class="vehicle-dashboard__section">
      <AlertPanel title="🚨 Special Security Alerts" :alerts="data.specialAlerts" :loading="loading" />
    </section>

    <!-- Incident Charts -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="🚧 Restricted Zone Entries by Type" type="doughnut" :labels="zoneLabels" :datasets="zoneData" height="280px" :loading="loading" />
        <ChartCard title="🌙 Night Entry Breakdown" type="bar" :labels="nightLabels" :datasets="nightData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Route Violations & Tailgating -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="🛤️ Route Violations (Contractors/Visitors)" :columns="violationColumns" :rows="data.routeViolationsList" :loading="loading" />
        <DataTable title="🚗 Tailgating Incidents" :columns="tailgatingColumns" :rows="data.tailgatingIncidents" :loading="loading" />
      </div>
    </section>

    <!-- Incident Correlation -->
    <section class="vehicle-dashboard__section">
      <DataTable title="🔗 Human-Vehicle Incident Correlation" :columns="correlationColumns" :rows="data.incidentCorrelation" :loading="loading" />
    </section>

    <!-- Stolen/Mismatched Plates -->
    <section class="vehicle-dashboard__section">
      <DataTable title="🚔 Stolen/Mismatched Plate Detections" :columns="stolenColumns" :rows="data.stolenDetections" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable, AlertPanel } from './components'

export default {
  name: 'VehicleSecurityDashboard',
  components: { KPICard, ChartCard, DataTable, AlertPanel },
  setup() {
    const loading = ref(true)
    const dateRange = ref('today')
    const refreshInterval = ref(null)
    
    const data = ref({
      restrictedZoneEntries: 0, nightEntries: 0, humanVehicleIncidents: 0, stolenPlates: 0, routeViolations: 0, totalAlerts: 0,
      specialAlerts: [], restrictedByType: [], nightByType: [], routeViolationsList: [], tailgatingIncidents: [], incidentCorrelation: [], stolenDetections: []
    })

    const violationColumns = [
      { key: 'plate', label: 'Plate' }, { key: 'type', label: 'Type', type: 'badge' },
      { key: 'driver', label: 'Driver/Visitor' }, { key: 'violation', label: 'Violation' },
      { key: 'location', label: 'Location' }, { key: 'timestamp', label: 'Time' }
    ]
    const tailgatingColumns = [
      { key: 'lead_vehicle', label: 'Lead Vehicle' }, { key: 'follow_vehicle', label: 'Follow Vehicle' },
      { key: 'gate', label: 'Gate' }, { key: 'timestamp', label: 'Time' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]
    const correlationColumns = [
      { key: 'incident_id', label: 'Incident ID' }, { key: 'vehicle', label: 'Vehicle' },
      { key: 'person', label: 'Person' }, { key: 'type', label: 'Type' },
      { key: 'description', label: 'Description' }, { key: 'timestamp', label: 'Time' },
      { key: 'severity', label: 'Severity', type: 'badge' }
    ]
    const stolenColumns = [
      { key: 'plate', label: 'Plate' }, { key: 'detection_time', label: 'Detection Time' },
      { key: 'camera', label: 'Camera' }, { key: 'match_type', label: 'Match Type', type: 'badge' },
      { key: 'action_taken', label: 'Action Taken' }, { key: 'status', label: 'Status', type: 'badge' }
    ]

    const zoneLabels = computed(() => data.value.restrictedByType?.map(r => r.type) || [])
    const zoneData = computed(() => [{ data: data.value.restrictedByType?.map(r => r.count) || [], backgroundColor: ['#1976d2', '#43a047', '#fb8c00'] }])
    
    const nightLabels = computed(() => data.value.nightByType?.map(n => n.type) || [])
    const nightData = computed(() => [{ label: 'Entries', data: data.value.nightByType?.map(n => n.count) || [], backgroundColor: ['#1976d2', '#43a047', '#fb8c00'] }])

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_vehicle_management.api.vehicle_dashboard_api.get_vehicle_security_dashboard', { date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load security dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(() => { fetchData(); refreshInterval.value = setInterval(fetchData, 60000) })
    onUnmounted(() => { if (refreshInterval.value) clearInterval(refreshInterval.value) })

    return { loading, dateRange, data, violationColumns, tailgatingColumns, correlationColumns, stolenColumns, zoneLabels, zoneData, nightLabels, nightData, refreshData }
  }
}
</script>

<style src="./dashboard-vehicle.css"></style>

