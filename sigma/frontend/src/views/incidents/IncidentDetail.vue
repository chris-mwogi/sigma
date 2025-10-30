<template>
  <div class="incident-detail">
    <div class="flex-between mb-3">
      <h1>{{ incidentData?.name }}</h1>
      <router-link to="/incidents" class="btn btn-outline">
        ← Back
      </router-link>
    </div>

    <div v-if="loading" class="text-center p-3">Loading...</div>
    <div v-else-if="!incidentData" class="alert alert-danger">
      Incident not found
    </div>
    <div v-else class="card">
      <div class="card-body p-3">
        <div class="detail-row">
          <span class="detail-label">Incident ID:</span>
          <span class="detail-value">{{ incidentData.name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Title:</span>
          <span class="detail-value">{{ incidentData.title }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Date:</span>
          <span class="detail-value">{{ formatDate(incidentData.incident_date) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Status:</span>
          <span :class="['badge', `badge-${getStatusClass(incidentData.status)}`]">
            {{ incidentData.status }}
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Description:</span>
          <span class="detail-value">{{ incidentData.description || 'N/A' }}</span>
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
  name: 'IncidentDetail',
  setup() {
    const route = useRoute()
    const loading = ref(false)
    const incidentData = ref(null)

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

    const loadIncident = async () => {
      loading.value = true
      try {
        const response = await api.get(`/api/resource/Incident Report/${route.params.id}`)
        incidentData.value = response.data.data
      } catch (error) {
        console.error('Failed to load incident:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadIncident()
    })

    return {
      loading,
      incidentData,
      getStatusClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.incident-detail h1 {
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
  min-width: 120px;
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
</style>

