<template>
  <div class="asset-list">
    <div class="flex-between mb-3">
      <h1>Assets</h1>
      <button @click="refreshData" class="btn btn-primary">
        🔄 Refresh
      </button>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="filters mb-3">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search assets..."
            class="search-input"
          />
          <select v-model="filterType" class="filter-select">
            <option value="">All Types</option>
            <option value="Equipment">Equipment</option>
            <option value="Vehicle">Vehicle</option>
            <option value="Property">Property</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="filteredAssets.length === 0" class="text-center p-3 text-muted">
          No assets found
        </div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>Asset ID</th>
              <th>Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Value</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="asset in paginatedAssets" :key="asset.name">
              <td>{{ asset.name }}</td>
              <td>{{ asset.asset_name }}</td>
              <td>{{ asset.asset_type }}</td>
              <td>
                <span :class="['badge', `badge-${getStatusClass(asset.status)}`]">
                  {{ asset.status }}
                </span>
              </td>
              <td>${{ asset.asset_value || '0' }}</td>
              <td>
                <router-link :to="`/assets/${asset.name}`" class="btn btn-sm btn-outline">
                  View
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="totalPages > 1" class="pagination mt-3">
          <button
            @click="currentPage = Math.max(1, currentPage - 1)"
            :disabled="currentPage === 1"
            class="btn btn-sm"
          >
            Previous
          </button>
          <span class="page-info">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          <button
            @click="currentPage = Math.min(totalPages, currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="btn btn-sm"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

export default {
  name: 'AssetList',
  setup() {
    const loading = ref(false)
    const assets = ref([])
    const searchQuery = ref('')
    const filterType = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)

    const filteredAssets = computed(() => {
      let filtered = assets.value

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(a =>
          a.name.toLowerCase().includes(query) ||
          a.asset_name.toLowerCase().includes(query)
        )
      }

      if (filterType.value) {
        filtered = filtered.filter(a => a.asset_type === filterType.value)
      }

      return filtered
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredAssets.value.length / pageSize.value)
    })

    const paginatedAssets = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredAssets.value.slice(start, end)
    })

    const getStatusClass = (status) => {
      const statusMap = {
        'Active': 'success',
        'Inactive': 'warning',
        'Damaged': 'danger',
        'Retired': 'secondary'
      }
      return statusMap[status] || 'secondary'
    }

    const loadAssets = async () => {
      loading.value = true
      try {
        const response = await api.get('/api/resource/Asset?fields=["name","asset_name","asset_type","status","asset_value"]&limit_page_length=500')
        assets.value = response.data.data || []
      } catch (error) {
        console.error('Failed to load assets:', error)
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadAssets()
    }

    onMounted(() => {
      loadAssets()
    })

    return {
      loading,
      assets,
      searchQuery,
      filterType,
      currentPage,
      pageSize,
      filteredAssets,
      paginatedAssets,
      totalPages,
      getStatusClass,
      refreshData
    }
  }
}
</script>

<style scoped>
.asset-list h1 {
  font-size: 24px;
  margin: 0;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input,
.filter-select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #0084ff;
  box-shadow: 0 0 0 3px rgba(0, 132, 255, 0.1);
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.page-info {
  font-size: 14px;
  color: #666;
}
</style>

