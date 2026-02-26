<template>
  <div class="dashboard vendor-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">📋 Guarding Contract & Vendor Management</h1>
        <p class="dashboard__subtitle">Contract compliance and vendor performance tracking</p>
      </div>
      <div class="dashboard__actions">
        <select v-model="selectedVendor" class="form-select">
          <option value="">All Vendors</option>
          <option v-for="v in vendors" :key="v" :value="v">{{ v }}</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Contract KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="📝" :value="data.activeContracts" label="Active Contracts" variant="primary" :loading="loading" />
        <KPICard icon="👮" :value="data.contractedGuards" label="Contracted Guards" variant="info" :loading="loading" />
        <KPICard icon="✅" :value="data.deployedGuards" label="Deployed Guards" variant="success" :loading="loading" />
        <KPICard icon="📊" :value="data.avgSlaScore" label="Avg SLA Score %" format="percent" :variant="data.avgSlaScore >= 85 ? 'success' : 'warning'" :loading="loading" />
        <KPICard icon="💰" :value="data.monthlyBilling" label="Monthly Billing" format="currency" variant="info" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="👮 Contracted vs Deployed by Vendor" type="bar" :labels="contractedVsDeployed.labels" :datasets="contractedVsDeployed.datasets" :loading="loading" />
        <ChartCard title="💰 Billing vs Attendance Hours" type="line" :labels="billingTrend.labels" :datasets="billingTrend.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Vendor Performance -->
    <section class="dashboard__section">
      <DataTable title="📊 Vendor Performance Scorecard" :columns="vendorColumns" :rows="data.vendorPerformance" :loading="loading" />
    </section>

    <!-- SLA & Contracts -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📈 SLA Compliance Trend" type="line" :labels="slaTrend.labels" :datasets="slaTrend.datasets" :loading="loading" />
        <DataTable title="📋 Contract Status" :columns="contractColumns" :rows="data.contracts" :loading="loading" />
      </div>
    </section>

    <!-- Penalties & Surcharges -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="⚠️ SLA Penalties" :columns="penaltyColumns" :rows="data.penalties" :loading="loading" />
        <DataTable title="💰 Surcharge Records" :columns="surchargeColumns" :rows="data.surcharges" :loading="loading" />
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'VendorManagementDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const selectedVendor = ref('')
    const vendors = ref([])
    const data = ref({
      activeContracts: 0, contractedGuards: 0, deployedGuards: 0, avgSlaScore: 0,
      monthlyBilling: 0, vendorPerformance: [], contracts: [], penalties: [], surcharges: [],
      contractedDeployedData: [], billingData: [], slaData: []
    })

    const vendorColumns = [
      { key: 'vendor', label: 'Vendor' }, { key: 'contracted', label: 'Contracted', type: 'number' },
      { key: 'deployed', label: 'Deployed', type: 'number' }, { key: 'sla_score', label: 'SLA %', type: 'percent' },
      { key: 'rating', label: 'Rating', type: 'badge' }
    ]
    const contractColumns = [
      { key: 'contract', label: 'Contract' }, { key: 'vendor', label: 'Vendor' },
      { key: 'start_date', label: 'Start', type: 'date' }, { key: 'end_date', label: 'End', type: 'date' },
      { key: 'status', label: 'Status', type: 'badge' }
    ]
    const penaltyColumns = [
      { key: 'vendor', label: 'Vendor' }, { key: 'reason', label: 'Reason' },
      { key: 'amount', label: 'Amount', type: 'number' }, { key: 'date', label: 'Date', type: 'date' }
    ]
    const surchargeColumns = [
      { key: 'description', label: 'Description' }, { key: 'vendor', label: 'Vendor' },
      { key: 'amount', label: 'Amount', type: 'number' }, { key: 'status', label: 'Status', type: 'badge' }
    ]

    const contractedVsDeployed = computed(() => ({
      labels: data.value.contractedDeployedData?.map(d => d.vendor) || [],
      datasets: [
        { label: 'Contracted', data: data.value.contractedDeployedData?.map(d => d.contracted) || [] },
        { label: 'Deployed', data: data.value.contractedDeployedData?.map(d => d.deployed) || [] }
      ]
    }))
    const billingTrend = computed(() => ({
      labels: data.value.billingData?.map(b => b.month) || [],
      datasets: [
        { label: 'Billing (KES)', data: data.value.billingData?.map(b => b.billing) || [] },
        { label: 'Attendance Hours', data: data.value.billingData?.map(b => b.hours) || [] }
      ]
    }))
    const slaTrend = computed(() => ({
      labels: data.value.slaData?.map(s => s.month) || [],
      datasets: [{ label: 'SLA Compliance %', data: data.value.slaData?.map(s => s.score) || [] }]
    }))

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_vendor_management_dashboard', { vendor: selectedVendor.value })
        if (res.data.message) {
          data.value = res.data.message
          vendors.value = res.data.message.vendorList || []
        }
      } catch (e) { console.error('Failed to load vendor dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, selectedVendor, vendors, data, vendorColumns, contractColumns, penaltyColumns, surchargeColumns, contractedVsDeployed, billingTrend, slaTrend, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>

