<template>
  <div class="case-dashboard">
    <header class="case-dashboard__header">
      <div class="case-dashboard__title-section">
        <h1 class="case-dashboard__title">👥 HR Misconduct Dashboard</h1>
        <p class="case-dashboard__subtitle">Employee Discipline • HR Case Management</p>
      </div>
      <div class="case-dashboard__actions">
        <select v-model="selectedDepartment" class="form-select">
          <option value="all">All Departments</option>
          <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- HR KPIs -->
    <section class="case-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📂" :value="data.open_cases" label="Open Cases" variant="warning" :loading="loading" />
        <KPICard icon="🔍" :value="data.under_investigation" label="Under Investigation" variant="primary" :loading="loading" />
        <KPICard icon="📆" :value="data.cases_this_month" label="Cases This Month" variant="info" :loading="loading" />
        <KPICard icon="👤" :value="data.pending_assignments" label="Pending Assignments" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Department Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="🏢 HR Misconduct by Department" type="bar" :labels="deptLabels" :datasets="deptData" height="320px" :loading="loading" />
    </section>

    <!-- Charts Grid -->
    <section class="case-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📋 Cases by Category" type="pie" :labels="categoryLabels" :datasets="categoryData" height="280px" :loading="loading" />
        <ChartCard title="📊 Cases by Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Trend Chart -->
    <section class="case-dashboard__section">
      <ChartCard title="📈 Case Trend (Monthly)" type="line" :labels="trendLabels" :datasets="trendData" height="300px" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard } from './components'

export default {
  name: 'HRMisconductDashboard',
  components: { KPICard, ChartCard },
  setup() {
    const loading = ref(true)
    const selectedDepartment = ref('all')
    const departments = ref([])
    const data = ref({
      open_cases: 0, under_investigation: 0, cases_this_month: 0, pending_assignments: 0,
      by_department: [], by_category: [], by_status: [], trend: []
    })

    const deptLabels = computed(() => data.value.by_department?.map(d => d.department) || [])
    const deptData = computed(() => [{ label: 'Cases', data: data.value.by_department?.map(d => d.count) || [], backgroundColor: '#5c6bc0' }])

    const categoryLabels = computed(() => data.value.by_category?.map(c => c.category) || [])
    const categoryData = computed(() => [{ data: data.value.by_category?.map(c => c.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935', '#00acc1'] }])

    const statusLabels = computed(() => data.value.by_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.by_status?.map(s => s.count) || [], backgroundColor: ['#5c6bc0', '#fb8c00', '#43a047', '#e53935'] }])

    const trendLabels = computed(() => data.value.trend?.map(t => t.period) || [])
    const trendData = computed(() => [{ label: 'HR Cases', data: data.value.trend?.map(t => t.total) || [], borderColor: '#5c6bc0', fill: false }])

    const fetchData = async () => {
      loading.value = true
      try {
        const [hrData, trend] = await Promise.all([
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_hr_misconduct_dashboard'),
          api.post('/api/method/sigma.sigma_case_management.api.dashboard_api.get_cases_over_time', { period: 'monthly' })
        ])
        if (hrData.data.message) {
          data.value.open_cases = hrData.data.message.employee_cases
          data.value.pending_assignments = hrData.data.message.pending_hr_decision
          data.value.by_department = hrData.data.message.by_department
          data.value.by_category = hrData.data.message.misconduct_types
        }
        if (trend.data.message) data.value.trend = trend.data.message
      } catch (e) { console.error('Failed to load HR misconduct dashboard:', e) }
      finally { loading.value = false }
    }

    onMounted(fetchData)
    return { loading, selectedDepartment, departments, data, deptLabels, deptData, categoryLabels, categoryData, statusLabels, statusData, trendLabels, trendData, fetchData }
  }
}
</script>

<style src="./dashboard-case.css"></style>

