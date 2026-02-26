<template>
  <div class="vehicle-dashboard">
    <header class="vehicle-dashboard__header">
      <div class="vehicle-dashboard__title-section">
        <h1 class="vehicle-dashboard__title">⚙️ Vehicle Maintenance & Health Dashboard</h1>
        <p class="vehicle-dashboard__subtitle">Company fleet maintenance tracking • Preventive maintenance</p>
      </div>
      <div class="vehicle-dashboard__actions">
        <select v-model="selectedDepartment" class="form-select">
          <option value="all">All Departments</option>
          <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Maintenance KPIs -->
    <section class="vehicle-dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="🔧" :value="data.dueForService" label="Due for Service" variant="warning" :loading="loading" />
        <KPICard icon="⛽" :value="data.fuelCostPerVehicle" label="Avg Fuel Cost/Vehicle" format="currency" variant="info" :loading="loading" />
        <KPICard icon="💰" :value="data.maintenanceCost" label="Maintenance Cost (MTD)" format="currency" variant="primary" :loading="loading" />
        <KPICard icon="🔴" :value="data.faultCodeAlerts" label="OBD Fault Alerts" variant="danger" :loading="loading" />
        <KPICard icon="🔋" :value="data.batteryIssues" label="Battery Health Issues" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Service Schedule & Costs -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="📅 Vehicles Due for Service" :columns="serviceColumns" :rows="data.serviceDue" :loading="loading" />
        <ChartCard title="💰 Maintenance Cost by Department" type="bar" :labels="deptCostLabels" :datasets="deptCostData" height="300px" :loading="loading" />
      </div>
    </section>

    <!-- Fuel Analysis -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="⛽ Fuel Consumption Trend" type="line" :labels="fuelTrendLabels" :datasets="fuelTrendData" height="280px" :loading="loading" />
        <ChartCard title="🚗 Fuel Cost per Vehicle" type="bar" :labels="vehicleFuelLabels" :datasets="vehicleFuelData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Fault Codes & Issues -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="🔴 Active Fault Code Alerts" :columns="faultColumns" :rows="data.faultCodes" :loading="loading" />
        <DataTable title="🔋 Battery Health Report" :columns="batteryColumns" :rows="data.batteryReport" :loading="loading" />
      </div>
    </section>

    <!-- Maintenance History -->
    <section class="vehicle-dashboard__section">
      <DataTable title="📋 Recent Maintenance History" :columns="historyColumns" :rows="data.maintenanceHistory" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'VehicleMaintenanceDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedDepartment = ref('all')
    const departments = ref(['Operations', 'Engineering', 'Corporate', 'Regional'])
    
    const data = ref({
      dueForService: 0, fuelCostPerVehicle: 0, maintenanceCost: 0, faultCodeAlerts: 0, batteryIssues: 0,
      serviceDue: [], departmentCosts: [], fuelTrend: [], vehicleFuel: [], faultCodes: [], batteryReport: [], maintenanceHistory: []
    })

    const serviceColumns = [
      { key: 'vehicle', label: 'Vehicle' }, { key: 'last_service', label: 'Last Service' },
      { key: 'next_due', label: 'Next Due' }, { key: 'mileage', label: 'Mileage' },
      { key: 'service_type', label: 'Service Type' }, { key: 'priority', label: 'Priority', type: 'badge' }
    ]
    const faultColumns = [
      { key: 'vehicle', label: 'Vehicle' }, { key: 'code', label: 'Fault Code' },
      { key: 'description', label: 'Description' }, { key: 'severity', label: 'Severity', type: 'badge' },
      { key: 'detected', label: 'Detected' }
    ]
    const batteryColumns = [
      { key: 'vehicle', label: 'Vehicle' }, { key: 'voltage', label: 'Voltage' },
      { key: 'health', label: 'Health %', type: 'number' }, { key: 'age_months', label: 'Age (Months)' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]
    const historyColumns = [
      { key: 'vehicle', label: 'Vehicle' }, { key: 'date', label: 'Date' },
      { key: 'service_type', label: 'Service Type' }, { key: 'cost', label: 'Cost', type: 'currency' },
      { key: 'vendor', label: 'Vendor' }, { key: 'status', label: 'Status', type: 'badge' }
    ]

    const deptCostLabels = computed(() => data.value.departmentCosts?.map(d => d.department) || [])
    const deptCostData = computed(() => [{ label: 'Cost (KES)', data: data.value.departmentCosts?.map(d => d.cost) || [], backgroundColor: '#1976d2' }])
    
    const fuelTrendLabels = computed(() => data.value.fuelTrend?.map(f => f.month) || [])
    const fuelTrendData = computed(() => [{ label: 'Liters', data: data.value.fuelTrend?.map(f => f.liters) || [], borderColor: '#fb8c00', fill: true, backgroundColor: 'rgba(251,140,0,0.1)' }])
    
    const vehicleFuelLabels = computed(() => data.value.vehicleFuel?.map(v => v.vehicle) || [])
    const vehicleFuelData = computed(() => [{ label: 'Cost (KES)', data: data.value.vehicleFuel?.map(v => v.cost) || [], backgroundColor: '#43a047' }])

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_vehicle_management.api.vehicle_dashboard_api.get_vehicle_maintenance_dashboard', { department: selectedDepartment.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load maintenance dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, selectedDepartment, departments, data, serviceColumns, faultColumns, batteryColumns, historyColumns, deptCostLabels, deptCostData, fuelTrendLabels, fuelTrendData, vehicleFuelLabels, vehicleFuelData, refreshData }
  }
}
</script>

<style src="./dashboard-vehicle.css"></style>

