<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <div>
        <h1>Dashboard</h1>
        <p class="subtitle">Welcome to Kenya Power Security Management System</p>
      </div>
    </div>

    <div class="grid grid-4">
      <div class="stat-card stat-card-primary">
        <div class="stat-icon">
          <span>📋</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.cases }}</div>
          <div class="stat-label">Active Cases</div>
        </div>
      </div>

      <div class="stat-card stat-card-warning">
        <div class="stat-icon">
          <span>⚠️</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.incidents }}</div>
          <div class="stat-label">Incidents</div>
        </div>
      </div>

      <div class="stat-card stat-card-accent">
        <div class="stat-icon">
          <span>🔐</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.accessEvents }}</div>
          <div class="stat-label">Access Events</div>
        </div>
      </div>

      <div class="stat-card stat-card-success">
        <div class="stat-icon">
          <span>👮</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.guardShifts }}</div>
          <div class="stat-label">Guard Shifts</div>
        </div>
      </div>
    </div>

    <div class="grid grid-2 mt-3">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Recent Cases</h2>
        </div>
        <div class="card-body">
          <div v-if="loading" class="text-center p-3">Loading...</div>
          <div v-else-if="recentCases.length === 0" class="text-center p-3 text-muted">
            No cases found
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Title</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="case_ in recentCases" :key="case_.name">
                <td>{{ case_.name }}</td>
                <td>{{ case_.title }}</td>
                <td>
                  <span :class="['badge', `badge-${getStatusClass(case_.status)}`]">
                    {{ case_.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Quick Actions</h2>
        </div>
        <div class="card-body p-3">
          <div class="action-list">
            <router-link to="/cases/new" class="action-item">
              <span class="action-icon">➕</span>
              <span>Create New Case</span>
            </router-link>
            <router-link to="/incidents" class="action-item">
              <span class="action-icon">📝</span>
              <span>View Incidents</span>
            </router-link>
            <router-link to="/access-control" class="action-item">
              <span class="action-icon">🔑</span>
              <span>Access Control</span>
            </router-link>
            <router-link to="/guard-monitoring" class="action-item">
              <span class="action-icon">📍</span>
              <span>Guard Monitoring</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'Dashboard',
  setup() {
    const loading = ref(false)
    const stats = ref({
      cases: 0,
      incidents: 0,
      accessEvents: 0,
      guardShifts: 0
    })
    const recentCases = ref([])

    const getStatusClass = (status) => {
      const statusMap = {
        'Open': 'primary',
        'In Progress': 'info',
        'Closed': 'success',
        'On Hold': 'warning'
      }
      return statusMap[status] || 'secondary'
    }

    const loadDashboardData = async () => {
      loading.value = true
      try {
        // Load statistics
        const casesResponse = await api.get('/api/resource/Case?fields=["name"]&limit_page_length=1')
        const incidentsResponse = await api.get('/api/resource/Incident Report?fields=["name"]&limit_page_length=1')
        const accessResponse = await api.get('/api/resource/Access Event?fields=["name"]&limit_page_length=1')
        const shiftsResponse = await api.get('/api/resource/Guard Shift?fields=["name"]&limit_page_length=1')

        stats.value.cases = casesResponse.data.data?.length || 0
        stats.value.incidents = incidentsResponse.data.data?.length || 0
        stats.value.accessEvents = accessResponse.data.data?.length || 0
        stats.value.guardShifts = shiftsResponse.data.data?.length || 0

        // Load recent cases
        const recentResponse = await api.get('/api/resource/Case?fields=["name","title","status"]&limit_page_length=5&order_by=`modified` desc')
        recentCases.value = recentResponse.data.data || []
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadDashboardData()
    })

    return {
      loading,
      stats,
      recentCases,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px 0;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.dashboard h1 {
  font-size: 32px;
  margin: 0 0 8px 0;
  color: #00337F;
  font-weight: 700;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.stat-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border-left: 4px solid;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.5) 0%, transparent 70%);
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.stat-card-primary {
  border-left-color: #00337F;
}

.stat-card-primary .stat-icon {
  background-color: #e8f0f8;
  color: #00337F;
}

.stat-card-warning {
  border-left-color: #F39200;
}

.stat-card-warning .stat-icon {
  background-color: #fff8e8;
  color: #F39200;
}

.stat-card-accent {
  border-left-color: #00A651;
}

.stat-card-accent .stat-icon {
  background-color: #e8f8f0;
  color: #00A651;
}

.stat-card-success {
  border-left-color: #28a745;
}

.stat-card-success .stat-icon {
  background-color: #e8f5e9;
  color: #28a745;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #00337F;
}

.stat-label {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
  font-weight: 500;
}

.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.badge-primary {
  background-color: #e8f0f8;
  color: #00337F;
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
  background-color: #fff8e8;
  color: #F39200;
}

.badge-secondary {
  background-color: #f5f5f5;
  color: #666;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 8px;
  background-color: #f8f9fa;
  color: #00337F;
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  font-weight: 500;
}

.action-item:hover {
  background-color: #e8f0f8;
  transform: translateX(4px);
  border-left-color: #00337F;
}

.action-icon {
  font-size: 20px;
}

@media (max-width: 768px) {
  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }

  .stat-value {
    font-size: 20px;
  }
}
</style>

