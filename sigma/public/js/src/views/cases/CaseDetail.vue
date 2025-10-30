<template>
  <div class="case-detail">
    <div class="flex-between mb-3">
      <h1>{{ caseData?.name }}</h1>
      <router-link to="/cases" class="btn btn-outline">
        ← Back to Cases
      </router-link>
    </div>

    <div v-if="loading" class="text-center p-3">Loading...</div>
    <div v-else-if="!caseData" class="alert alert-danger">
      Case not found
    </div>
    <div v-else class="grid grid-2">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Case Information</h2>
        </div>
        <div class="card-body p-3">
          <div class="detail-row">
            <span class="detail-label">Case ID:</span>
            <span class="detail-value">{{ caseData.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Title:</span>
            <span class="detail-value">{{ caseData.title }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span :class="['badge', `badge-${getStatusClass(caseData.status)}`]">
              {{ caseData.status }}
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Priority:</span>
            <span class="detail-value">{{ caseData.priority || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Assigned To:</span>
            <span class="detail-value">{{ caseData.assigned_to || 'Unassigned' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Created:</span>
            <span class="detail-value">{{ formatDate(caseData.creation) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Modified:</span>
            <span class="detail-value">{{ formatDate(caseData.modified) }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Description</h2>
        </div>
        <div class="card-body p-3">
          <p>{{ caseData.description || 'No description provided' }}</p>
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
  name: 'CaseDetail',
  setup() {
    const route = useRoute()
    const loading = ref(false)
    const caseData = ref(null)

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

    const loadCase = async () => {
      loading.value = true
      try {
        const response = await api.get(`/api/resource/Case/${route.params.id}`)
        caseData.value = response.data.data
      } catch (error) {
        console.error('Failed to load case:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadCase()
    })

    return {
      loading,
      caseData,
      getStatusClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.case-detail h1 {
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

.badge-warning {
  background-color: #fff3e0;
  color: #f57c00;
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

