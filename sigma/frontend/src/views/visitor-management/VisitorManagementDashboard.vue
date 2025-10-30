<template>
  <div class="visitor-dashboard">
    <div class="page-header">
      <h1>Visitor Management</h1>
      <p class="subtitle">Track and manage visitor access</p>
    </div>

    <div class="grid grid-4">
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon">👥</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.todayVisitors }}</div>
          <div class="kpi-label">Today's Visitors</div>
        </div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon">⏳</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.checkedIn }}</div>
          <div class="kpi-label">Checked In</div>
        </div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon">✅</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.checkedOut }}</div>
          <div class="kpi-label">Checked Out</div>
        </div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon">📋</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.preRegistered }}</div>
          <div class="kpi-label">Pre-Registered</div>
        </div>
      </div>
    </div>

    <div class="grid grid-2 mt-3">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Active Visitors</h2>
          <button class="btn-small">+ Register Visitor</button>
        </div>
        <div class="card-body">
          <div class="visitor-list">
            <div v-for="visitor in activeVisitors" :key="visitor.id" class="visitor-item">
              <div class="visitor-header">
                <span class="visitor-name">{{ visitor.name }}</span>
                <span :class="['visitor-status', `status-${visitor.status}`]">{{ visitor.status }}</span>
              </div>
              <div class="visitor-info">
                <span class="visitor-company">🏢 {{ visitor.company }}</span>
                <span class="visitor-purpose">📌 {{ visitor.purpose }}</span>
              </div>
              <div class="visitor-meta">
                <span class="visitor-time">{{ visitor.checkInTime }}</span>
                <span class="visitor-host">Host: {{ visitor.host }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Visitor Actions</h2>
        </div>
        <div class="card-body">
          <div class="action-list">
            <button class="action-btn">
              <span class="action-icon">➕</span>
              <span>Register New Visitor</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">📋</span>
              <span>Pre-Register Visitors</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">📊</span>
              <span>View History</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">🔐</span>
              <span>Access Logs</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'VisitorManagementDashboard',
  setup() {
    const stats = ref({
      todayVisitors: 12,
      checkedIn: 8,
      checkedOut: 4,
      preRegistered: 3
    })

    const activeVisitors = ref([
      { id: 1, name: 'Sarah Johnson', company: 'Acme Corp', purpose: 'Meeting', status: 'Checked In', checkInTime: '09:30 AM', host: 'John Doe' },
      { id: 2, name: 'Michael Chen', company: 'Tech Solutions', purpose: 'Presentation', status: 'Checked In', checkInTime: '10:15 AM', host: 'Jane Smith' },
      { id: 3, name: 'Emma Wilson', company: 'Consulting Ltd', purpose: 'Audit', status: 'Checked In', checkInTime: '08:45 AM', host: 'Mike Johnson' }
    ])

    return {
      stats,
      activeVisitors
    }
  }
}
</script>

<style scoped>
.visitor-dashboard {
  padding: 20px 0;
}

.page-header {
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: var(--kp-text);
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: var(--kp-muted);
  margin: 0;
}

.kpi-card {
  background-color: var(--kp-surface);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  border-left: 4px solid;
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.kpi-primary { border-left-color: var(--kp-primary); }
.kpi-warning { border-left-color: #F39200; }
.kpi-success { border-left-color: #16A34A; }
.kpi-info { border-left-color: var(--kp-secondary); }

.kpi-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background-color: var(--kp-hover);
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--kp-text);
}

.kpi-label {
  font-size: 13px;
  color: var(--kp-muted);
  margin-top: 4px;
}

.card {
  background-color: var(--kp-surface);
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--kp-border);
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--kp-text);
  margin: 0;
}

.btn-small {
  background-color: var(--kp-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-small:hover {
  background-color: var(--kp-primary-dark);
}

.card-body {
  padding: 24px;
}

.visitor-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.visitor-item {
  padding: 16px;
  border: 1px solid var(--kp-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.visitor-item:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
}

.visitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.visitor-name {
  font-weight: 600;
  color: var(--kp-text);
}

.visitor-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.status-Checked\ In { background-color: #DCFCE7; color: #16A34A; }
.status-Checked\ Out { background-color: #F3F4F6; color: #6B7280; }
.status-Pre-Registered { background-color: #E0E7FF; color: #4F46E5; }

.visitor-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: var(--kp-muted);
  margin-bottom: 8px;
}

.visitor-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--kp-muted);
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 8px;
  background-color: var(--kp-bg);
  border: 1px solid var(--kp-border);
  color: var(--kp-text);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.action-btn:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
  color: var(--kp-primary);
}

.action-icon {
  font-size: 18px;
}

.grid {
  display: grid;
  gap: 24px;
}

.grid-4 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
.grid-2 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }

.mt-3 { margin-top: 40px; }

@media (max-width: 768px) {
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
  .grid-2 { grid-template-columns: 1fr; }
}
</style>

