<template>
  <div class="support-dashboard">
    <div class="page-header">
      <h1>Support</h1>
      <p class="subtitle">Technical support and issue resolution</p>
    </div>

    <div class="grid grid-4">
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon">🆘</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.activeIssues }}</div>
          <div class="kpi-label">Active Issues</div>
        </div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.criticalIssues }}</div>
          <div class="kpi-label">Critical</div>
        </div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon">✅</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.resolvedToday }}</div>
          <div class="kpi-label">Resolved Today</div>
        </div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon">⏱️</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.avgResponseTime }}</div>
          <div class="kpi-label">Avg Response</div>
        </div>
      </div>
    </div>

    <div class="grid grid-2 mt-3">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Active Support Cases</h2>
          <button class="btn-small">+ New Case</button>
        </div>
        <div class="card-body">
          <div class="case-list">
            <div v-for="case_ in activeCases" :key="case_.id" class="case-item">
              <div class="case-header">
                <span class="case-id">{{ case_.id }}</span>
                <span :class="['case-severity', `severity-${case_.severity}`]">{{ case_.severity }}</span>
              </div>
              <div class="case-title">{{ case_.title }}</div>
              <div class="case-meta">
                <span class="case-assignee">👤 {{ case_.assignee }}</span>
                <span class="case-time">{{ case_.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Support Resources</h2>
        </div>
        <div class="card-body">
          <div class="resource-list">
            <button class="resource-btn">
              <span class="resource-icon">📚</span>
              <span>Knowledge Base</span>
            </button>
            <button class="resource-btn">
              <span class="resource-icon">🎓</span>
              <span>Training Materials</span>
            </button>
            <button class="resource-btn">
              <span class="resource-icon">🔧</span>
              <span>Troubleshooting Guide</span>
            </button>
            <button class="resource-btn">
              <span class="resource-icon">📞</span>
              <span>Contact Support</span>
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
  name: 'SupportDashboard',
  setup() {
    const stats = ref({
      activeIssues: 18,
      criticalIssues: 3,
      resolvedToday: 12,
      avgResponseTime: '45m'
    })

    const activeCases = ref([
      { id: 'SUP-001', title: 'Database connection timeout', severity: 'Critical', assignee: 'John Doe', time: '1 hour ago' },
      { id: 'SUP-002', title: 'API rate limiting issue', severity: 'High', assignee: 'Jane Smith', time: '3 hours ago' },
      { id: 'SUP-003', title: 'Report export failing', severity: 'Medium', assignee: 'Mike Johnson', time: '5 hours ago' }
    ])

    return {
      stats,
      activeCases
    }
  }
}
</script>

<style scoped>
.support-dashboard {
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

.case-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.case-item {
  padding: 16px;
  border: 1px solid var(--kp-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.case-item:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.case-id {
  font-weight: 600;
  color: var(--kp-primary);
}

.case-severity {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.severity-Critical { background-color: #FEE2E2; color: #DC2626; }
.severity-High { background-color: #FEF3C7; color: #D97706; }
.severity-Medium { background-color: #E0E7FF; color: #4F46E5; }

.case-title {
  font-weight: 600;
  color: var(--kp-text);
  margin-bottom: 8px;
}

.case-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--kp-muted);
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-btn {
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

.resource-btn:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
  color: var(--kp-primary);
}

.resource-icon {
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

