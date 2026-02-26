<template>
  <div class="dashboard supervisor-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">👷 Guard Supervisor Dashboard</h1>
        <p class="dashboard__subtitle">Daily operations management and team oversight</p>
      </div>
      <div class="dashboard__actions">
        <input type="date" v-model="selectedDate" class="form-select" />
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Daily KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="📋" :value="data.rostersToday" label="Rosters Today" variant="primary" :loading="loading" />
        <KPICard icon="⚠️" :value="data.attendanceExceptions" label="Attendance Exceptions" variant="warning" :loading="loading" />
        <KPICard icon="🔧" :value="data.equipmentIssued" label="Equipment Issued" variant="info" :loading="loading" />
        <KPICard icon="📓" :value="data.occurrenceBookEntries" label="OB Entries Today" variant="primary" :loading="loading" />
        <KPICard icon="⏳" :value="data.pendingActions" label="Pending Actions" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Roster & Attendance -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="📅 Today's Roster" :columns="rosterColumns" :rows="data.roster" :loading="loading">
          <template #actions>
            <button class="btn btn--secondary">+ Add Entry</button>
          </template>
        </DataTable>
        <DataTable title="⚠️ Attendance Exceptions" :columns="exceptionColumns" :rows="data.exceptions" :loading="loading" />
      </div>
    </section>

    <!-- Equipment & OB -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="🔧 Equipment Register" :columns="equipmentColumns" :rows="data.equipment" :loading="loading" />
        <DataTable title="📓 Occurrence Book" :columns="obColumns" :rows="data.occurrenceBook" :loading="loading">
          <template #actions>
            <button class="btn btn--secondary">+ New Entry</button>
          </template>
        </DataTable>
      </div>
    </section>

    <!-- Charts -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Shift Distribution" type="bar" :labels="shiftChart.labels" :datasets="shiftChart.datasets" :loading="loading" />
        <ChartCard title="📈 Weekly Attendance Trend" type="line" :labels="attendanceTrend.labels" :datasets="attendanceTrend.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Pending Actions -->
    <section class="dashboard__section">
      <DataTable title="⏳ Incident Actions Pending" :columns="actionsColumns" :rows="data.pendingActionsList" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'GuardSupervisorDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedDate = ref(new Date().toISOString().split('T')[0])
    const data = ref({
      rostersToday: 0, attendanceExceptions: 0, equipmentIssued: 0,
      occurrenceBookEntries: 0, pendingActions: 0, roster: [], exceptions: [],
      equipment: [], occurrenceBook: [], pendingActionsList: [], shiftData: [], attendanceData: []
    })

    const rosterColumns = [
      { key: 'guard', label: 'Guard' }, { key: 'post', label: 'Post' },
      { key: 'shift', label: 'Shift' }, { key: 'status', label: 'Status', type: 'badge' }
    ]
    const exceptionColumns = [
      { key: 'guard', label: 'Guard' }, { key: 'type', label: 'Exception Type', type: 'badge' },
      { key: 'time', label: 'Time' }, { key: 'action', label: 'Action Required' }
    ]
    const equipmentColumns = [
      { key: 'item', label: 'Item' }, { key: 'serial', label: 'Serial #' },
      { key: 'issued_to', label: 'Issued To' }, { key: 'status', label: 'Status', type: 'badge' }
    ]
    const obColumns = [
      { key: 'time', label: 'Time' }, { key: 'entry', label: 'Entry' },
      { key: 'recorded_by', label: 'Recorded By' }, { key: 'category', label: 'Category', type: 'badge' }
    ]
    const actionsColumns = [
      { key: 'incident', label: 'Incident' }, { key: 'action', label: 'Action Required' },
      { key: 'assigned_to', label: 'Assigned To' }, { key: 'due_date', label: 'Due Date', type: 'date' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]

    const shiftChart = computed(() => ({
      labels: data.value.shiftData?.map(s => s.shift) || [],
      datasets: [{ label: 'Guards', data: data.value.shiftData?.map(s => s.count) || [] }]
    }))
    const attendanceTrend = computed(() => ({
      labels: data.value.attendanceData?.map(a => a.day) || [],
      datasets: [
        { label: 'Present', data: data.value.attendanceData?.map(a => a.present) || [] },
        { label: 'Absent', data: data.value.attendanceData?.map(a => a.absent) || [] }
      ]
    }))

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_guard_supervisor_dashboard', { date: selectedDate.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load supervisor dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, selectedDate, data, rosterColumns, exceptionColumns, equipmentColumns, obColumns, actionsColumns, shiftChart, attendanceTrend, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>

