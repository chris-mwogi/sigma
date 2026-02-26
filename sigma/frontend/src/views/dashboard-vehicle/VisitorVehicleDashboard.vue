<template>
  <div class="vehicle-dashboard">
    <header class="vehicle-dashboard__header">
      <div class="vehicle-dashboard__title-section">
        <h1 class="vehicle-dashboard__title">🟡 Visitor Vehicle Management Dashboard</h1>
        <p class="vehicle-dashboard__subtitle">Vendors, contractors & external visitors • Access approval tracking</p>
      </div>
      <div class="vehicle-dashboard__actions">
        <select v-model="dateRange" class="form-select">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Visitor Vehicle KPIs -->
    <section class="vehicle-dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="📅" :value="data.expectedToday" label="Expected Today" variant="info" :loading="loading" />
        <KPICard icon="✅" :value="data.approved" label="Approved" variant="success" :loading="loading" />
        <KPICard icon="⏳" :value="data.pendingApproval" label="Pending Host Approval" variant="warning" :loading="loading" />
        <KPICard icon="🅿️" :value="data.parkedOnsite" label="Parked Onsite" variant="primary" :loading="loading" />
        <KPICard icon="⚠️" :value="data.overstayVehicles" label="Overstay Vehicles" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--3">
        <ChartCard title="📊 Vehicles by Purpose" type="doughnut" :labels="purposeLabels" :datasets="purposeData" height="280px" :loading="loading" />
        <ChartCard title="🏢 Frequency by Vendor Company" type="bar" :labels="vendorLabels" :datasets="vendorData" height="280px" :loading="loading" />
        <ChartCard title="🏛️ By Hosting Department" type="bar" :labels="deptLabels" :datasets="deptData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Active Visitor Vehicles -->
    <section class="vehicle-dashboard__section">
      <DataTable title="🚕 Active Visitor Vehicles" :columns="activeColumns" :rows="data.activeVehicles" :loading="loading" />
    </section>

    <!-- Pre-registered & ANPR Hits -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="📋 Pre-Registered Vehicles" :columns="preregColumns" :rows="data.preRegistered" :loading="loading" />
        <DataTable title="📸 ANPR Camera Hits" :columns="anprColumns" :rows="data.anprHits" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'VisitorVehicleDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const dateRange = ref('today')
    
    const data = ref({
      expectedToday: 0, approved: 0, pendingApproval: 0, parkedOnsite: 0, overstayVehicles: 0,
      byPurpose: [], byVendor: [], byDepartment: [], activeVehicles: [], preRegistered: [], anprHits: []
    })

    const activeColumns = [
      { key: 'plate_number', label: 'Plate Number' }, { key: 'visitor_name', label: 'Visitor' },
      { key: 'company', label: 'Company' }, { key: 'purpose', label: 'Purpose' },
      { key: 'host', label: 'Host' }, { key: 'entry_time', label: 'Entry Time' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]
    const preregColumns = [
      { key: 'plate_number', label: 'Plate Number' }, { key: 'visitor_name', label: 'Visitor' },
      { key: 'company', label: 'Company' }, { key: 'expected_date', label: 'Expected Date' },
      { key: 'host', label: 'Host' }, { key: 'approval_status', label: 'Approval', type: 'badge' }
    ]
    const anprColumns = [
      { key: 'plate_number', label: 'Plate Number' }, { key: 'camera', label: 'Camera' },
      { key: 'timestamp', label: 'Timestamp' }, { key: 'match_status', label: 'Match', type: 'badge' },
      { key: 'host_responsible', label: 'Host Responsible' }
    ]

    const purposeLabels = computed(() => data.value.byPurpose?.map(p => p.purpose) || [])
    const purposeData = computed(() => [{ data: data.value.byPurpose?.map(p => p.count) || [], backgroundColor: ['#fb8c00', '#ff7043', '#ffca28', '#ffa726', '#ffb74d'] }])
    
    const vendorLabels = computed(() => data.value.byVendor?.map(v => v.vendor) || [])
    const vendorData = computed(() => [{ label: 'Visits', data: data.value.byVendor?.map(v => v.count) || [], backgroundColor: '#fb8c00' }])
    
    const deptLabels = computed(() => data.value.byDepartment?.map(d => d.department) || [])
    const deptData = computed(() => [{ label: 'Hosting', data: data.value.byDepartment?.map(d => d.count) || [], backgroundColor: '#1976d2' }])

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_vehicle_management.api.vehicle_dashboard_api.get_visitor_vehicle_dashboard', { date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load visitor vehicle dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, dateRange, data, activeColumns, preregColumns, anprColumns, purposeLabels, purposeData, vendorLabels, vendorData, deptLabels, deptData, refreshData }
  }
}
</script>

<style src="./dashboard-vehicle.css"></style>

