<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">🏢 Enterprise Risk Overview</h1>
        <p class="risk-dashboard__subtitle">Board & Executive Level • Organisation-Wide Risk Exposure</p>
      </div>
      <div class="risk-dashboard__actions">
        <select v-model="filters.department" class="form-select" @change="fetchData">
          <option value="">All Departments</option>
          <option v-for="d in filterOptions.departments" :key="d.value" :value="d.value">{{ d.label }}</option>
        </select>
        <select v-model="filters.category" class="form-select" @change="fetchData">
          <option value="">All Categories</option>
          <option v-for="c in filterOptions.categories" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Executive KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="📊" :value="data.total_risks" label="Total Risks" variant="primary" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_critical_risks" label="High & Critical" variant="danger" :loading="loading" />
        <KPICard icon="⚡" :value="data.active_risks" label="Active Risks" variant="warning" :loading="loading" />
        <KPICard icon="✅" :value="data.mitigated_risks" label="Mitigated" variant="success" :loading="loading" />
        <KPICard icon="📈" :value="riskReductionPct + '%'" label="Risk Reduction" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Charts Row -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Risks by Priority" type="doughnut" :labels="priorityLabels" :datasets="priorityData" height="300px" :loading="loading" />
        <ChartCard title="📋 Risks by Category" type="bar" :labels="categoryLabels" :datasets="categoryData" height="300px" :loading="loading" />
      </div>
    </section>

    <!-- Heat Maps -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <RiskHeatMap title="🔥 Inherent Risk Heat Map" subtitle="Before Controls" :matrix="data.heatmap?.inherent" :loading="loading" />
        <RiskHeatMap title="🛡️ Residual Risk Heat Map" subtitle="After Controls" :matrix="data.heatmap?.residual" :loading="loading" />
      </div>
    </section>

    <!-- Top Risks Table -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">🔝 Top 10 Risks by Inherent Score</h3>
        <DataTable :columns="topRiskColumns" :data="data.top_risks" :loading="loading" emptyText="No high-risk items found" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable, RiskHeatMap } from './components'
import './dashboard-risk.css'

export default {
  name: 'EnterpriseRiskDashboard',
  components: { KPICard, ChartCard, DataTable, RiskHeatMap },
  setup() {
    const loading = ref(true)
    const filters = ref({ department: '', category: '', period: 'ytd' })
    const filterOptions = ref({ departments: [], categories: [] })
    const data = ref({
      total_risks: 0, high_critical_risks: 0, active_risks: 0, mitigated_risks: 0,
      by_priority: [], by_category: [], top_risks: [], heatmap: { inherent: [], residual: [] }
    })

    const priorityLabels = computed(() => data.value.by_priority?.map(p => p.priority) || [])
    const priorityData = computed(() => [{
      data: data.value.by_priority?.map(p => p.count) || [],
      backgroundColor: ['#7b1fa2', '#c62828', '#ef6c00', '#fbc02d', '#66bb6a', '#9e9e9e']
    }])

    const categoryLabels = computed(() => data.value.by_category?.map(c => c.category) || [])
    const categoryData = computed(() => [{ label: 'Risks', data: data.value.by_category?.map(c => c.count) || [], backgroundColor: '#5c6bc0' }])

    const riskReductionPct = computed(() => {
      const total = data.value.total_risks || 1
      const mitigated = data.value.mitigated_risks || 0
      return Math.round((mitigated / total) * 100)
    })

    const topRiskColumns = [
      { key: 'risk_title', label: 'Risk Title' },
      { key: 'risk_category', label: 'Category' },
      { key: 'department', label: 'Department' },
      { key: 'inherent_risk_score', label: 'Inherent Score', type: 'score' },
      { key: 'residual_risk_score', label: 'Residual Score', type: 'score' },
      { key: 'residual_risk_rating', label: 'Rating', type: 'badge' }
    ]

    const fetchData = async () => {
      loading.value = true
      try {
        const [overview, heatmap, options] = await Promise.all([
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_enterprise_risk_overview', { filters: filters.value }),
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_residual_risk_heatmap'),
          api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_filter_options')
        ])
        if (overview.data.message) Object.assign(data.value, overview.data.message)
        if (heatmap.data.message) data.value.heatmap = heatmap.data.message
        if (options.data.message) Object.assign(filterOptions.value, options.data.message)
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, filters, filterOptions, data, priorityLabels, priorityData, categoryLabels, categoryData, riskReductionPct, topRiskColumns, fetchData }
  }
}
</script>

