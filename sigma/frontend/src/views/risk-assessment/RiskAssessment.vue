<template>
  <div class="risk-assessment">
    <h1>Risk Assessment</h1>

    <div class="grid grid-4 mt-3">
      <div class="risk-card critical">
        <div class="risk-icon">🔴</div>
        <div class="risk-content">
          <div class="risk-value">{{ stats.critical }}</div>
          <div class="risk-label">Critical</div>
        </div>
      </div>

      <div class="risk-card high">
        <div class="risk-icon">🟠</div>
        <div class="risk-content">
          <div class="risk-value">{{ stats.high }}</div>
          <div class="risk-label">High</div>
        </div>
      </div>

      <div class="risk-card medium">
        <div class="risk-icon">🟡</div>
        <div class="risk-content">
          <div class="risk-value">{{ stats.medium }}</div>
          <div class="risk-label">Medium</div>
        </div>
      </div>

      <div class="risk-card low">
        <div class="risk-icon">🟢</div>
        <div class="risk-content">
          <div class="risk-value">{{ stats.low }}</div>
          <div class="risk-label">Low</div>
        </div>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-header">
        <h2 class="card-title">Risk Assessments</h2>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-3">Loading...</div>
        <div v-else-if="assessments.length === 0" class="text-center p-3 text-muted">
          No risk assessments found
        </div>
        <table v-else class="table table-striped">
          <thead>
            <tr>
              <th>Assessment ID</th>
              <th>Title</th>
              <th>Risk Level</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="assessment in assessments" :key="assessment.name">
              <td>{{ assessment.name }}</td>
              <td>{{ assessment.title }}</td>
              <td>
                <span :class="['badge', `badge-${getRiskClass(assessment.risk_level)}`]">
                  {{ assessment.risk_level }}
                </span>
              </td>
              <td>
                <span :class="['badge', `badge-${getStatusClass(assessment.status)}`]">
                  {{ assessment.status }}
                </span>
              </td>
              <td>{{ formatDate(assessment.assessment_date) }}</td>
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
  name: 'RiskAssessment',
  setup() {
    const loading = ref(false)
    const assessments = ref([])
    const stats = ref({
      critical: 0,
      high: 0,
      medium: 0,
      low: 0
    })

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const getRiskClass = (level) => {
      const riskMap = {
        'Critical': 'critical',
        'High': 'high',
        'Medium': 'medium',
        'Low': 'low'
      }
      return riskMap[level] || 'secondary'
    }

    const getStatusClass = (status) => {
      const statusMap = {
        'Open': 'primary',
        'In Progress': 'info',
        'Completed': 'success',
        'Closed': 'success'
      }
      return statusMap[status] || 'secondary'
    }

    const loadRiskAssessments = async () => {
      loading.value = true
      try {
        const response = await api.get('/api/resource/Risk Assessment?fields=["name","title","risk_level","status","assessment_date"]&limit_page_length=100')
        assessments.value = response.data.data || []

        // Calculate stats
        stats.value.critical = assessments.value.filter(a => a.risk_level === 'Critical').length
        stats.value.high = assessments.value.filter(a => a.risk_level === 'High').length
        stats.value.medium = assessments.value.filter(a => a.risk_level === 'Medium').length
        stats.value.low = assessments.value.filter(a => a.risk_level === 'Low').length
      } catch (error) {
        console.error('Failed to load risk assessments:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadRiskAssessments()
    })

    return {
      loading,
      assessments,
      stats,
      formatDate,
      getRiskClass,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.risk-assessment h1 {
  font-size: 24px;
  margin: 0;
}

.risk-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid;
}

.risk-card.critical {
  border-left-color: #dc3545;
}

.risk-card.high {
  border-left-color: #fd7e14;
}

.risk-card.medium {
  border-left-color: #ffc107;
}

.risk-card.low {
  border-left-color: #28a745;
}

.risk-icon {
  font-size: 32px;
}

.risk-content {
  flex: 1;
}

.risk-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}

.risk-label {
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

.badge-critical {
  background-color: #f8d7da;
  color: #721c24;
}

.badge-high {
  background-color: #fff3cd;
  color: #856404;
}

.badge-medium {
  background-color: #fff3cd;
  color: #856404;
}

.badge-low {
  background-color: #d4edda;
  color: #155724;
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

