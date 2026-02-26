<template>
  <div class="dashboard incident-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">🚨 Incident Management & Escalation</h1>
        <p class="dashboard__subtitle">Track incidents, investigations, and escalations</p>
      </div>
      <div class="dashboard__actions">
        <select v-model="dateRange" class="form-select">
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="quarter">This Quarter</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Incident KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--6">
        <KPICard icon="🔴" :value="data.activeIncidents" label="Active Incidents" variant="danger" :loading="loading" />
        <KPICard icon="⏰" :value="data.overdueInvestigations" label="Overdue Investigations" variant="warning" :loading="loading" />
        <KPICard icon="📈" :value="data.escalatedIncidents" label="Escalated (This Month)" variant="danger" :loading="loading" />
        <KPICard icon="✅" :value="data.resolvedIncidents" label="Resolved (This Month)" variant="success" :loading="loading" />
        <KPICard icon="⏱️" :value="data.avgResolutionTime" label="Avg Resolution (hrs)" variant="info" :loading="loading" />
        <KPICard icon="🔁" :value="data.recurringIncidents" label="Recurring Incidents" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Active Incidents & Escalation -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <AlertPanel title="🔴 Active Incidents" icon="🚨" :alerts="activeIncidentAlerts" :loading="loading" @alert-click="handleIncidentClick" />
        <AlertPanel title="⚠️ Escalation Queue" icon="📤" :alerts="escalationAlerts" :loading="loading" @alert-click="handleEscalationClick" />
      </div>
    </section>

    <!-- Charts -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Incidents by Category" type="doughnut" :labels="incidentsByCategory.labels" :datasets="incidentsByCategory.datasets" :loading="loading" />
        <ChartCard title="📈 Incident Trend" type="line" :labels="incidentTrend.labels" :datasets="incidentTrend.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Root Cause & Recurring -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="🔍 Root Cause Analysis" type="bar" :labels="rootCauses.labels" :datasets="rootCauses.datasets" :loading="loading" />
        <DataTable title="🔁 Recurring Incidents" :columns="recurringColumns" :rows="data.recurringList" :loading="loading" />
      </div>
    </section>

    <!-- Investigation Status -->
    <section class="dashboard__section">
      <DataTable title="🔍 Investigation Status" :columns="investigationColumns" :rows="data.investigations" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable, AlertPanel } from './components'

export default {
  name: 'IncidentEscalationDashboard',
  components: { KPICard, ChartCard, DataTable, AlertPanel },
  setup() {
    const loading = ref(true)
    const dateRange = ref('month')
    const data = ref({
      activeIncidents: 0, overdueInvestigations: 0, escalatedIncidents: 0,
      resolvedIncidents: 0, avgResolutionTime: 0, recurringIncidents: 0,
      activeList: [], escalationQueue: [], recurringList: [], investigations: [],
      categoryData: [], trendData: [], rootCauseData: []
    })

    const recurringColumns = [
      { key: 'incident_type', label: 'Incident Type' }, { key: 'site', label: 'Site' },
      { key: 'occurrences', label: 'Occurrences', type: 'number' }, { key: 'last_occurred', label: 'Last Occurred', type: 'date' }
    ]
    const investigationColumns = [
      { key: 'incident', label: 'Incident' }, { key: 'assigned_to', label: 'Assigned To' },
      { key: 'start_date', label: 'Started', type: 'date' }, { key: 'due_date', label: 'Due', type: 'date' },
      { key: 'progress', label: 'Progress %', type: 'percent' }, { key: 'status', label: 'Status', type: 'badge' }
    ]

    const activeIncidentAlerts = computed(() => data.value.activeList?.map(i => ({
      title: i.title, description: i.description, severity: i.severity,
      location: i.site, time: i.created_at, action: 'View'
    })) || [])
    const escalationAlerts = computed(() => data.value.escalationQueue?.map(e => ({
      title: e.incident, description: `Escalated to ${e.escalated_to}`, severity: e.priority,
      location: e.site, time: e.escalated_at, action: 'Handle'
    })) || [])

    const incidentsByCategory = computed(() => ({
      labels: data.value.categoryData?.map(c => c.category) || [],
      datasets: [{ data: data.value.categoryData?.map(c => c.count) || [] }]
    }))
    const incidentTrend = computed(() => ({
      labels: data.value.trendData?.map(t => t.date) || [],
      datasets: [
        { label: 'New', data: data.value.trendData?.map(t => t.new) || [] },
        { label: 'Resolved', data: data.value.trendData?.map(t => t.resolved) || [] }
      ]
    }))
    const rootCauses = computed(() => ({
      labels: data.value.rootCauseData?.map(r => r.cause) || [],
      datasets: [{ label: 'Count', data: data.value.rootCauseData?.map(r => r.count) || [] }]
    }))

    const handleIncidentClick = (incident) => console.log('Incident:', incident)
    const handleEscalationClick = (escalation) => console.log('Escalation:', escalation)

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_incident_escalation_dashboard', { date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load incident dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, dateRange, data, recurringColumns, investigationColumns, activeIncidentAlerts, escalationAlerts, incidentsByCategory, incidentTrend, rootCauses, handleIncidentClick, handleEscalationClick, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>

