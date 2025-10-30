<template>
  <div class="access-control">
    <h1>Access Control Management</h1>

    <div class="grid grid-3 mt-3">
      <div class="module-card">
        <div class="module-icon">🔑</div>
        <h3>Access Events</h3>
        <p>Monitor and manage access events</p>
        <button @click="loadAccessEvents" class="btn btn-primary btn-sm">
          View Events
        </button>
      </div>

      <div class="module-card">
        <div class="module-icon">🚪</div>
        <h3>Access Points</h3>
        <p>Manage access points and entry points</p>
        <button @click="loadAccessPoints" class="btn btn-primary btn-sm">
          View Points
        </button>
      </div>

      <div class="module-card">
        <div class="module-icon">📋</div>
        <h3>Access Policies</h3>
        <p>Configure access control policies</p>
        <button @click="loadAccessPolicies" class="btn btn-primary btn-sm">
          View Policies
        </button>
      </div>
    </div>

    <div v-if="selectedModule" class="card mt-3">
      <div class="card-header">
        <h2 class="card-title">{{ selectedModule }}</h2>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="data.length === 0" class="text-center p-3 text-muted">
          No data found
        </div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in data" :key="item.name">
              <td>{{ item.name }}</td>
              <td>{{ item.title || item.name }}</td>
              <td>
                <span class="badge badge-success">Active</span>
              </td>
              <td>{{ formatDate(item.creation) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import api from '../../services/api'

export default {
  name: 'AccessControl',
  setup() {
    const loading = ref(false)
    const selectedModule = ref('')
    const data = ref([])

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const loadAccessEvents = async () => {
      loading.value = true
      selectedModule.value = 'Access Events'
      try {
        const response = await api.get('/api/resource/Access Event?fields=["name","title","creation"]&limit_page_length=100')
        data.value = response.data.data || []
      } catch (error) {
        console.error('Failed to load access events:', error)
      } finally {
        loading.value = false
      }
    }

    const loadAccessPoints = async () => {
      loading.value = true
      selectedModule.value = 'Access Points'
      try {
        const response = await api.get('/api/resource/Access Point?fields=["name","title","creation"]&limit_page_length=100')
        data.value = response.data.data || []
      } catch (error) {
        console.error('Failed to load access points:', error)
      } finally {
        loading.value = false
      }
    }

    const loadAccessPolicies = async () => {
      loading.value = true
      selectedModule.value = 'Access Policies'
      try {
        const response = await api.get('/api/resource/Access Policy?fields=["name","title","creation"]&limit_page_length=100')
        data.value = response.data.data || []
      } catch (error) {
        console.error('Failed to load access policies:', error)
      } finally {
        loading.value = false
      }
    }

    return {
      loading,
      selectedModule,
      data,
      formatDate,
      loadAccessEvents,
      loadAccessPoints,
      loadAccessPolicies
    }
  }
}
</script>

<style scoped>
.access-control h1 {
  font-size: 24px;
  margin: 0;
}

.module-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.module-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.module-card h3 {
  font-size: 16px;
  margin: 12px 0;
  color: #1a1a1a;
}

.module-card p {
  font-size: 12px;
  color: #666;
  margin: 8px 0 16px 0;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table thead {
  background-color: #f9f9f9;
  border-bottom: 2px solid #ddd;
}

.table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
}

.table td {
  padding: 12px;
  border-bottom: 1px solid #ddd;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background-color: #e8f5e9;
  color: #388e3c;
}
</style>

