<template>
  <div class="incident-list">
    <div class="flex-between mb-3">
      <h1>Incident Reports</h1>
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
            placeholder="Search incidents..."
            class="search-input"
          />
        </div>

        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="filteredIncidents.length === 0" class="text-center p-3 text-muted">
          No incidents found
        </div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>Incident ID</th>
              <th>Title</th>
              <th>Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="incident in paginatedIncidents" :key="incident.name">
              <td>{{ incident.name }}</td>
              <td>{{ incident.title }}</td>
              <td>{{ formatDate(incident.incident_date) }}</td>
              <td>
                <span :class="['badge', `badge-${getStatusClass(incident.status)}`]">
                  {{ incident.status }}
                </span>
              </td>
              <td>
                <router-link :to="`/incidents/${incident.name}`" class="btn btn-sm btn-outline">
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
  name: 'IncidentList',
  setup() {
    const loading = ref(false)
    const incidents = ref([])
    const searchQuery = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)

    const filteredIncidents = computed(() => {
      if (!searchQuery.value) return incidents.value

      const query = searchQuery.value.toLowerCase()
      return incidents.value.filter(i =>
        i.name.toLowerCase().includes(query) ||
        i.title.toLowerCase().includes(query)
      )
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredIncidents.value.length / pageSize.value)
    })

    const paginatedIncidents = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredIncidents.value.slice(start, end)
    })

    const getStatusClass = (status) => {
      const statusMap = {
        'Open': 'primary',
        'In Progress': 'info',
        'Resolved': 'success',
        'Closed': 'success'
      }
      return statusMap[status] || 'secondary'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const loadIncidents = async () => {
      loading.value = true
      try {
        const response = await api.get('/api/resource/Incident Report?fields=["name","title","incident_date","status"]&limit_page_length=500')
        incidents.value = response.data.data || []
      } catch (error) {
        console.error('Failed to load incidents:', error)
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadIncidents()
    }

    onMounted(() => {
      loadIncidents()
    })

    return {
      loading,
      incidents,
      searchQuery,
      currentPage,
      pageSize,
      filteredIncidents,
      paginatedIncidents,
      totalPages,
      getStatusClass,
      formatDate,
      refreshData
    }
  }
}
</script>

<style scoped>
.incident-list h1 {
  font-size: 24px;
  margin: 0;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input:focus {
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

.badge-primary {
  background-color: #e3f2fd;
  color: #1976d2;
}

.badge-info {
  background-color: #e0f2f1;
  color: #00897b;
}

.badge-success {
  background-color: #e8f5e9;
  color: #388e3c;
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

