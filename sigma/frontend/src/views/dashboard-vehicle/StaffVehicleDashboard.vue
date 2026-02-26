<template>
  <div class="vehicle-dashboard">
    <header class="vehicle-dashboard__header">
      <div class="vehicle-dashboard__title-section">
        <h1 class="vehicle-dashboard__title">🚗 Staff Vehicle Dashboard</h1>
        <p class="vehicle-dashboard__subtitle">Employee personal vehicles • Parking & access management</p>
      </div>
      <div class="vehicle-dashboard__actions">
        <select v-model="selectedLocation" class="form-select">
          <option value="all">All Locations</option>
          <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Staff Vehicle KPIs -->
    <section class="vehicle-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="🅿️" :value="data.parkingOccupancy" label="Parking Occupancy %" format="percent" :variant="data.parkingOccupancy > 90 ? 'danger' : 'success'" :loading="loading" />
        <KPICard icon="🚗" :value="data.vehiclesInside" label="Staff Vehicles Inside" variant="primary" :loading="loading" />
        <KPICard icon="⏰" :value="data.pastAllowedTime" label="Past Allowed Time" variant="warning" :loading="loading" />
        <KPICard icon="🚦" :value="data.gateUsagePerHour" label="Gate Usage/Hour" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Entry Frequency & Gate Load -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Entry Frequency per Department" type="bar" :labels="deptLabels" :datasets="deptEntryData" height="300px" :loading="loading" />
        <ChartCard title="🚦 Gate Load by Staff Vehicles" type="line" :labels="hourLabels" :datasets="gateLoadData" height="300px" :loading="loading" />
      </div>
    </section>

    <!-- Parking Heatmap -->
    <section class="vehicle-dashboard__section">
      <div class="vehicle-map">
        <div class="vehicle-map__header">
          <h3>🗺️ Staff Parking Heatmap</h3>
        </div>
        <div class="parking-heatmap-container">
          <ChartCard title="" type="bar" :labels="zoneLabels" :datasets="zoneOccupancyData" height="250px" :loading="loading" />
        </div>
      </div>
    </section>

    <!-- Registered Staff Vehicles Table -->
    <section class="vehicle-dashboard__section">
      <DataTable title="📋 Registered Staff Vehicles" :columns="staffVehicleColumns" :rows="data.registeredVehicles" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'StaffVehicleDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedLocation = ref('all')
    const locations = ref(['HQ Stima Plaza', 'Likoni Road', 'Industrial Area', 'Ruaraka'])
    
    const data = ref({
      parkingOccupancy: 0, vehiclesInside: 0, pastAllowedTime: 0, gateUsagePerHour: 0,
      departmentEntries: [], gateLoadHourly: [], zoneOccupancy: [], registeredVehicles: []
    })

    const staffVehicleColumns = [
      { key: 'plate_number', label: 'Plate Number' },
      { key: 'employee_name', label: 'Employee' },
      { key: 'department', label: 'Department' },
      { key: 'employee_id', label: 'Employee ID' },
      { key: 'access_level', label: 'Access Level', type: 'badge' },
      { key: 'last_entry', label: 'Last Entry' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]

    const deptLabels = computed(() => data.value.departmentEntries?.map(d => d.department) || [])
    const deptEntryData = computed(() => [{ label: 'Entries', data: data.value.departmentEntries?.map(d => d.count) || [], backgroundColor: '#43a047' }])
    
    const hourLabels = computed(() => data.value.gateLoadHourly?.map(h => h.hour) || [])
    const gateLoadData = computed(() => [{ label: 'Vehicles', data: data.value.gateLoadHourly?.map(h => h.count) || [], borderColor: '#1976d2', fill: true, backgroundColor: 'rgba(25,118,210,0.1)' }])
    
    const zoneLabels = computed(() => data.value.zoneOccupancy?.map(z => z.zone) || [])
    const zoneOccupancyData = computed(() => [
      { label: 'Occupied', data: data.value.zoneOccupancy?.map(z => z.occupied) || [], backgroundColor: '#43a047' },
      { label: 'Available', data: data.value.zoneOccupancy?.map(z => z.available) || [], backgroundColor: '#e0e0e0' }
    ])

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_vehicle_management.api.vehicle_dashboard_api.get_staff_vehicle_dashboard', { location: selectedLocation.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load staff vehicle dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, selectedLocation, locations, data, staffVehicleColumns, deptLabels, deptEntryData, hourLabels, gateLoadData, zoneLabels, zoneOccupancyData, refreshData }
  }
}
</script>

<style src="./dashboard-vehicle.css"></style>

