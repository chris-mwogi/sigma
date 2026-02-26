<template>
  <div class="vehicle-dashboard">
    <header class="vehicle-dashboard__header">
      <div class="vehicle-dashboard__title-section">
        <h1 class="vehicle-dashboard__title">🅿️ Parking Management Dashboard</h1>
        <p class="vehicle-dashboard__subtitle">All vehicle types • Zone occupancy & violations</p>
      </div>
      <div class="vehicle-dashboard__actions">
        <select v-model="selectedLocation" class="form-select">
          <option value="all">All Locations</option>
          <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Parking KPIs -->
    <section class="vehicle-dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="🅿️" :value="data.totalCapacity" label="Total Capacity" variant="info" :loading="loading" />
        <KPICard icon="🚙" :value="data.companyOccupancy" label="Company Occupancy" variant="primary" :loading="loading" />
        <KPICard icon="🚗" :value="data.staffOccupancy" label="Staff Occupancy" variant="success" :loading="loading" />
        <KPICard icon="🚕" :value="data.visitorOccupancy" label="Visitor Occupancy" variant="warning" :loading="loading" />
        <KPICard icon="⚠️" :value="data.violations" label="Parking Violations" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Occupancy Overview -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Overall Occupancy" type="doughnut" :labels="['Occupied', 'Available']" :datasets="occupancyData" height="280px" :loading="loading" />
        <ChartCard title="🚗 Occupancy by Vehicle Type" type="bar" :labels="['Company', 'Staff', 'Visitor']" :datasets="typeOccupancyData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Zone Heatmap & Occupancy -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <div class="vehicle-map">
          <div class="vehicle-map__header">
            <h3>🗺️ Parking Lot Heatmap</h3>
            <div class="vehicle-map__legend">
              <span class="vehicle-map__legend-item"><span class="vehicle-map__legend-dot vehicle-map__legend-dot--company"></span> Company</span>
              <span class="vehicle-map__legend-item"><span class="vehicle-map__legend-dot vehicle-map__legend-dot--staff"></span> Staff</span>
              <span class="vehicle-map__legend-item"><span class="vehicle-map__legend-dot vehicle-map__legend-dot--visitor"></span> Visitor</span>
            </div>
          </div>
          <div class="parking-heatmap">
            <div v-for="(slot, idx) in parkingSlots" :key="idx" :class="['parking-slot', `parking-slot--${slot.status}`]" :title="slot.plate || 'Empty'">
              {{ slot.zone }}
            </div>
          </div>
        </div>
        <ChartCard title="📍 Occupancy per Zone" type="bar" :labels="zoneLabels" :datasets="zoneOccupancyData" height="300px" :loading="loading" />
      </div>
    </section>

    <!-- Reserved Slots -->
    <section class="vehicle-dashboard__section">
      <ChartCard title="⭐ Reserved Slot Utilization" type="bar" :labels="reservedLabels" :datasets="reservedData" height="250px" :loading="loading" />
    </section>

    <!-- Violations & Overstay -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="⚠️ Vehicles Overstaying" :columns="overstayColumns" :rows="data.overstaying" :loading="loading" />
        <DataTable title="🚫 Wrong Zone Violations" :columns="violationColumns" :rows="data.wrongZone" :loading="loading" />
      </div>
    </section>

    <!-- Unidentified Vehicles -->
    <section class="vehicle-dashboard__section">
      <DataTable title="❓ Unidentified Vehicles (No DB Match)" :columns="unidentifiedColumns" :rows="data.unidentified" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'ParkingManagementDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedLocation = ref('all')
    const locations = ref(['HQ Stima Plaza', 'Likoni Road', 'Industrial Area', 'Ruaraka'])
    
    const data = ref({
      totalCapacity: 0, companyOccupancy: 0, staffOccupancy: 0, visitorOccupancy: 0, violations: 0,
      totalOccupied: 0, totalAvailable: 0, zoneOccupancy: [], reservedUtilization: [],
      parkingSlots: [], overstaying: [], wrongZone: [], unidentified: []
    })

    const overstayColumns = [
      { key: 'plate', label: 'Plate' }, { key: 'type', label: 'Type', type: 'badge' },
      { key: 'zone', label: 'Zone' }, { key: 'entry_time', label: 'Entry Time' },
      { key: 'duration', label: 'Duration' }, { key: 'allowed', label: 'Allowed' }
    ]
    const violationColumns = [
      { key: 'plate', label: 'Plate' }, { key: 'type', label: 'Type', type: 'badge' },
      { key: 'assigned_zone', label: 'Assigned Zone' }, { key: 'actual_zone', label: 'Actual Zone' },
      { key: 'timestamp', label: 'Detected' }
    ]
    const unidentifiedColumns = [
      { key: 'plate', label: 'Plate' }, { key: 'zone', label: 'Zone' },
      { key: 'entry_time', label: 'Entry Time' }, { key: 'camera', label: 'Camera' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]

    const parkingSlots = computed(() => data.value.parkingSlots || Array(40).fill(null).map((_, i) => ({ zone: `Z${Math.floor(i/10)+1}`, status: ['empty', 'company', 'staff', 'visitor'][Math.floor(Math.random()*4)], plate: null })))
    
    const occupancyData = computed(() => [{ data: [data.value.totalOccupied, data.value.totalAvailable], backgroundColor: ['#1976d2', '#e0e0e0'] }])
    const typeOccupancyData = computed(() => [{ label: 'Vehicles', data: [data.value.companyOccupancy, data.value.staffOccupancy, data.value.visitorOccupancy], backgroundColor: ['#1976d2', '#43a047', '#fb8c00'] }])
    
    const zoneLabels = computed(() => data.value.zoneOccupancy?.map(z => z.zone) || [])
    const zoneOccupancyData = computed(() => [
      { label: 'Occupied', data: data.value.zoneOccupancy?.map(z => z.occupied) || [], backgroundColor: '#1976d2' },
      { label: 'Available', data: data.value.zoneOccupancy?.map(z => z.available) || [], backgroundColor: '#e0e0e0' }
    ])
    
    const reservedLabels = computed(() => data.value.reservedUtilization?.map(r => r.category) || [])
    const reservedData = computed(() => [
      { label: 'Used', data: data.value.reservedUtilization?.map(r => r.used) || [], backgroundColor: '#43a047' },
      { label: 'Unused', data: data.value.reservedUtilization?.map(r => r.unused) || [], backgroundColor: '#e0e0e0' }
    ])

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_vehicle_management.api.vehicle_dashboard_api.get_parking_management_dashboard', { location: selectedLocation.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load parking dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, selectedLocation, locations, data, overstayColumns, violationColumns, unidentifiedColumns, parkingSlots, occupancyData, typeOccupancyData, zoneLabels, zoneOccupancyData, reservedLabels, reservedData, refreshData }
  }
}
</script>

<style src="./dashboard-vehicle.css"></style>

