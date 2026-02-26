<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">🔍 Audit & Assurance Dashboard</h1>
        <p class="risk-dashboard__subtitle">Link Audit Findings to Risks • Internal Audit, Risk Committee</p>
      </div>
      <div class="risk-dashboard__actions">
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Audit KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="📊" :value="data.total_risks" label="Total Risks" variant="primary" :loading="loading" />
        <KPICard icon="✅" :value="data.assessed_risks" label="Assessed Risks" variant="success" :loading="loading" />
        <KPICard icon="🔴" :value="data.high_risk_count" label="High-Risk Findings" variant="danger" :loading="loading" />
        <KPICard icon="📈" :value="data.coverage_percentage + '%'" label="Risk Coverage" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Coverage Meter -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">📊 Risk Assessment Coverage</h3>
        <div class="coverage-meter">
          <div class="coverage-meter__bar">
            <div class="coverage-meter__fill" :style="{ width: data.coverage_percentage + '%' }"></div>
          </div>
          <div class="coverage-meter__stats">
            <span>{{ data.assessed_risks }} of {{ data.total_risks }} risks assessed</span>
            <span class="coverage-meter__pct">{{ data.coverage_percentage }}%</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Charts -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Risk Assessment Distribution" type="doughnut" :labels="['Assessed', 'Not Assessed']" :datasets="coverageData" height="280px" :loading="loading" />
        <ChartCard title="📋 Repeat Findings" type="bar" :labels="repeatLabels" :datasets="repeatData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- High-Risk Findings -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">🔴 High-Risk Findings</h3>
        <DataTable :columns="findingsColumns" :data="data.high_risk_findings" :loading="loading" emptyText="No high-risk findings">
          <template #cell-residual_risk_rating="{ value }">
            <span class="badge" :class="getRatingBadgeClass(value)">{{ value }}</span>
          </template>
          <template #cell-residual_risk_score="{ value }">
            <span class="score" :class="getScoreClass(value)">{{ value }}</span>
          </template>
        </DataTable>
      </div>
    </section>

    <!-- Repeat Findings -->
    <section class="risk-dashboard__section" v-if="data.repeat_findings?.length">
      <div class="data-card">
        <h3 class="data-card__title">🔁 Repeat Findings (Multiple Assessments)</h3>
        <div class="repeat-findings">
          <div v-for="finding in data.repeat_findings" :key="finding.linked_risk" class="repeat-finding">
            <span class="repeat-finding__risk">{{ finding.linked_risk }}</span>
            <span class="repeat-finding__count">{{ finding.assessment_count }} assessments</span>
          </div>
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
  name: 'AuditAssuranceDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const data = ref({ total_risks: 0, assessed_risks: 0, coverage_percentage: 0, high_risk_findings: [], high_risk_count: 0, repeat_findings: [] })

    const coverageData = computed(() => [{
      data: [data.value.assessed_risks, data.value.total_risks - data.value.assessed_risks],
      backgroundColor: ['#43a047', '#e0e0e0']
    }])

    const repeatLabels = computed(() => data.value.repeat_findings?.slice(0, 5).map(f => f.linked_risk?.substring(0, 15) + '...') || [])
    const repeatData = computed(() => [{ label: 'Assessments', data: data.value.repeat_findings?.slice(0, 5).map(f => f.assessment_count) || [], backgroundColor: '#5c6bc0' }])

    const findingsColumns = [
      { key: 'risk_title', label: 'Risk Title' },
      { key: 'residual_risk_rating', label: 'Rating' },
      { key: 'residual_risk_score', label: 'Score' },
      { key: 'assessment_date', label: 'Assessment Date', type: 'date' }
    ]

    const getRatingBadgeClass = (rating) => {
      const r = (rating || '').toLowerCase()
      if (r.includes('extreme')) return 'badge--extreme'
      if (r.includes('critical')) return 'badge--critical'
      if (r.includes('high')) return 'badge--high'
      if (r.includes('medium')) return 'badge--medium'
      return 'badge--low'
    }
    const getScoreClass = (score) => {
      if (score >= 20) return 'score--extreme'
      if (score >= 15) return 'score--critical'
      if (score >= 10) return 'score--high'
      if (score >= 5) return 'score--medium'
      return 'score--low'
    }

    const fetchData = async () => {
      loading.value = true
      try {
        const response = await api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_audit_dashboard_data')
        if (response.data.message) Object.assign(data.value, response.data.message)
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, data, coverageData, repeatLabels, repeatData, findingsColumns, getRatingBadgeClass, getScoreClass, fetchData }
  }
}
</script>

<style scoped>
.coverage-meter__bar { height: 24px; background: #e0e0e0; border-radius: 12px; overflow: hidden; margin-bottom: 8px; }
.coverage-meter__fill { height: 100%; background: linear-gradient(90deg, #43a047, #66bb6a); border-radius: 12px; transition: width 0.5s; }
.coverage-meter__stats { display: flex; justify-content: space-between; font-size: 14px; }
.coverage-meter__pct { font-weight: 700; color: #43a047; }
.repeat-findings { display: flex; flex-direction: column; gap: 8px; }
.repeat-finding { display: flex; justify-content: space-between; padding: 12px; background: var(--rd-bg); border-radius: 6px; }
.repeat-finding__risk { font-weight: 500; }
.repeat-finding__count { color: var(--rd-muted); font-size: 12px; }
</style>

