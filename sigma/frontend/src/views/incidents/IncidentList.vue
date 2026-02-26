<template>
  <div class="incident-list">
    <div class="flex-between mb-3">
      <h1>🚨 Incidents</h1>
      <button @click="refreshData" class="btn btn-outline">🔄 Refresh</button>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="filters mb-3">
          <input v-model="searchQuery" type="text" placeholder="Search incidents..." class="search-input" />
          <select v-model="filterStatus" class="filter-select">
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Investigating">Investigating</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
          </select>
          <select v-model="filterSeverity" class="filter-select">
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="filteredIncidents.length === 0" class="text-center p-3 text-muted">No incidents found</div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Type</th>
              <th>Status</th>
              <th>Severity</th>
              <th>Location</th>
              <th>Reported</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="i in paginatedIncidents" :key="i.name">
              <td>{{ i.name }}</td>
              <td>{{ i.incident_title || i.subject }}</td>
              <td>{{ i.incident_type }}</td>
              <td><span :class="['badge', `badge-${getStatusClass(i.status)}`]">{{ i.status }}</span></td>
              <td><span :class="['badge', `badge-${getSeverityClass(i.severity)}`]">{{ i.severity }}</span></td>
              <td>{{ i.location || '-' }}</td>
              <td>{{ formatDate(i.creation) }}</td>
              <td><router-link :to="`/incidents/${i.name}`" class="btn btn-sm btn-outline">View</router-link></td>
            </tr>
          </tbody>
        </table>

        <div v-if="totalPages > 1" class="pagination mt-3">
          <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage === 1" class="btn btn-sm">Previous</button>
          <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
          <button @click="currentPage = Math.min(totalPages, currentPage + 1)" :disabled="currentPage === totalPages" class="btn btn-sm">Next</button>
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
    const filterStatus = ref('')
    const filterSeverity = ref('')
    const currentPage = ref(1)
    const pageSize = ref(15)

    const filteredIncidents = computed(() => {
      let filtered = incidents.value
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        filtered = filtered.filter(i => i.name.toLowerCase().includes(q) || (i.incident_title || '').toLowerCase().includes(q))
      }
      if (filterStatus.value) filtered = filtered.filter(i => i.status === filterStatus.value)
      if (filterSeverity.value) filtered = filtered.filter(i => i.severity === filterSeverity.value)
      return filtered
    })

    const totalPages = computed(() => Math.ceil(filteredIncidents.value.length / pageSize.value))
    const paginatedIncidents = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      return filteredIncidents.value.slice(start, start + pageSize.value)
    })

    const getStatusClass = s => ({ 'Open': 'warning', 'Investigating': 'info', 'Resolved': 'success', 'Closed': 'secondary' }[s] || 'secondary')
    const getSeverityClass = s => ({ 'Critical': 'danger', 'High': 'warning', 'Medium': 'info', 'Low': 'success' }[s] || 'secondary')
    const formatDate = d => d ? new Date(d).toLocaleDateString() : '-'

    const loadIncidents = async () => {
      loading.value = true
      try {
        const r = await api.get('/api/resource/Incident?fields=["name","incident_title","subject","incident_type","status","severity","location","creation"]&limit_page_length=500')
        incidents.value = r.data.data || []
      } catch (e) { console.error('Failed to load incidents:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => loadIncidents()
    onMounted(loadIncidents)

    return { loading, incidents, searchQuery, filterStatus, filterSeverity, currentPage, pageSize, filteredIncidents, paginatedIncidents, totalPages, getStatusClass, getSeverityClass, formatDate, refreshData }
  }
}
</script>

<style scoped>
.incident-list h1 { font-size: 24px; margin: 0; }
.filters { display: flex; gap: 12px; flex-wrap: wrap; }
.search-input, .filter-select { flex: 1; min-width: 150px; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.search-input:focus, .filter-select:focus { outline: none; border-color: #0084ff; }
.badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.badge-success { background: #e8f5e9; color: #388e3c; }
.badge-warning { background: #fff3e0; color: #f57c00; }
.badge-danger { background: #ffebee; color: #c62828; }
.badge-info { background: #e3f2fd; color: #1976d2; }
.badge-secondary { background: #f5f5f5; color: #666; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 12px; }
.page-info { font-size: 14px; color: #666; }
</style>

