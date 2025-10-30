<template>
  <div class="projects-dashboard">
    <div class="page-header">
      <h1>Projects</h1>
      <p class="subtitle">Project management and tracking</p>
    </div>

    <div class="grid grid-4">
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon">📁</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.activeProjects }}</div>
          <div class="kpi-label">Active Projects</div>
        </div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon">⏳</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.inProgress }}</div>
          <div class="kpi-label">In Progress</div>
        </div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon">✅</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.completed }}</div>
          <div class="kpi-label">Completed</div>
        </div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon">📊</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.avgCompletion }}</div>
          <div class="kpi-label">Avg Completion</div>
        </div>
      </div>
    </div>

    <div class="grid grid-2 mt-3">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Current Projects</h2>
          <button class="btn-small">+ New Project</button>
        </div>
        <div class="card-body">
          <div class="project-list">
            <div v-for="project in projects" :key="project.id" class="project-item">
              <div class="project-header">
                <span class="project-name">{{ project.name }}</span>
                <span :class="['project-status', `status-${project.status}`]">{{ project.status }}</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: project.progress + '%' }"></div>
              </div>
              <div class="project-meta">
                <span class="project-progress">{{ project.progress }}% Complete</span>
                <span class="project-deadline">Due: {{ project.deadline }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Project Actions</h2>
        </div>
        <div class="card-body">
          <div class="action-list">
            <button class="action-btn">
              <span class="action-icon">➕</span>
              <span>Create Project</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">👥</span>
              <span>Manage Team</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">📅</span>
              <span>View Timeline</span>
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
import { ref } from 'vue'

export default {
  name: 'ProjectsDashboard',
  setup() {
    const stats = ref({
      activeProjects: 8,
      inProgress: 5,
      completed: 23,
      avgCompletion: '65%'
    })

    const projects = ref([
      { id: 1, name: 'Security System Upgrade', status: 'In Progress', progress: 75, deadline: '2024-12-15' },
      { id: 2, name: 'Access Control Implementation', status: 'In Progress', progress: 60, deadline: '2024-11-30' },
      { id: 3, name: 'CCTV Network Expansion', status: 'Planning', progress: 30, deadline: '2024-12-31' },
      { id: 4, name: 'Guard Training Program', status: 'In Progress', progress: 85, deadline: '2024-11-20' }
    ])

    return {
      stats,
      projects
    }
  }
}
</script>

<style scoped>
.projects-dashboard {
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

.project-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.project-item {
  padding: 16px;
  border: 1px solid var(--kp-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.project-item:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.project-name {
  font-weight: 600;
  color: var(--kp-text);
}

.project-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.status-In\ Progress { background-color: #FEF3C7; color: #D97706; }
.status-Planning { background-color: #E0E7FF; color: #4F46E5; }
.status-Completed { background-color: #DCFCE7; color: #16A34A; }

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: var(--kp-bg);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--kp-primary), var(--kp-secondary));
  transition: width 0.3s ease;
}

.project-meta {
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

