<template>
  <div class="case-list">
    <div class="flex-between mb-3">
      <h1>Cases</h1>
      <router-link to="/cases/new" class="btn btn-primary">
        + New Case
      </router-link>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="filters mb-3">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search cases..."
            class="search-input"
          />
          <select v-model="filterStatus" class="filter-select">
            <option value="">All Status</option>
            <option value="Open">Open</option>
            <option value="In Progress">In Progress</option>
            <option value="Closed">Closed</option>
            <option value="On Hold">On Hold</option>
          </select>
        </div>

        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="filteredCases.length === 0" class="text-center p-3 text-muted">
          No cases found
        </div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th @click="sortBy('name')" class="sortable">
                Case ID
                <span v-if="sortField === 'name'" class="sort-icon">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th @click="sortBy('title')" class="sortable">
                Title
                <span v-if="sortField === 'title'" class="sort-icon">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th @click="sortBy('status')" class="sortable">
                Status
                <span v-if="sortField === 'status'" class="sort-icon">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th @click="sortBy('modified')" class="sortable">
                Modified
                <span v-if="sortField === 'modified'" class="sort-icon">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="case_ in paginatedCases" :key="case_.name">
              <td>{{ case_.name }}</td>
              <td>{{ case_.title }}</td>
              <td>
                <span :class="['badge', `badge-${getStatusClass(case_.status)}`]">
                  {{ case_.status }}
                </span>
              </td>
              <td>{{ formatDate(case_.modified) }}</td>
              <td>
                <router-link :to="`/cases/${case_.name}`" class="btn btn-sm btn-outline">
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
  name: 'CaseList',
  setup() {
    const loading = ref(false)
    const cases = ref([])
    const searchQuery = ref('')
    const filterStatus = ref('')
    const sortField = ref('modified')
    const sortOrder = ref('desc')
    const currentPage = ref(1)
    const pageSize = ref(10)

    const filteredCases = computed(() => {
      let filtered = cases.value

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(c =>
          c.name.toLowerCase().includes(query) ||
          c.title.toLowerCase().includes(query)
        )
      }

      if (filterStatus.value) {
        filtered = filtered.filter(c => c.status === filterStatus.value)
      }

      // Sort
      filtered.sort((a, b) => {
        let aVal = a[sortField.value]
        let bVal = b[sortField.value]

        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase()
          bVal = bVal.toLowerCase()
        }

        if (sortOrder.value === 'asc') {
          return aVal > bVal ? 1 : -1
        } else {
          return aVal < bVal ? 1 : -1
        }
      })

      return filtered
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredCases.value.length / pageSize.value)
    })

    const paginatedCases = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredCases.value.slice(start, end)
    })

    const getStatusClass = (status) => {
      const statusMap = {
        'Open': 'primary',
        'In Progress': 'info',
        'Closed': 'success',
        'On Hold': 'warning'
      }
      return statusMap[status] || 'secondary'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const sortBy = (field) => {
      if (sortField.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortField.value = field
        sortOrder.value = 'asc'
      }
    }

    const loadCases = async () => {
      loading.value = true
      try {
        const response = await api.get('/api/resource/Case?fields=["name","title","status","modified"]&limit_page_length=500')
        cases.value = response.data.data || []
      } catch (error) {
        console.error('Failed to load cases:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadCases()
    })

    return {
      loading,
      cases,
      searchQuery,
      filterStatus,
      sortField,
      sortOrder,
      currentPage,
      pageSize,
      filteredCases,
      paginatedCases,
      totalPages,
      getStatusClass,
      formatDate,
      sortBy
    }
  }
}
</script>

<style scoped>
.case-list h1 {
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

.sortable {
  cursor: pointer;
  user-select: none;
  padding: 12px;
  position: relative;
}

.sortable:hover {
  background-color: #f9f9f9;
}

.sort-icon {
  margin-left: 4px;
  font-size: 10px;
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

.badge-warning {
  background-color: #fff3e0;
  color: #f57c00;
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

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }

  .table {
    font-size: 12px;
  }

  .table th,
  .table td {
    padding: 8px;
  }
}
</style>

