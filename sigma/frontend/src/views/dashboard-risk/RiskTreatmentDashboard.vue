<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">🛠️ Risk Treatment & Mitigation Dashboard</h1>
        <p class="risk-dashboard__subtitle">Track Effectiveness of Mitigation Actions • Risk Managers & Project Teams</p>
      </div>
      <div class="risk-dashboard__actions">
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Treatment KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📋" :value="totalPlans" label="Total Treatment Plans" variant="primary" :loading="loading" />
        <KPICard icon="⏰" :value="data.overdue_plans?.length || 0" label="Overdue Plans" variant="danger" :loading="loading" />
        <KPICard icon="⏱️" :value="data.avg_close_time_days + ' days'" label="Avg Time to Close" variant="info" :loading="loading" />
        <KPICard icon="⚠️" :value="data.risks_without_plans" label="Risks Without Plans" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Treatment Plans by Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="300px" :loading="loading" />
        <ChartCard title="📈 Treatment Progress Distribution" type="bar" :labels="progressLabels" :datasets="progressData" height="300px" :loading="loading" />
      </div>
    </section>

    <!-- Overdue Treatment Plans -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">⚠️ Overdue Treatment Plans</h3>
        <DataTable :columns="overdueColumns" :data="data.overdue_plans" :loading="loading" emptyText="No overdue treatment plans">
          <template #cell-days_overdue="{ value }">
            <span class="badge badge--danger">{{ value }} days overdue</span>
          </template>
          <template #cell-progress_percentage="{ value }">
            <div class="progress-wrapper">
              <div class="progress-bar">
                <div class="progress-bar__fill" :class="getProgressClass(value)" :style="{ width: value + '%' }"></div>
              </div>
              <span class="progress-text">{{ value }}%</span>
            </div>
          </template>
        </DataTable>
      </div>
    </section>

    <!-- Risks Without Treatment -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">🚨 Active Risks Without Treatment Plans</h3>
        <div v-if="data.risks_without_plans > 0" class="alert-banner alert-banner--warning">
          <span class="alert-banner__icon">⚠️</span>
          <span>{{ data.risks_without_plans }} active risks have no treatment plan assigned. Review and create treatment plans for these risks.</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'
import './dashboard-risk.css'

export default {
  name: 'RiskTreatmentDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const data = ref({ by_status: [], overdue_plans: [], avg_close_time_days: 0, risks_without_plans: 0 })

    const totalPlans = computed(() => data.value.by_status?.reduce((sum, s) => sum + s.count, 0) || 0)
    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{
      data: data.value.by_status?.map(s => s.count) || [],
      backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935', '#9e9e9e']
    }])

    const progressLabels = ['0-25%', '26-50%', '51-75%', '76-99%', '100%']
    const progressData = computed(() => {
      const bins = [0, 0, 0, 0, 0]
      // This would need actual data - using mock distribution
      return [{ label: 'Plans', data: bins, backgroundColor: '#5c6bc0' }]
    })

    const overdueColumns = [
      { key: 'plan_title', label: 'Plan Title' },
      { key: 'risk_title', label: 'Related Risk' },
      { key: 'risk_category', label: 'Category' },
      { key: 'plan_owner', label: 'Owner' },
      { key: 'days_overdue', label: 'Days Overdue' },
      { key: 'progress_percentage', label: 'Progress' }
    ]

    const getProgressClass = (pct) => {
      if (pct >= 75) return 'progress-bar__fill--success'
      if (pct >= 50) return 'progress-bar__fill--warning'
      return 'progress-bar__fill--danger'
    }

    const fetchData = async () => {
      loading.value = true
      try {
        const response = await api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_treatment_dashboard_data')
        if (response.data.message) Object.assign(data.value, response.data.message)
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, data, totalPlans, statusLabels, statusData, progressLabels, progressData, overdueColumns, getProgressClass, fetchData }
  }
}
</script>

<style scoped>
.progress-wrapper { display: flex; align-items: center; gap: 8px; }
.progress-bar { flex: 1; height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; }
.progress-bar__fill { height: 100%; transition: width 0.3s; }
.progress-bar__fill--success { background: #43a047; }
.progress-bar__fill--warning { background: #fb8c00; }
.progress-bar__fill--danger { background: #e53935; }
.progress-text { font-size: 12px; font-weight: 600; min-width: 40px; }
.alert-banner { display: flex; align-items: center; gap: 12px; padding: 16px; border-radius: 8px; }
.alert-banner--warning { background: rgba(251, 140, 0, 0.1); border: 1px solid #fb8c00; color: #e65100; }
.alert-banner__icon { font-size: 24px; }
</style>

