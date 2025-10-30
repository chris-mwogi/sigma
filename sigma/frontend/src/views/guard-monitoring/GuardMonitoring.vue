<template>
  <div class="guard-monitoring">
    <h1>Guard Monitoring</h1>

    <div class="grid grid-3 mt-3">
      <div class="stat-card">
        <div class="stat-icon">👮</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalGuards }}</div>
          <div class="stat-label">Total Guards</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.onDuty }}</div>
          <div class="stat-label">On Duty</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">⏸️</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.offDuty }}</div>
          <div class="stat-label">Off Duty</div>
        </div>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-header">
        <h2 class="card-title">Guard Shifts</h2>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="shifts.length === 0" class="text-center p-3 text-muted">
          No shifts found
        </div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>Guard Name</th>
              <th>Shift Date</th>
              <th>Start Time</th>
              <th>End Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="shift in shifts" :key="shift.name">
              <td>{{ shift.guard_name }}</td>
              <td>{{ formatDate(shift.shift_date) }}</td>
              <td>{{ shift.start_time }}</td>
              <td>{{ shift.end_time }}</td>
              <td>
                <span :class="['badge', `badge-${getStatusClass(shift.status)}`]">
                  {{ shift.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

export default {
  name: 'GuardMonitoring',
  setup() {
    const loading = ref(false)
    const shifts = ref([])
    const stats = ref({
      totalGuards: 0,
      onDuty: 0,
      offDuty: 0
    })

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const getStatusClass = (status) => {
      const statusMap = {
        'Active': 'success',
        'Completed': 'info',
        'Cancelled': 'danger'
      }
      return statusMap[status] || 'secondary'
    }

    const loadGuardData = async () => {
      loading.value = true
      try {
        // Load shifts
        const shiftsResponse = await api.get('/api/resource/Guard Shift?fields=["name","guard_name","shift_date","start_time","end_time","status"]&limit_page_length=100')
        shifts.value = shiftsResponse.data.data || []

        // Calculate stats
        stats.value.totalGuards = new Set(shifts.value.map(s => s.guard_name)).size
        stats.value.onDuty = shifts.value.filter(s => s.status === 'Active').length
        stats.value.offDuty = shifts.value.filter(s => s.status !== 'Active').length
      } catch (error) {
        console.error('Failed to load guard data:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadGuardData()
    })

    return {
      loading,
      shifts,
      stats,
      formatDate,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.guard-monitoring h1 {
  font-size: 24px;
  margin: 0;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 32px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
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
}

.badge-success {
  background-color: #e8f5e9;
  color: #388e3c;
}

.badge-info {
  background-color: #e0f2f1;
  color: #00897b;
}

.badge-danger {
  background-color: #ffebee;
  color: #c62828;
}

.badge-secondary {
  background-color: #f5f5f5;
  color: #666;
}
</style>

