<template>
  <div class="dashboard combined-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">🧩 Combined Security & Risk Dashboard</h1>
        <p class="dashboard__subtitle">Strategic security and risk correlation analysis</p>
      </div>
      <div class="dashboard__actions">
        <select v-model="dateRange" class="form-select">
          <option value="month">This Month</option>
          <option value="quarter">This Quarter</option>
          <option value="year">This Year</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Strategic KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="🎯" :value="data.overallRiskScore" label="Overall Risk Score" :variant="getRiskVariant(data.overallRiskScore)" :loading="loading" />
        <KPICard icon="🏢" :value="data.highRiskSites" label="High-Risk Sites" variant="danger" :loading="loading" />
        <KPICard icon="✅" :value="data.guardingAdequacy" label="Guarding Adequacy %" format="percent" :variant="data.guardingAdequacy >= 90 ? 'success' : 'warning'" :loading="loading" />
        <KPICard icon="💰" :value="data.securityBudget" label="Security Budget" format="currency" variant="info" :loading="loading" />
        <KPICard icon="📊" :value="data.costEffectiveness" label="Cost Effectiveness %" format="percent" variant="primary" :loading="loading" />
      </div>
    </section>

    <!-- Sites by Risk Score -->
    <section class="dashboard__section">
      <DataTable title="🏢 Sites Sorted by Risk Score" :columns="siteRiskColumns" :rows="data.sitesByRisk" :loading="loading" />
    </section>

    <!-- Risk vs Guarding Charts -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Guarding Adequacy vs Risk Level" type="bar" :labels="guardingVsRisk.labels" :datasets="guardingVsRisk.datasets" :loading="loading" />
        <ChartCard title="📈 Risk Level vs Incidents Correlation" type="line" :labels="riskVsIncidents.labels" :datasets="riskVsIncidents.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Cost Analysis -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="💰 Cost vs Risk Mitigation Effectiveness" type="bar" :labels="costVsMitigation.labels" :datasets="costVsMitigation.datasets" :loading="loading" />
        <div class="risk-matrix-card">
          <div class="risk-matrix-card__header">
            <h3>🎯 Risk Matrix Overview</h3>
          </div>
          <div class="risk-matrix-card__body">
            <div class="risk-matrix">
              <div v-for="(cell, idx) in riskMatrixCells" :key="idx" :class="['risk-matrix__cell', `risk-matrix__cell--${cell.level}`]">
                <span class="risk-matrix__count">{{ cell.count }}</span>
                <span class="risk-matrix__label">{{ cell.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Regional Analysis -->
    <section class="dashboard__section">
      <ChartCard title="🗺️ Risk by Region" type="bar" :labels="riskByRegion.labels" :datasets="riskByRegion.datasets" height="350px" :loading="loading" />
    </section>

    <!-- Recommendations -->
    <section class="dashboard__section">
      <div class="recommendations-card">
        <div class="recommendations-card__header">
          <h3>💡 Security Recommendations</h3>
        </div>
        <div class="recommendations-card__body">
          <div v-for="(rec, idx) in data.recommendations" :key="idx" class="recommendation-item">
            <span class="recommendation-item__icon">{{ rec.priority === 'High' ? '🔴' : rec.priority === 'Medium' ? '🟡' : '🟢' }}</span>
            <div class="recommendation-item__content">
              <div class="recommendation-item__title">{{ rec.title }}</div>
              <div class="recommendation-item__desc">{{ rec.description }}</div>
            </div>
            <span class="recommendation-item__impact">Impact: {{ rec.impact }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'CombinedSecurityRiskDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const dateRange = ref('month')
    const data = ref({
      overallRiskScore: 0, highRiskSites: 0, guardingAdequacy: 0, securityBudget: 0,
      costEffectiveness: 0, sitesByRisk: [], recommendations: [], riskMatrix: [],
      guardingRiskData: [], incidentsRiskData: [], costMitigationData: [], regionData: []
    })

    const siteRiskColumns = [
      { key: 'site', label: 'Site' }, { key: 'region', label: 'Region' },
      { key: 'risk_score', label: 'Risk Score', type: 'number' }, { key: 'guarding_strength', label: 'Guards', type: 'number' },
      { key: 'incidents', label: 'Incidents', type: 'number' }, { key: 'status', label: 'Status', type: 'badge' }
    ]

    const getRiskVariant = (score) => score > 70 ? 'danger' : score > 40 ? 'warning' : 'success'

    const riskMatrixCells = computed(() => data.value.riskMatrix?.length ? data.value.riskMatrix : [
      { level: 'critical', count: 0, label: 'Critical' }, { level: 'high', count: 0, label: 'High' },
      { level: 'medium', count: 0, label: 'Medium' }, { level: 'low', count: 0, label: 'Low' }
    ])

    const guardingVsRisk = computed(() => ({
      labels: data.value.guardingRiskData?.map(d => d.site) || [],
      datasets: [
        { label: 'Risk Score', data: data.value.guardingRiskData?.map(d => d.risk) || [] },
        { label: 'Guard Strength', data: data.value.guardingRiskData?.map(d => d.guards) || [] }
      ]
    }))
    const riskVsIncidents = computed(() => ({
      labels: data.value.incidentsRiskData?.map(d => d.month) || [],
      datasets: [
        { label: 'Risk Score', data: data.value.incidentsRiskData?.map(d => d.risk) || [] },
        { label: 'Incidents', data: data.value.incidentsRiskData?.map(d => d.incidents) || [] }
      ]
    }))
    const costVsMitigation = computed(() => ({
      labels: data.value.costMitigationData?.map(d => d.category) || [],
      datasets: [
        { label: 'Cost (KES)', data: data.value.costMitigationData?.map(d => d.cost) || [] },
        { label: 'Effectiveness %', data: data.value.costMitigationData?.map(d => d.effectiveness) || [] }
      ]
    }))
    const riskByRegion = computed(() => ({
      labels: data.value.regionData?.map(r => r.region) || [],
      datasets: [{ label: 'Risk Score', data: data.value.regionData?.map(r => r.score) || [] }]
    }))

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_combined_security_risk_dashboard', { date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load combined dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, dateRange, data, siteRiskColumns, getRiskVariant, riskMatrixCells, guardingVsRisk, riskVsIncidents, costVsMitigation, riskByRegion, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>
<style scoped>
.risk-matrix-card { background: var(--kp-surface); border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.risk-matrix-card__header { padding: 16px 20px; border-bottom: 1px solid var(--kp-border); }
.risk-matrix-card__header h3 { margin: 0; font-size: 16px; }
.risk-matrix-card__body { padding: 20px; }
.risk-matrix { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.risk-matrix__cell { padding: 20px; border-radius: 8px; text-align: center; }
.risk-matrix__cell--critical { background: #ffebee; }
.risk-matrix__cell--high { background: #fff3e0; }
.risk-matrix__cell--medium { background: #fff8e1; }
.risk-matrix__cell--low { background: #e8f5e9; }
.risk-matrix__count { display: block; font-size: 28px; font-weight: 700; }
.risk-matrix__label { font-size: 12px; color: var(--kp-muted); }
.recommendations-card { background: var(--kp-surface); border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.recommendations-card__header { padding: 16px 20px; border-bottom: 1px solid var(--kp-border); }
.recommendations-card__header h3 { margin: 0; font-size: 16px; }
.recommendations-card__body { padding: 16px; }
.recommendation-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px; background: var(--kp-bg); border-radius: 8px; margin-bottom: 12px; }
.recommendation-item__icon { font-size: 20px; }
.recommendation-item__content { flex: 1; }
.recommendation-item__title { font-weight: 600; font-size: 14px; }
.recommendation-item__desc { font-size: 13px; color: var(--kp-muted); margin-top: 4px; }
.recommendation-item__impact { font-size: 12px; color: var(--kp-primary); font-weight: 500; }
</style>

