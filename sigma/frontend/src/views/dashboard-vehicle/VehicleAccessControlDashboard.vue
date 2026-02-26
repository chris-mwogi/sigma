<template>
  <div class="vehicle-dashboard">
    <header class="vehicle-dashboard__header">
      <div class="vehicle-dashboard__title-section">
        <h1 class="vehicle-dashboard__title">🔐 Vehicle Access Control Dashboard</h1>
        <p class="vehicle-dashboard__subtitle">ISO 27001 & ISO 18788 Compliant • All vehicle categories</p>
      </div>
      <div class="vehicle-dashboard__actions">
        <select v-model="vehicleType" class="form-select">
          <option value="all">All Types</option>
          <option value="company">Company</option>
          <option value="staff">Staff</option>
          <option value="visitor">Visitor</option>
        </select>
        <select v-model="dateRange" class="form-select">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Access Control KPIs -->
    <section class="vehicle-dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="✅" :value="data.successfulEntries" label="Successful Entries" variant="success" :loading="loading" />
        <KPICard icon="🚫" :value="data.deniedEntries" label="Denied Entries" variant="danger" :loading="loading" />
        <KPICard icon="⚠️" :value="data.suspiciousAttempts" label="Suspicious Attempts" variant="warning" :loading="loading" />
        <KPICard icon="📸" :value="data.anprMismatches" label="ANPR Mismatches" variant="danger" :loading="loading" />
        <KPICard icon="⏰" :value="data.expiredPasses" label="Expired/Unauthorized" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Access by Vehicle Type -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--3">
        <div class="access-breakdown-card">
          <h4>🚙 Company Vehicles</h4>
          <p class="access-note">Fleet authorization based</p>
          <div class="access-stats">
            <span class="stat success">{{ data.companyAccess?.allowed || 0 }} Allowed</span>
            <span class="stat danger">{{ data.companyAccess?.denied || 0 }} Denied</span>
          </div>
        </div>
        <div class="access-breakdown-card">
          <h4>🚗 Staff Vehicles</h4>
          <p class="access-note">AD-linked access level</p>
          <div class="access-stats">
            <span class="stat success">{{ data.staffAccess?.allowed || 0 }} Allowed</span>
            <span class="stat danger">{{ data.staffAccess?.denied || 0 }} Denied</span>
          </div>
        </div>
        <div class="access-breakdown-card">
          <h4>🚕 Visitor Vehicles</h4>
          <p class="access-note">Pre-approval + temp gate pass</p>
          <div class="access-stats">
            <span class="stat success">{{ data.visitorAccess?.allowed || 0 }} Allowed</span>
            <span class="stat danger">{{ data.visitorAccess?.denied || 0 }} Denied</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Charts -->
    <section class="vehicle-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Access Trends by Type" type="line" :labels="trendLabels" :datasets="trendData" height="300px" :loading="loading" />
        <ChartCard title="🚦 Denial Reasons" type="doughnut" :labels="denialLabels" :datasets="denialData" height="300px" :loading="loading" />
      </div>
    </section>

    <!-- Access Events Table -->
    <section class="vehicle-dashboard__section">
      <DataTable title="📋 Recent Access Events" :columns="accessColumns" :rows="data.accessEvents" :loading="loading" />
    </section>

    <!-- Alerts -->
    <section class="vehicle-dashboard__section">
      <AlertPanel title="🚨 Security Alerts" :alerts="data.securityAlerts" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable, AlertPanel } from './components'

export default {
  name: 'VehicleAccessControlDashboard',
  components: { KPICard, ChartCard, DataTable, AlertPanel },
  setup() {
    const loading = ref(true)
    const vehicleType = ref('all')
    const dateRange = ref('today')
    
    const data = ref({
      successfulEntries: 0, deniedEntries: 0, suspiciousAttempts: 0, anprMismatches: 0, expiredPasses: 0,
      companyAccess: {}, staffAccess: {}, visitorAccess: {},
      accessTrends: [], denialReasons: [], accessEvents: [], securityAlerts: []
    })

    const accessColumns = [
      { key: 'timestamp', label: 'Time' }, { key: 'plate_number', label: 'Plate' },
      { key: 'vehicle_type', label: 'Type', type: 'badge' }, { key: 'gate', label: 'Gate' },
      { key: 'action', label: 'Action', type: 'badge' }, { key: 'reason', label: 'Reason' },
      { key: 'operator', label: 'Operator' }
    ]

    const trendLabels = computed(() => data.value.accessTrends?.map(t => t.hour) || [])
    const trendData = computed(() => [
      { label: 'Company', data: data.value.accessTrends?.map(t => t.company) || [], borderColor: '#1976d2' },
      { label: 'Staff', data: data.value.accessTrends?.map(t => t.staff) || [], borderColor: '#43a047' },
      { label: 'Visitor', data: data.value.accessTrends?.map(t => t.visitor) || [], borderColor: '#fb8c00' }
    ])
    
    const denialLabels = computed(() => data.value.denialReasons?.map(d => d.reason) || [])
    const denialData = computed(() => [{ data: data.value.denialReasons?.map(d => d.count) || [], backgroundColor: ['#e53935', '#ff7043', '#ffca28', '#9e9e9e', '#78909c'] }])

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_vehicle_management.api.vehicle_dashboard_api.get_vehicle_access_control_dashboard', { vehicle_type: vehicleType.value, date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load access control dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, vehicleType, dateRange, data, accessColumns, trendLabels, trendData, denialLabels, denialData, refreshData }
  }
}
</script>

<style src="./dashboard-vehicle.css"></style>
<style scoped>
.access-breakdown-card { background: var(--vd-surface); border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.access-breakdown-card h4 { margin: 0 0 8px; font-size: 16px; }
.access-note { font-size: 12px; color: var(--vd-muted); margin-bottom: 16px; }
.access-stats { display: flex; gap: 16px; }
.access-stats .stat { padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; }
.access-stats .stat.success { background: rgba(67,160,71,0.15); color: #43a047; }
.access-stats .stat.danger { background: rgba(229,57,53,0.15); color: #e53935; }
</style>

