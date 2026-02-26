<template>
  <div class="case-detail">
    <div class="flex-between mb-3">
      <div>
        <router-link to="/cases" class="text-muted">← Back to Cases</router-link>
        <h1>{{ caseData.case_title || caseData.name }}</h1>
      </div>
      <div class="header-actions">
        <button @click="refreshData" class="btn btn-outline">🔄 Refresh</button>
      </div>
    </div>

    <div v-if="loading" class="text-center p-5">Loading...</div>
    <div v-else class="case-content">
      <div class="card mb-3">
        <div class="card-header"><h3>📋 Case Information</h3></div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item"><label>Case ID</label><span>{{ caseData.name }}</span></div>
            <div class="info-item"><label>Status</label><span :class="['badge', `badge-${getStatusClass(caseData.status)}`]">{{ caseData.status }}</span></div>
            <div class="info-item"><label>Type</label><span>{{ caseData.case_type }}</span></div>
            <div class="info-item"><label>Severity</label><span :class="['badge', `badge-${getSeverityClass(caseData.severity_level)}`]">{{ caseData.severity_level }}</span></div>
            <div class="info-item"><label>Assigned To</label><span>{{ caseData.assigned_to || '-' }}</span></div>
            <div class="info-item"><label>Region</label><span>{{ caseData.region || '-' }}</span></div>
            <div class="info-item"><label>Created</label><span>{{ formatDate(caseData.creation) }}</span></div>
            <div class="info-item"><label>Modified</label><span>{{ formatDate(caseData.modified) }}</span></div>
          </div>
        </div>
      </div>

      <div class="card mb-3">
        <div class="card-header"><h3>📝 Description</h3></div>
        <div class="card-body">
          <p>{{ caseData.description || 'No description provided.' }}</p>
        </div>
      </div>

      <div class="card mb-3">
        <div class="card-header"><h3>📎 Related Information</h3></div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item"><label>Related Incident</label><span>{{ caseData.related_incident || '-' }}</span></div>
            <div class="info-item"><label>Reporter</label><span>{{ caseData.reporter || caseData.reported_by || '-' }}</span></div>
            <div class="info-item"><label>Report Date</label><span>{{ formatDate(caseData.report_date) }}</span></div>
            <div class="info-item"><label>SLA Due Date</label><span>{{ formatDate(caseData.sla_due_date) }}</span></div>
          </div>
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
    const loading = ref(true)
    const caseData = ref({})

    const getStatusClass = s => ({ 'Open': 'warning', 'In Progress': 'info', 'Under Investigation': 'primary', 'Closed': 'success' }[s] || 'secondary')
    const getSeverityClass = s => ({ 'Critical': 'danger', 'High': 'warning', 'Medium': 'info', 'Low': 'success' }[s] || 'secondary')
    const formatDate = d => d ? new Date(d).toLocaleDateString() : '-'

    const loadCase = async () => {
      loading.value = true
      try {
        const r = await api.get(`/api/resource/Sigma Case/${route.params.id}`)
        caseData.value = r.data.data || {}
      } catch (e) { console.error('Failed to load case:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => loadCase()
    onMounted(loadCase)

    return { loading, caseData, getStatusClass, getSeverityClass, formatDate, refreshData }
  }
}
</script>

<style scoped>
.case-detail h1 { font-size: 24px; margin: 8px 0 0 0; }
.header-actions { display: flex; gap: 8px; }
.case-content { display: flex; flex-direction: column; gap: 16px; }
.card-header { background: #f8f9fa; padding: 12px 16px; border-bottom: 1px solid #e9ecef; }
.card-header h3 { margin: 0; font-size: 16px; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.info-item { display: flex; flex-direction: column; }
.info-item label { font-size: 12px; color: #666; margin-bottom: 4px; text-transform: uppercase; }
.info-item span { font-size: 14px; color: #333; }
.badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; width: fit-content; }
.badge-success { background: #e8f5e9; color: #388e3c; }
.badge-warning { background: #fff3e0; color: #f57c00; }
.badge-danger { background: #ffebee; color: #c62828; }
.badge-info { background: #e3f2fd; color: #1976d2; }
.badge-primary { background: #e8eaf6; color: #3f51b5; }
.badge-secondary { background: #f5f5f5; color: #666; }
</style>

