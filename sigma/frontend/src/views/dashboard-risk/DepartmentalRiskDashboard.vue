<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">🏬 Departmental Risk Dashboard</h1>
        <p class="risk-dashboard__subtitle">Department-Level Monitoring & Accountability</p>
      </div>
      <div class="risk-dashboard__actions">
        <select v-model="selectedDepartment" class="form-select" @change="fetchData">
          <option value="">All Departments</option>
          <option v-for="d in departments" :key="d.value" :value="d.value">{{ d.label }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Department KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="📊" :value="totalRisks" label="Total Risks" variant="primary" :loading="loading" />
        <KPICard icon="⚡" :value="activeRisks" label="Active" variant="warning" :loading="loading" />
        <KPICard icon="✅" :value="closedRisks" label="Closed" variant="success" :loading="loading" />
        <KPICard icon="⏰" :value="data.overdue_count" label="Overdue Plans" variant="danger" :loading="loading" />
        <KPICard icon="📈" :value="data.avg_residual_score" label="Avg Risk Score" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Open vs Closed Risks" type="bar" :labels="deptLabels" :datasets="deptData" height="300px" :loading="loading" />
        <ChartCard title="📋 Treatment Plans Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="300px" :loading="loading" />
      </div>
    </section>

    <!-- Risks Due for Review -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">📅 Risks Due for Review (Next 30 Days)</h3>
        <DataTable :columns="reviewColumns" :data="data.risks_due_review" :loading="loading" emptyText="No risks due for review" />
      </div>
    </section>

    <!-- Overdue Treatment Plans -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">⚠️ Overdue Treatment Plans</h3>
        <DataTable :columns="overdueColumns" :data="data.overdue_plans" :loading="loading" emptyText="No overdue plans" />
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
  name: 'DepartmentalRiskDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedDepartment = ref('')
    const departments = ref([])
    const data = ref({ by_department: [], by_status: [], overdue_plans: [], risks_due_review: [], overdue_count: 0, avg_residual_score: 0 })

    const totalRisks = computed(() => data.value.by_department?.reduce((sum, d) => sum + d.total, 0) || 0)
    const activeRisks = computed(() => data.value.by_department?.reduce((sum, d) => sum + d.active, 0) || 0)
    const closedRisks = computed(() => data.value.by_department?.reduce((sum, d) => sum + d.closed, 0) || 0)

    const deptLabels = computed(() => data.value.by_department?.map(d => d.department) || [])
    const deptData = computed(() => [
      { label: 'Active', data: data.value.by_department?.map(d => d.active) || [], backgroundColor: '#ef6c00' },
      { label: 'Closed', data: data.value.by_department?.map(d => d.closed) || [], backgroundColor: '#43a047' }
    ])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935', '#9e9e9e'] }])

    const reviewColumns = [
      { key: 'risk_title', label: 'Risk' },
      { key: 'department', label: 'Department' },
      { key: 'risk_owner', label: 'Owner' },
      { key: 'next_review_date', label: 'Review Date', type: 'date' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]
    const overdueColumns = [
      { key: 'plan_title', label: 'Plan' },
      { key: 'risk_title', label: 'Risk' },
      { key: 'plan_owner', label: 'Owner' },
      { key: 'target_completion_date', label: 'Due Date', type: 'date' },
      { key: 'progress_percentage', label: 'Progress', type: 'progress' }
    ]

    const fetchData = async () => {
      loading.value = true
      try {
        const [deptData, treatmentData, reviewData, options] = await Promise.all([
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_departmental_risk_summary', { department: selectedDepartment.value }),
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_treatment_plans_status', { department: selectedDepartment.value }),
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_risks_due_for_review', { department: selectedDepartment.value }),
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_filter_options')
        ])
        if (deptData.data.message) data.value.by_department = deptData.data.message.by_department
        if (treatmentData.data.message) Object.assign(data.value, treatmentData.data.message)
        if (reviewData.data.message) data.value.risks_due_review = reviewData.data.message
        if (options.data.message) departments.value = options.data.message.departments
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, selectedDepartment, departments, data, totalRisks, activeRisks, closedRisks, deptLabels, deptData, statusLabels, statusData, reviewColumns, overdueColumns, fetchData }
  }
}
</script>

