<template>
  <div class="asset-transactions">
    <div class="flex-between mb-3">
      <h1>Asset Transactions</h1>
      <button @click="refreshData" class="btn btn-primary">
        🔄 Refresh
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs mb-3">
      <button
        @click="activeTab = 'acquisitions'"
        :class="['tab-btn', { active: activeTab === 'acquisitions' }]"
      >
        Acquisitions ({{ acquisitions.length }})
      </button>
      <button
        @click="activeTab = 'disposals'"
        :class="['tab-btn', { active: activeTab === 'disposals' }]"
      >
        Disposals ({{ disposals.length }})
      </button>
    </div>

    <!-- Acquisitions Tab -->
    <div v-if="activeTab === 'acquisitions'" class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="acquisitions.length === 0" class="text-center p-3 text-muted">
          No asset acquisitions found
        </div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>Invoice ID</th>
              <th>Supplier</th>
              <th>Date</th>
              <th>Items</th>
              <th>Total Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="invoice in acquisitions" :key="invoice.name">
              <td>{{ invoice.name }}</td>
              <td>{{ invoice.supplier }}</td>
              <td>{{ formatDate(invoice.posting_date) }}</td>
              <td>{{ invoice.item_count || 1 }}</td>
              <td>${{ formatCurrency(invoice.total) }}</td>
              <td>
                <span :class="['badge', `badge-${getStatusClass(invoice.docstatus)}`]">
                  {{ getStatusLabel(invoice.docstatus) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Disposals Tab -->
    <div v-if="activeTab === 'disposals'" class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="disposals.length === 0" class="text-center p-3 text-muted">
          No asset disposals found
        </div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>Invoice ID</th>
              <th>Customer</th>
              <th>Date</th>
              <th>Items</th>
              <th>Total Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="invoice in disposals" :key="invoice.name">
              <td>{{ invoice.name }}</td>
              <td>{{ invoice.customer }}</td>
              <td>{{ formatDate(invoice.posting_date) }}</td>
              <td>{{ invoice.item_count || 1 }}</td>
              <td>${{ formatCurrency(invoice.total) }}</td>
              <td>
                <span :class="['badge', `badge-${getStatusClass(invoice.docstatus)}`]">
                  {{ getStatusLabel(invoice.docstatus) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-2 mt-4">
      <div class="stat-card">
        <h3>Total Acquisitions</h3>
        <p class="stat-value">${{ formatCurrency(totalAcquisitions) }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Disposals</h3>
        <p class="stat-value">${{ formatCurrency(totalDisposals) }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

export default {
  name: 'AssetTransactions',
  setup() {
    const loading = ref(false)
    const activeTab = ref('acquisitions')
    const acquisitions = ref([])
    const disposals = ref([])

    const totalAcquisitions = computed(() => {
      return acquisitions.value.reduce((sum, inv) => sum + (inv.total || 0), 0)
    })

    const totalDisposals = computed(() => {
      return disposals.value.reduce((sum, inv) => sum + (inv.total || 0), 0)
    })

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    }

    const formatCurrency = (value) => {
      if (!value) return '0.00'
      return parseFloat(value).toFixed(2)
    }

    const getStatusClass = (docstatus) => {
      if (docstatus === 1) return 'success'
      if (docstatus === 2) return 'danger'
      return 'warning'
    }

    const getStatusLabel = (docstatus) => {
      if (docstatus === 1) return 'Submitted'
      if (docstatus === 2) return 'Cancelled'
      return 'Draft'
    }

    const loadTransactions = async () => {
      loading.value = true
      try {
        // Load purchase invoices (acquisitions)
        const piResponse = await api.get('/api/resource/Purchase Invoice?fields=["name","supplier","posting_date","total"]&limit_page_length=500')
        acquisitions.value = piResponse.data.data || []

        // Load sales invoices (disposals)
        const siResponse = await api.get('/api/resource/Sales Invoice?fields=["name","customer","posting_date","total"]&limit_page_length=500')
        disposals.value = siResponse.data.data || []
      } catch (error) {
        console.error('Failed to load transactions:', error)
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadTransactions()
    }

    onMounted(() => {
      loadTransactions()
    })

    return {
      loading,
      activeTab,
      acquisitions,
      disposals,
      totalAcquisitions,
      totalDisposals,
      formatDate,
      formatCurrency,
      getStatusClass,
      getStatusLabel,
      refreshData
    }
  }
}
</script>

<style scoped>
.asset-transactions h1 {
  font-size: 24px;
  margin: 0;
}

.tabs {
  display: flex;
  gap: 8px;
  border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
  padding: 12px 16px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn.active {
  color: #0084ff;
  border-bottom-color: #0084ff;
}

.tab-btn:hover {
  color: #0084ff;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.badge-success {
  background-color: #e8f5e9;
  color: #388e3c;
}

.badge-warning {
  background-color: #fff3e0;
  color: #f57c00;
}

.badge-danger {
  background-color: #ffebee;
  color: #c62828;
}

.stat-card {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
}

.stat-value {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #0084ff;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
}
</style>

