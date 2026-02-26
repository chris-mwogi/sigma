<template>
  <div class="case-form">
    <div class="flex-between mb-3">
      <div>
        <router-link to="/cases" class="text-muted">← Back to Cases</router-link>
        <h1>📁 New Case</h1>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <form @submit.prevent="submitCase">
          <div class="form-grid">
            <div class="form-group">
              <label>Case Title *</label>
              <input v-model="form.case_title" type="text" class="form-control" required />
            </div>
            <div class="form-group">
              <label>Case Type *</label>
              <select v-model="form.case_type" class="form-control" required>
                <option value="">Select Type</option>
                <option value="Fraud">Fraud</option>
                <option value="Theft">Theft</option>
                <option value="Misconduct">Misconduct</option>
                <option value="Safety">Safety</option>
                <option value="Complaint">Complaint</option>
                <option value="Legal">Legal</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div class="form-group">
              <label>Severity Level *</label>
              <select v-model="form.severity_level" class="form-control" required>
                <option value="">Select Severity</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            <div class="form-group">
              <label>Region</label>
              <input v-model="form.region" type="text" class="form-control" />
            </div>
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" class="form-control" rows="4"></textarea>
          </div>

          <div class="form-actions">
            <router-link to="/cases" class="btn btn-outline">Cancel</router-link>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Creating...' : 'Create Case' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

export default {
  name: 'CaseForm',
  setup() {
    const router = useRouter()
    const submitting = ref(false)
    const form = ref({
      case_title: '',
      case_type: '',
      severity_level: '',
      region: '',
      description: '',
      status: 'Open'
    })

    const submitCase = async () => {
      submitting.value = true
      try {
        await api.post('/api/resource/Sigma Case', form.value)
        router.push('/cases')
      } catch (e) {
        console.error('Failed to create case:', e)
        alert('Failed to create case. Please try again.')
      } finally {
        submitting.value = false
      }
    }

    return { form, submitting, submitCase }
  }
}
</script>

<style scoped>
.case-form h1 { font-size: 24px; margin: 8px 0 0 0; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 16px; }
.form-group { display: flex; flex-direction: column; margin-bottom: 16px; }
.form-group label { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 6px; }
.form-control { padding: 10px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
.form-control:focus { outline: none; border-color: #0084ff; box-shadow: 0 0 0 3px rgba(0, 132, 255, 0.1); }
textarea.form-control { resize: vertical; min-height: 100px; }
.form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid #e9ecef; }
</style>

