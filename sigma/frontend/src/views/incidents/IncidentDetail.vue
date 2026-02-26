<template>
  <div class="incident-detail">
    <div class="flex-between mb-3">
      <div>
        <router-link to="/incidents" class="text-muted">← Back to Incidents</router-link>
        <h1>{{ incident.incident_title || incident.name }}</h1>
      </div>
      <button @click="refreshData" class="btn btn-outline">🔄 Refresh</button>
    </div>

    <div v-if="loading" class="text-center p-5">Loading...</div>
    <div v-else class="incident-content">
      <div class="card mb-3">
        <div class="card-header"><h3>🚨 Incident Information</h3></div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item"><label>Incident ID</label><span>{{ incident.name }}</span></div>
            <div class="info-item"><label>Status</label><span :class="['badge', `badge-${getStatusClass(incident.status)}`]">{{ incident.status }}</span></div>
            <div class="info-item"><label>Type</label><span>{{ incident.incident_type }}</span></div>
            <div class="info-item"><label>Severity</label><span :class="['badge', `badge-${getSeverityClass(incident.severity)}`]">{{ incident.severity }}</span></div>
            <div class="info-item"><label>Location</label><span>{{ incident.location || '-' }}</span></div>
            <div class="info-item"><label>Zone</label><span>{{ incident.zone || '-' }}</span></div>
            <div class="info-item"><label>Reported By</label><span>{{ incident.reported_by || '-' }}</span></div>
            <div class="info-item"><label>Reported At</label><span>{{ formatDateTime(incident.creation) }}</span></div>
          </div>
        </div>
      </div>

      <div class="card mb-3">
        <div class="card-header"><h3>📝 Description</h3></div>
        <div class="card-body">
          <p>{{ incident.description || 'No description provided.' }}</p>
        </div>
      </div>

      <div class="card mb-3">
        <div class="card-header"><h3>🔍 Investigation Details</h3></div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item"><label>Assigned To</label><span>{{ incident.assigned_to || '-' }}</span></div>
            <div class="info-item"><label>Resolution</label><span>{{ incident.resolution || '-' }}</span></div>
            <div class="info-item"><label>Resolved At</label><span>{{ formatDateTime(incident.resolved_at) }}</span></div>
            <div class="info-item"><label>Related Case</label><span>{{ incident.related_case || '-' }}</span></div>
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
  name: 'IncidentDetail',
  setup() {
    const route = useRoute()
    const loading = ref(true)
    const incident = ref({})

    const getStatusClass = s => ({ 'Open': 'warning', 'Investigating': 'info', 'Resolved': 'success', 'Closed': 'secondary' }[s] || 'secondary')
    const getSeverityClass = s => ({ 'Critical': 'danger', 'High': 'warning', 'Medium': 'info', 'Low': 'success' }[s] || 'secondary')
    const formatDateTime = d => d ? new Date(d).toLocaleString() : '-'

    const loadIncident = async () => {
      loading.value = true
      try {
        const r = await api.get(`/api/resource/Incident/${route.params.id}`)
        incident.value = r.data.data || {}
      } catch (e) { console.error('Failed to load incident:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => loadIncident()
    onMounted(loadIncident)

    return { loading, incident, getStatusClass, getSeverityClass, formatDateTime, refreshData }
  }
}
</script>

<style scoped>
.incident-detail h1 { font-size: 24px; margin: 8px 0 0 0; }
.incident-content { display: flex; flex-direction: column; gap: 16px; }
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
.badge-secondary { background: #f5f5f5; color: #666; }
</style>

