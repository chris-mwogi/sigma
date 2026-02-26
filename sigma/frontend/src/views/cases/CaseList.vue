<template>
  <div class="case-list">
    <div class="flex-between mb-3">
      <h1>📁 Cases</h1>
      <div class="header-actions">
        <router-link to="/cases/new" class="btn btn-primary">+ New Case</router-link>
        <button @click="refreshData" class="btn btn-outline">🔄 Refresh</button>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="filters mb-3">
          <input v-model="searchQuery" type="text" placeholder="Search cases..." class="search-input" />
          <select v-model="filterStatus" class="filter-select">
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="In Progress">In Progress</option>
            <option value="Under Investigation">Under Investigation</option>
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
        <div v-else-if="filteredCases.length === 0" class="text-center p-3 text-muted">No cases found</div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Title</th>
              <th>Type</th>
              <th>Status</th>
              <th>Severity</th>
              <th>Assigned To</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in paginatedCases" :key="c.name">
              <td>{{ c.name }}</td>
              <td>{{ c.case_title || c.subject }}</td>
              <td>{{ c.case_type }}</td>
              <td><span :class="['badge', `badge-${getStatusClass(c.status)}`]">{{ c.status }}</span></td>
              <td><span :class="['badge', `badge-${getSeverityClass(c.severity_level)}`]">{{ c.severity_level }}</span></td>
              <td>{{ c.assigned_to || '-' }}</td>
              <td>{{ formatDate(c.creation) }}</td>
              <td><router-link :to="`/cases/${c.name}`" class="btn btn-sm btn-outline">View</router-link></td>
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
  name: 'CaseList',
  setup() {
    const loading = ref(false)
    const cases = ref([])
    const searchQuery = ref('')
    const filterStatus = ref('')
    const filterSeverity = ref('')
    const currentPage = ref(1)
    const pageSize = ref(15)

    const filteredCases = computed(() => {
      let filtered = cases.value
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        filtered = filtered.filter(c => c.name.toLowerCase().includes(q) || (c.case_title || '').toLowerCase().includes(q))
      }
      if (filterStatus.value) filtered = filtered.filter(c => c.status === filterStatus.value)
      if (filterSeverity.value) filtered = filtered.filter(c => c.severity_level === filterSeverity.value)
      return filtered
    })

    const totalPages = computed(() => Math.ceil(filteredCases.value.length / pageSize.value))
    const paginatedCases = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      return filteredCases.value.slice(start, start + pageSize.value)
    })

    const getStatusClass = s => ({ 'Open': 'warning', 'In Progress': 'info', 'Under Investigation': 'primary', 'Closed': 'success' }[s] || 'secondary')
    const getSeverityClass = s => ({ 'Critical': 'danger', 'High': 'warning', 'Medium': 'info', 'Low': 'success' }[s] || 'secondary')
    const formatDate = d => d ? new Date(d).toLocaleDateString() : '-'

    const loadCases = async () => {
      loading.value = true
      try {
        const r = await api.get('/api/resource/Sigma Case?fields=["name","case_title","subject","case_type","status","severity_level","assigned_to","creation"]&limit_page_length=500')
        cases.value = r.data.data || []
      } catch (e) { console.error('Failed to load cases:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => loadCases()
    onMounted(loadCases)

    return { loading, cases, searchQuery, filterStatus, filterSeverity, currentPage, pageSize, filteredCases, paginatedCases, totalPages, getStatusClass, getSeverityClass, formatDate, refreshData }
  }
}
</script>

<style scoped>
.case-list h1 { font-size: 24px; margin: 0; }
.header-actions { display: flex; gap: 8px; }
.filters { display: flex; gap: 12px; flex-wrap: wrap; }
.search-input, .filter-select { flex: 1; min-width: 150px; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.search-input:focus, .filter-select:focus { outline: none; border-color: #0084ff; }
.badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.badge-success { background: #e8f5e9; color: #388e3c; }
.badge-warning { background: #fff3e0; color: #f57c00; }
.badge-danger { background: #ffebee; color: #c62828; }
.badge-info { background: #e3f2fd; color: #1976d2; }
.badge-primary { background: #e8eaf6; color: #3f51b5; }
.badge-secondary { background: #f5f5f5; color: #666; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 12px; }
.page-info { font-size: 14px; color: #666; }
</style>

