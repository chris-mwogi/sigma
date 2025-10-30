<template>
  <div class="asset-detail">
    <div class="flex-between mb-3">
      <h1>{{ assetData?.name }}</h1>
      <router-link to="/assets" class="btn btn-outline">
        ← Back
      </router-link>
    </div>

    <div v-if="loading" class="text-center p-3">Loading...</div>
    <div v-else-if="!assetData" class="alert alert-danger">
      Asset not found
    </div>
    <div v-else class="grid grid-2">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Asset Information</h2>
        </div>
        <div class="card-body p-3">
          <div class="detail-row">
            <span class="detail-label">Asset ID:</span>
            <span class="detail-value">{{ assetData.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Name:</span>
            <span class="detail-value">{{ assetData.asset_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Type:</span>
            <span class="detail-value">{{ assetData.asset_type }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span :class="['badge', `badge-${getStatusClass(assetData.status)}`]">
              {{ assetData.status }}
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Value:</span>
            <span class="detail-value">${{ assetData.asset_value || '0' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Location:</span>
            <span class="detail-value">{{ assetData.location || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Additional Details</h2>
        </div>
        <div class="card-body p-3">
          <div class="detail-row">
            <span class="detail-label">Serial Number:</span>
            <span class="detail-value">{{ assetData.serial_number || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Manufacturer:</span>
            <span class="detail-value">{{ assetData.manufacturer || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Purchase Date:</span>
            <span class="detail-value">{{ formatDate(assetData.purchase_date) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Warranty Expiry:</span>
            <span class="detail-value">{{ formatDate(assetData.warranty_expiry) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'

export default {
  name: 'AssetDetail',
  setup() {
    const route = useRoute()
    const loading = ref(false)
    const assetData = ref(null)

    const getStatusClass = (status) => {
      const statusMap = {
        'Active': 'success',
        'Inactive': 'warning',
        'Damaged': 'danger',
        'Retired': 'secondary'
      }
      return statusMap[status] || 'secondary'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    const loadAsset = async () => {
      loading.value = true
      try {
        const response = await api.get(`/api/resource/Asset/${route.params.id}`)
        assetData.value = response.data.data
      } catch (error) {
        console.error('Failed to load asset:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadAsset()
    })

    return {
      loading,
      assetData,
      getStatusClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.asset-detail h1 {
  font-size: 24px;
  margin: 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: #666;
  min-width: 140px;
}

.detail-value {
  color: #333;
  word-break: break-word;
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

.badge-secondary {
  background-color: #f5f5f5;
  color: #666;
}

@media (max-width: 768px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }

  .detail-row {
    flex-direction: column;
    gap: 4px;
  }
}
</style>

