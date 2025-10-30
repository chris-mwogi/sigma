<template>
  <div class="case-form">
    <div class="flex-between mb-3">
      <h1>Create New Case</h1>
      <router-link to="/cases" class="btn btn-outline">
        ← Back to Cases
      </router-link>
    </div>

    <div class="card">
      <div class="card-body p-3">
        <form @submit.prevent="submitForm">
          <div class="grid grid-2">
            <div class="form-group">
              <label for="title">Title *</label>
              <input
                id="title"
                v-model="form.title"
                type="text"
                placeholder="Enter case title"
                required
              />
            </div>

            <div class="form-group">
              <label for="priority">Priority</label>
              <select id="priority" v-model="form.priority">
                <option value="">Select Priority</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="description">Description</label>
            <textarea
              id="description"
              v-model="form.description"
              placeholder="Enter case description"
            ></textarea>
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label for="status">Status</label>
              <select id="status" v-model="form.status">
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="On Hold">On Hold</option>
                <option value="Closed">Closed</option>
              </select>
            </div>

            <div class="form-group">
              <label for="assigned_to">Assigned To</label>
              <input
                id="assigned_to"
                v-model="form.assigned_to"
                type="text"
                placeholder="User email"
              />
            </div>
          </div>

          <div v-if="error" class="alert alert-danger mb-3">
            {{ error }}
          </div>

          <div v-if="success" class="alert alert-success mb-3">
            {{ success }}
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Creating...' : 'Create Case' }}
            </button>
            <router-link to="/cases" class="btn btn-outline">
              Cancel
            </router-link>
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
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    const form = ref({
      title: '',
      description: '',
      priority: '',
      status: 'Open',
      assigned_to: ''
    })

    const submitForm = async () => {
      error.value = ''
      success.value = ''

      if (!form.value.title.trim()) {
        error.value = 'Title is required'
        return
      }

      loading.value = true
      try {
        const response = await api.post('/api/resource/Case', {
          title: form.value.title,
          description: form.value.description,
          priority: form.value.priority,
          status: form.value.status,
          assigned_to: form.value.assigned_to
        })

        success.value = 'Case created successfully!'
        setTimeout(() => {
          router.push(`/cases/${response.data.data.name}`)
        }, 1000)
      } catch (err) {
        error.value = err.response?.data?.message || 'Failed to create case'
      } finally {
        loading.value = false
      }
    }

    return {
      loading,
      error,
      success,
      form,
      submitForm
    }
  }
}
</script>

<style scoped>
.case-form h1 {
  font-size: 24px;
  margin: 0;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #333;
}

input,
select,
textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #0084ff;
  box-shadow: 0 0 0 3px rgba(0, 132, 255, 0.1);
}

textarea {
  resize: vertical;
  min-height: 120px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #0084ff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0066cc;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid #0084ff;
  color: #0084ff;
}

.btn-outline:hover {
  background-color: #0084ff;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>

