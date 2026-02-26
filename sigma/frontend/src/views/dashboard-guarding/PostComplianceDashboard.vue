<template>
  <div class="dashboard compliance-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">📜 Post Orders & Compliance Dashboard</h1>
        <p class="dashboard__subtitle">Post order compliance and inspection tracking</p>
      </div>
      <div class="dashboard__actions">
        <select v-model="selectedSite" class="form-select">
          <option value="">All Sites</option>
          <option v-for="s in sites" :key="s" :value="s">{{ s }}</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Compliance KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="📊" :value="data.postOrderScore" label="Post Order Score %" format="percent" :variant="data.postOrderScore >= 85 ? 'success' : 'warning'" :loading="loading" />
        <KPICard icon="🔍" :value="data.inspectionsDone" label="Inspections Done" variant="primary" :loading="loading" />
        <KPICard icon="⚠️" :value="data.nonCompliance" label="Non-Compliance Findings" variant="danger" :loading="loading" />
        <KPICard icon="📄" :value="data.updatedSOPs" label="Updated SOPs" variant="info" :loading="loading" />
        <KPICard icon="⏳" :value="data.pendingReviews" label="Pending Reviews" variant="warning" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📈 Compliance Score Trend" type="line" :labels="complianceTrend.labels" :datasets="complianceTrend.datasets" :loading="loading" />
        <ChartCard title="📊 Compliance by Category" type="doughnut" :labels="complianceByCategory.labels" :datasets="complianceByCategory.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Post Orders & Inspections -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="📜 Post Order Status" :columns="postOrderColumns" :rows="data.postOrders" :loading="loading" />
        <DataTable title="🔍 Recent Inspections" :columns="inspectionColumns" :rows="data.inspections" :loading="loading" />
      </div>
    </section>

    <!-- Non-Compliance -->
    <section class="dashboard__section">
      <DataTable title="⚠️ Non-Compliance Findings" :columns="findingsColumns" :rows="data.findings" :loading="loading" />
    </section>

    <!-- Compliance by Site -->
    <section class="dashboard__section">
      <ChartCard title="🏢 Compliance Score by Site" type="bar" :labels="siteCompliance.labels" :datasets="siteCompliance.datasets" height="350px" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'PostComplianceDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedSite = ref('')
    const sites = ref([])
    const data = ref({
      postOrderScore: 0, inspectionsDone: 0, nonCompliance: 0, updatedSOPs: 0,
      pendingReviews: 0, postOrders: [], inspections: [], findings: [],
      complianceData: [], categoryData: [], siteData: []
    })

    const postOrderColumns = [
      { key: 'post', label: 'Post' }, { key: 'site', label: 'Site' },
      { key: 'last_updated', label: 'Last Updated', type: 'date' }, { key: 'status', label: 'Status', type: 'badge' }
    ]
    const inspectionColumns = [
      { key: 'site', label: 'Site' }, { key: 'inspector', label: 'Inspector' },
      { key: 'date', label: 'Date', type: 'date' }, { key: 'score', label: 'Score %', type: 'percent' },
      { key: 'result', label: 'Result', type: 'badge' }
    ]
    const findingsColumns = [
      { key: 'site', label: 'Site' }, { key: 'finding', label: 'Finding' },
      { key: 'severity', label: 'Severity', type: 'badge' }, { key: 'action_required', label: 'Action Required' },
      { key: 'due_date', label: 'Due Date', type: 'date' }, { key: 'status', label: 'Status', type: 'badge' }
    ]

    const complianceTrend = computed(() => ({
      labels: data.value.complianceData?.map(c => c.month) || [],
      datasets: [{ label: 'Compliance Score %', data: data.value.complianceData?.map(c => c.score) || [] }]
    }))
    const complianceByCategory = computed(() => ({
      labels: data.value.categoryData?.map(c => c.category) || [],
      datasets: [{ data: data.value.categoryData?.map(c => c.count) || [] }]
    }))
    const siteCompliance = computed(() => ({
      labels: data.value.siteData?.map(s => s.site) || [],
      datasets: [{ label: 'Compliance Score %', data: data.value.siteData?.map(s => s.score) || [] }]
    }))

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_post_compliance_dashboard', { site: selectedSite.value })
        if (res.data.message) {
          data.value = res.data.message
          sites.value = res.data.message.siteList || []
        }
      } catch (e) { console.error('Failed to load compliance dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, selectedSite, sites, data, postOrderColumns, inspectionColumns, findingsColumns, complianceTrend, complianceByCategory, siteCompliance, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>

