<template>
  <div class="risk-dashboard">
    <header class="risk-dashboard__header">
      <div class="risk-dashboard__title-section">
        <h1 class="risk-dashboard__title">📜 Compliance & Regulatory Risk Dashboard</h1>
        <p class="risk-dashboard__subtitle">Track Compliance-Related Risks & Obligations • Compliance Officers, Legal, Regulators</p>
      </div>
      <div class="risk-dashboard__actions">
        <button class="btn btn--primary" @click="fetchData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Compliance KPIs -->
    <section class="risk-dashboard__section">
      <div class="kpi-grid kpi-grid--4">
        <KPICard icon="🔗" :value="data.risks_linked_to_regulations" label="Risks Linked to Regulations" variant="primary" :loading="loading" />
        <KPICard icon="✅" :value="compliantCount" label="Compliant" variant="success" :loading="loading" />
        <KPICard icon="❌" :value="nonCompliantCount" label="Non-Compliant" variant="danger" :loading="loading" />
        <KPICard icon="⏰" :value="data.overdue_actions?.length || 0" label="Overdue Actions" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="risk-dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Compliance Status" type="doughnut" :labels="statusLabels" :datasets="statusData" height="280px" :loading="loading" />
        <ChartCard title="📋 Risks by Regulatory Framework" type="bar" :labels="frameworkLabels" :datasets="frameworkData" height="280px" :loading="loading" />
      </div>
    </section>

    <!-- Compliance Status Summary -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">📈 Compliance Rate</h3>
        <div class="compliance-rate">
          <div class="compliance-rate__meter">
            <div class="compliance-rate__fill" :style="{ width: complianceRate + '%' }" :class="getComplianceClass(complianceRate)"></div>
          </div>
          <span class="compliance-rate__value">{{ complianceRate }}%</span>
        </div>
      </div>
    </section>

    <!-- Overdue Actions -->
    <section class="risk-dashboard__section">
      <div class="data-card">
        <h3 class="data-card__title">⚠️ Overdue Compliance Actions</h3>
        <DataTable :columns="overdueColumns" :data="data.overdue_actions" :loading="loading" emptyText="No overdue compliance actions">
          <template #cell-compliance_status="{ value }">
            <span class="badge" :class="getStatusBadgeClass(value)">{{ value }}</span>
          </template>
        </DataTable>
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
  name: 'ComplianceRiskDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const data = ref({ risks_linked_to_regulations: 0, compliance_status: [], overdue_actions: [], by_framework: [] })

    const compliantCount = computed(() => data.value.compliance_status?.find(s => s.status === 'Compliant')?.count || 0)
    const nonCompliantCount = computed(() => data.value.compliance_status?.find(s => s.status === 'Non-Compliant')?.count || 0)
    const complianceRate = computed(() => {
      const total = data.value.compliance_status?.reduce((sum, s) => sum + s.count, 0) || 1
      return Math.round((compliantCount.value / total) * 100)
    })

    const statusLabels = computed(() => data.value.compliance_status?.map(s => s.status) || [])
    const statusData = computed(() => [{ data: data.value.compliance_status?.map(s => s.count) || [], backgroundColor: ['#43a047', '#e53935', '#fb8c00', '#9e9e9e'] }])

    const frameworkLabels = computed(() => data.value.by_framework?.map(f => f.framework) || [])
    const frameworkData = computed(() => [{ label: 'Requirements', data: data.value.by_framework?.map(f => f.count) || [], backgroundColor: '#5c6bc0' }])

    const overdueColumns = [
      { key: 'requirement_name', label: 'Requirement' },
      { key: 'regulatory_body', label: 'Regulatory Body' },
      { key: 'compliance_status', label: 'Status' },
      { key: 'next_review_date', label: 'Due Date', type: 'date' }
    ]

    const getComplianceClass = (rate) => {
      if (rate >= 80) return 'compliance-rate__fill--good'
      if (rate >= 50) return 'compliance-rate__fill--warning'
      return 'compliance-rate__fill--danger'
    }
    const getStatusBadgeClass = (status) => {
      if (status === 'Compliant') return 'badge--success'
      if (status === 'Non-Compliant') return 'badge--danger'
      return 'badge--warning'
    }

    const fetchData = async () => {
      loading.value = true
      try {
        const response = await api.post('/api/method/sigma.sigma_risk_assessment.api.risk_dashboard_api.get_compliance_dashboard_data')
        if (response.data.message) Object.assign(data.value, response.data.message)
      } catch (e) { console.error('Failed to fetch data:', e) }
      loading.value = false
    }

    onMounted(fetchData)
    return { loading, data, compliantCount, nonCompliantCount, complianceRate, statusLabels, statusData, frameworkLabels, frameworkData, overdueColumns, getComplianceClass, getStatusBadgeClass, fetchData }
  }
}
</script>

<style scoped>
.compliance-rate { display: flex; align-items: center; gap: 16px; }
.compliance-rate__meter { flex: 1; height: 24px; background: #e0e0e0; border-radius: 12px; overflow: hidden; }
.compliance-rate__fill { height: 100%; transition: width 0.5s; border-radius: 12px; }
.compliance-rate__fill--good { background: linear-gradient(90deg, #43a047, #66bb6a); }
.compliance-rate__fill--warning { background: linear-gradient(90deg, #fb8c00, #ffc107); }
.compliance-rate__fill--danger { background: linear-gradient(90deg, #c62828, #e53935); }
.compliance-rate__value { font-size: 32px; font-weight: 700; color: var(--rd-text); min-width: 80px; text-align: right; }
</style>

