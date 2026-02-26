<template>
  <div class="dashboard executive-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">🛡️ Executive Security Dashboard</h1>
        <p class="dashboard__subtitle">Strategic view of guarding performance, risk exposure, and compliance</p>
      </div>
      <div class="dashboard__actions">
        <select v-model="dateRange" class="form-select">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="quarter">This Quarter</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- KPI Cards Row -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--6">
        <KPICard icon="⚠️" :value="data.riskIndex" label="Security Risk Index" :variant="getRiskVariant(data.riskIndex)" format="number" :loading="loading" />
        <KPICard icon="👮" :value="data.guardStrength" label="Guard Strength" variant="primary" :loading="loading" />
        <KPICard icon="🏢" :value="data.highRiskSites" label="High-Risk Sites" variant="danger" :loading="loading" />
        <KPICard icon="💰" :value="data.monthlyGuardingCost" label="Monthly Guarding Cost" format="currency" variant="info" :loading="loading" />
        <KPICard icon="📊" :value="data.slaCompliance" label="SLA Compliance" format="percent" :variant="data.slaCompliance >= 90 ? 'success' : 'warning'" :loading="loading" />
        <KPICard icon="📋" :value="data.openIncidents" label="Open Incidents" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Charts Row -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📈 Incident Trends (12 Months)" type="line" :labels="incidentTrend.labels" :datasets="incidentTrend.datasets" :loading="loading" />
        <ChartCard title="🥧 Incidents by Category" type="doughnut" :labels="incidentsByCategory.labels" :datasets="incidentsByCategory.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Tables Row -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="🏢 High-Risk Sites" :columns="highRiskSitesColumns" :rows="data.highRiskSitesList" :loading="loading" />
        <DataTable title="📊 Vendor Performance Scorecard" :columns="vendorColumns" :rows="data.vendorScorecard" :loading="loading" />
      </div>
    </section>

    <!-- Cost Analysis -->
    <section class="dashboard__section">
      <ChartCard title="💰 Cost vs Risk Mitigation by Region" type="bar" :labels="costAnalysis.labels" :datasets="costAnalysis.datasets" height="350px" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'ExecutiveSecurityDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const dateRange = ref('month')
    const data = ref({
      riskIndex: 0, guardStrength: 0, highRiskSites: 0, monthlyGuardingCost: 0,
      slaCompliance: 0, openIncidents: 0, highRiskSitesList: [], vendorScorecard: [],
      incidentTrends: [], incidentCategories: [], costByRegion: []
    })

    const highRiskSitesColumns = [
      { key: 'site', label: 'Site' },
      { key: 'risk_score', label: 'Risk Score', type: 'number' },
      { key: 'incidents', label: 'Incidents', type: 'number' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]

    const vendorColumns = [
      { key: 'vendor', label: 'Vendor' },
      { key: 'deployed', label: 'Deployed', type: 'number' },
      { key: 'sla_score', label: 'SLA %', type: 'percent' },
      { key: 'performance', label: 'Performance', type: 'badge' }
    ]

    const incidentTrend = computed(() => ({
      labels: data.value.incidentTrends?.map(t => t.month) || [],
      datasets: [{ label: 'Incidents', data: data.value.incidentTrends?.map(t => t.count) || [] }]
    }))

    const incidentsByCategory = computed(() => ({
      labels: data.value.incidentCategories?.map(c => c.category) || [],
      datasets: [{ data: data.value.incidentCategories?.map(c => c.count) || [] }]
    }))

    const costAnalysis = computed(() => ({
      labels: data.value.costByRegion?.map(r => r.region) || [],
      datasets: [
        { label: 'Cost (KES)', data: data.value.costByRegion?.map(r => r.cost) || [] },
        { label: 'Risk Mitigation Score', data: data.value.costByRegion?.map(r => r.mitigation) || [] }
      ]
    }))

    const getRiskVariant = (score) => score > 70 ? 'danger' : score > 40 ? 'warning' : 'success'

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_executive_security_dashboard', { date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load executive dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, dateRange, data, highRiskSitesColumns, vendorColumns, incidentTrend, incidentsByCategory, costAnalysis, getRiskVariant, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>

