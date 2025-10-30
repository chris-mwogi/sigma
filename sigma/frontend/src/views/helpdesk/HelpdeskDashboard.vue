<template>
  <div class="helpdesk-dashboard">
    <div class="page-header">
      <h1>Helpdesk</h1>
      <p class="subtitle">Support ticket management and resolution</p>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-4">
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon">🎫</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.openTickets }}</div>
          <div class="kpi-label">Open Tickets</div>
        </div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon">⏱️</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.pendingTickets }}</div>
          <div class="kpi-label">Pending</div>
        </div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon">✅</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.resolvedTickets }}</div>
          <div class="kpi-label">Resolved</div>
        </div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon">⏰</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.avgResolutionTime }}</div>
          <div class="kpi-label">Avg Resolution</div>
        </div>
      </div>
    </div>

    <!-- Content Grid -->
    <div class="grid grid-2 mt-3">
      <!-- Recent Tickets -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Recent Tickets</h2>
          <button class="btn-small">+ New Ticket</button>
        </div>
        <div class="card-body">
          <div class="ticket-list">
            <div v-for="ticket in recentTickets" :key="ticket.id" class="ticket-item">
              <div class="ticket-header">
                <span class="ticket-id">{{ ticket.id }}</span>
                <span :class="['ticket-status', `status-${ticket.status}`]">{{ ticket.status }}</span>
              </div>
              <div class="ticket-title">{{ ticket.title }}</div>
              <div class="ticket-meta">
                <span class="ticket-priority" :class="`priority-${ticket.priority}`">{{ ticket.priority }}</span>
                <span class="ticket-date">{{ ticket.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Quick Actions</h2>
        </div>
        <div class="card-body">
          <div class="action-list">
            <button class="action-btn">
              <span class="action-icon">➕</span>
              <span>Create New Ticket</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">📋</span>
              <span>View All Tickets</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">👥</span>
              <span>Manage Agents</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">📊</span>
              <span>View Reports</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'HelpdeskDashboard',
  setup() {
    const stats = ref({
      openTickets: 24,
      pendingTickets: 8,
      resolvedTickets: 156,
      avgResolutionTime: '2.5h'
    })

    const recentTickets = ref([
      { id: 'TKT-001', title: 'System access issue', status: 'Open', priority: 'High', date: '2 hours ago' },
      { id: 'TKT-002', title: 'Password reset request', status: 'In Progress', priority: 'Medium', date: '4 hours ago' },
      { id: 'TKT-003', title: 'Report generation error', status: 'Pending', priority: 'High', date: '6 hours ago' },
      { id: 'TKT-004', title: 'Email configuration', status: 'Resolved', priority: 'Low', date: '1 day ago' }
    ])

    onMounted(() => {
      // Load data from API
    })

    return {
      stats,
      recentTickets
    }
  }
}
</script>

<style scoped>
.helpdesk-dashboard {
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

.ticket-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ticket-item {
  padding: 16px;
  border: 1px solid var(--kp-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.ticket-item:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.ticket-id {
  font-weight: 600;
  color: var(--kp-primary);
}

.ticket-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.status-Open { background-color: #FEE2E2; color: #DC2626; }
.status-In\ Progress { background-color: #FEF3C7; color: #D97706; }
.status-Resolved { background-color: #DCFCE7; color: #16A34A; }
.status-Pending { background-color: #E0E7FF; color: #4F46E5; }

.ticket-title {
  font-weight: 600;
  color: var(--kp-text);
  margin-bottom: 8px;
}

.ticket-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--kp-muted);
}

.ticket-priority {
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.priority-High { background-color: #FEE2E2; color: #DC2626; }
.priority-Medium { background-color: #FEF3C7; color: #D97706; }
.priority-Low { background-color: #DCFCE7; color: #16A34A; }

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

