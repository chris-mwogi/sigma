<template>
  <div class="dashboard k9-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">🐕 K9 Unit Dashboard</h1>
        <p class="dashboard__subtitle">K9 deployment and handler performance tracking</p>
      </div>
      <div class="dashboard__actions">
        <select v-model="dateRange" class="form-select">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- K9 KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="🐕" :value="data.totalDogs" label="Total K9 Units" variant="primary" :loading="loading" />
        <KPICard icon="✅" :value="data.activeDeployments" label="Active Deployments" variant="success" :loading="loading" />
        <KPICard icon="⚕️" :value="data.vetChecksDue" label="Vet Checks Due" variant="warning" :loading="loading" />
        <KPICard icon="👮" :value="data.handlers" label="Active Handlers" variant="info" :loading="loading" />
        <KPICard icon="🎯" :value="data.responseActivities" label="Response Activities" variant="primary" :loading="loading" />
      </div>
    </section>

    <!-- Deployment & Schedule -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="📅 Deployment Schedule" :columns="deploymentColumns" :rows="data.deploymentSchedule" :loading="loading" />
        <DataTable title="⚕️ Vet Checks Due" :columns="vetColumns" :rows="data.vetChecks" :loading="loading" />
      </div>
    </section>

    <!-- Handler Performance -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="🏆 Handler Performance" type="bar" :labels="handlerPerformance.labels" :datasets="handlerPerformance.datasets" :loading="loading" />
        <DataTable title="👮 Handler Scorecard" :columns="handlerColumns" :rows="data.handlerScorecard" :loading="loading" />
      </div>
    </section>

    <!-- K9 Status -->
    <section class="dashboard__section">
      <div class="k9-status-grid">
        <div v-for="dog in data.k9Units" :key="dog.name" class="k9-card">
          <div class="k9-card__avatar">🐕</div>
          <div class="k9-card__info">
            <div class="k9-card__name">{{ dog.name }}</div>
            <div class="k9-card__breed">{{ dog.breed }}</div>
          </div>
          <div class="k9-card__status">
            <span :class="['status-badge', `status-badge--${dog.status?.toLowerCase()}`]">{{ dog.status }}</span>
          </div>
          <div class="k9-card__handler">
            <span class="k9-card__label">Handler:</span>
            <span>{{ dog.handler }}</span>
          </div>
          <div class="k9-card__location">
            <span class="k9-card__label">Location:</span>
            <span>{{ dog.location }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Response Activity Log -->
    <section class="dashboard__section">
      <DataTable title="📋 Response Team Activity Log" :columns="activityColumns" :rows="data.activityLog" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'K9UnitDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const dateRange = ref('today')
    const data = ref({
      totalDogs: 0, activeDeployments: 0, vetChecksDue: 0, handlers: 0, responseActivities: 0,
      deploymentSchedule: [], vetChecks: [], handlerScorecard: [], k9Units: [], activityLog: [], handlerData: []
    })

    const deploymentColumns = [
      { key: 'dog', label: 'K9 Unit' }, { key: 'handler', label: 'Handler' },
      { key: 'site', label: 'Site' }, { key: 'shift', label: 'Shift' }, { key: 'status', label: 'Status', type: 'badge' }
    ]
    const vetColumns = [
      { key: 'dog', label: 'K9 Unit' }, { key: 'check_type', label: 'Check Type' },
      { key: 'due_date', label: 'Due Date', type: 'date' }, { key: 'status', label: 'Status', type: 'badge' }
    ]
    const handlerColumns = [
      { key: 'handler', label: 'Handler' }, { key: 'deployments', label: 'Deployments', type: 'number' },
      { key: 'response_time', label: 'Avg Response' }, { key: 'score', label: 'Score %', type: 'percent' }
    ]
    const activityColumns = [
      { key: 'time', label: 'Time' }, { key: 'dog', label: 'K9 Unit' }, { key: 'handler', label: 'Handler' },
      { key: 'activity', label: 'Activity' }, { key: 'location', label: 'Location' }, { key: 'outcome', label: 'Outcome', type: 'badge' }
    ]

    const handlerPerformance = computed(() => ({
      labels: data.value.handlerData?.map(h => h.handler) || [],
      datasets: [{ label: 'Performance Score', data: data.value.handlerData?.map(h => h.score) || [] }]
    }))

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_k9_dashboard', { date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load K9 dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, dateRange, data, deploymentColumns, vetColumns, handlerColumns, activityColumns, handlerPerformance, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>
<style scoped>
.k9-status-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.k9-card { background: var(--kp-surface); border-radius: 12px; padding: 20px; display: grid; grid-template-columns: auto 1fr auto; gap: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.k9-card__avatar { font-size: 48px; grid-row: span 2; }
.k9-card__name { font-weight: 700; font-size: 16px; }
.k9-card__breed { font-size: 12px; color: var(--kp-muted); }
.k9-card__handler, .k9-card__location { grid-column: span 3; font-size: 13px; }
.k9-card__label { color: var(--kp-muted); margin-right: 8px; }
.status-badge { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.status-badge--active { background: #e8f5e9; color: #388e3c; }
.status-badge--deployed { background: #e3f2fd; color: #1976d2; }
.status-badge--rest { background: #fff8e1; color: #f57c00; }
</style>

