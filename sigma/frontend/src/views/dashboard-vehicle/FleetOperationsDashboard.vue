<template>
  <div class="vehicle-dashboard">
    <header class="vehicle-dashboard__header">
      <div class="vehicle-dashboard__title-section">
        <h1 class="vehicle-dashboard__title">🛣️ Company Fleet Operations Dashboard</h1>
        <p class="vehicle-dashboard__subtitle">Official company vehicles • Real-time fleet tracking</p>
      </div>
      <div class="vehicle-dashboard__actions">
        <select v-model="selectedDepartment" class="form-select">
          <option value="all">All Departments</option>
          <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Fleet KPIs -->
    <section class="vehicle-dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="🚙" :value="data.activeOnRoad" label="Active on Road" variant="success" :loading="loading" />
        <KPICard icon="🅿️" :value="data.parkedAtYards" label="Parked at Yards" variant="info" :loading="loading" />
        <KPICard icon="🔧" :value="data.inMaintenance" label="In Maintenance" variant="warning" :loading="loading" />
        <KPICard icon="❌" :value="data.unavailable" label="Unavailable (Breakdown)" variant="danger" :loading="loading" />
        <KPICard icon="👨‍✈️" :value="data.activeDrivers" label="Active Drivers Today" variant="primary" :loading="loading" />
      </div>
    </section>

    <!-- GPS Map & Engine Stats -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <div class="vehicle-map">
          <div class="vehicle-map__header">
            <h3>📍 Live GPS Fleet Map</h3>
          </div>
          <div class="vehicle-map__canvas" id="fleet-map">
            <span>GPS Map Integration</span>
          </div>
        </div>
        <ChartCard title="⏱️ Engine Hours by Vehicle" type="bar" :labels="engineHoursLabels" :datasets="engineHoursData" height="320px" :loading="loading" />
      </div>
    </section>

    <!-- Fuel & Route Analytics -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="⛽ Fuel Usage (Liters)" type="line" :labels="fuelLabels" :datasets="fuelData" height="300px" :loading="loading" />
        <ChartCard title="🛤️ Route Deviations" type="bar" :labels="deviationLabels" :datasets="deviationData" height="300px" :loading="loading" />
      </div>
    </section>

    <!-- Work Orders & Driver Behavior -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="📋 Active Work Order Assignments" :columns="workOrderColumns" :rows="data.workOrders" :loading="loading" />
        <ChartCard title="👨‍✈️ Driver Behavior Analytics" type="radar" :labels="behaviorLabels" :datasets="behaviorData" height="320px" :loading="loading" />
      </div>
    </section>

    <!-- Fleet Inventory -->
    <section class="vehicle-dashboard__section">
      <DataTable title="🚗 Fleet Inventory" :columns="fleetColumns" :rows="data.fleetInventory" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'FleetOperationsDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedDepartment = ref('all')
    const departments = ref(['Operations', 'Engineering', 'Corporate', 'Regional Offices'])
    
    const data = ref({
      activeOnRoad: 0, parkedAtYards: 0, inMaintenance: 0, unavailable: 0, activeDrivers: 0,
      engineHours: [], fuelUsage: [], routeDeviations: [], workOrders: [], driverBehavior: {}, fleetInventory: []
    })

    const workOrderColumns = [
      { key: 'vehicle', label: 'Vehicle' }, { key: 'driver', label: 'Driver' },
      { key: 'task', label: 'Task' }, { key: 'location', label: 'Location' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]
    const fleetColumns = [
      { key: 'plate', label: 'Plate No.' }, { key: 'make_model', label: 'Make/Model' },
      { key: 'department', label: 'Department' }, { key: 'assigned_driver', label: 'Assigned Driver' },
      { key: 'status', label: 'Status', type: 'badge' }, { key: 'last_location', label: 'Last Location' }
    ]

    const engineHoursLabels = computed(() => data.value.engineHours?.map(e => e.vehicle) || [])
    const engineHoursData = computed(() => [{ label: 'Hours', data: data.value.engineHours?.map(e => e.hours) || [], backgroundColor: '#1976d2' }])
    
    const fuelLabels = computed(() => data.value.fuelUsage?.map(f => f.date) || [])
    const fuelData = computed(() => [{ label: 'Fuel (L)', data: data.value.fuelUsage?.map(f => f.liters) || [], borderColor: '#fb8c00' }])
    
    const deviationLabels = computed(() => data.value.routeDeviations?.map(r => r.vehicle) || [])
    const deviationData = computed(() => [{ label: 'Deviations', data: data.value.routeDeviations?.map(r => r.count) || [], backgroundColor: '#e53935' }])
    
    const behaviorLabels = ['Speed', 'Braking', 'Acceleration', 'Idling', 'Fuel Efficiency']
    const behaviorData = computed(() => [{ label: 'Score', data: Object.values(data.value.driverBehavior || {}), backgroundColor: 'rgba(25,118,210,0.3)', borderColor: '#1976d2' }])

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_vehicle_management.api.vehicle_dashboard_api.get_fleet_operations_dashboard', { department: selectedDepartment.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load fleet operations dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, selectedDepartment, departments, data, workOrderColumns, fleetColumns, engineHoursLabels, engineHoursData, fuelLabels, fuelData, deviationLabels, deviationData, behaviorLabels, behaviorData, refreshData }
  }
}
</script>

<style src="./dashboard-vehicle.css"></style>

