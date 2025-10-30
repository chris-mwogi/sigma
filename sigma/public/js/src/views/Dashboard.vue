<template>
  <div class="dashboard">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">Sigma Security Management</h1>
        <p class="hero-subtitle">Comprehensive security and asset management platform for Kenya Power</p>
        <div class="hero-cta">
          <router-link to="/cases" class="btn btn-primary btn-lg">
            <span>Get Started</span>
            <span class="btn-arrow">→</span>
          </router-link>
          <button class="btn btn-outline btn-lg" @click="scrollToModules">
            <span>Explore Modules</span>
          </button>
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-icon">🛡️</div>
      </div>
    </section>

    <!-- Key Statistics -->
    <section class="stats-section">
      <h2 class="section-title">System Overview</h2>
      <div class="grid grid-4">
        <div class="stat-card stat-card-primary">
          <div class="stat-icon">📋</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.cases }}</div>
            <div class="stat-label">Active Cases</div>
          </div>
        </div>
        <div class="stat-card stat-card-warning">
          <div class="stat-icon">⚠️</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.incidents }}</div>
            <div class="stat-label">Incidents</div>
          </div>
        </div>
        <div class="stat-card stat-card-accent">
          <div class="stat-icon">🔐</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.accessEvents }}</div>
            <div class="stat-label">Access Events</div>
          </div>
        </div>
        <div class="stat-card stat-card-success">
          <div class="stat-icon">👮</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.guardShifts }}</div>
            <div class="stat-label">Guard Shifts</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Modules Section -->
    <section class="modules-section" ref="modulesSection">
      <h2 class="section-title">All Modules</h2>
      <div class="modules-grid">
        <router-link v-for="module in modules" :key="module.id" :to="module.route" class="module-card">
          <div class="module-icon">{{ module.icon }}</div>
          <h3 class="module-name">{{ module.name }}</h3>
          <p class="module-description">{{ module.description }}</p>
          <div class="module-arrow">→</div>
        </router-link>
      </div>
    </section>

    <!-- Recent Activity -->
    <section class="activity-section">
      <div class="grid grid-2">
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Recent Cases</h2>
            <router-link to="/cases" class="card-link">View All</router-link>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center p-3">Loading...</div>
            <div v-else-if="recentCases.length === 0" class="text-center p-3 text-muted">
              No cases found
            </div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Title</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="case_ in recentCases" :key="case_.name">
                  <td>{{ case_.name }}</td>
                  <td>{{ case_.title }}</td>
                  <td>
                    <span :class="['badge', `badge-${getStatusClass(case_.status)}`]">
                      {{ case_.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Quick Actions</h2>
          </div>
          <div class="card-body p-3">
            <div class="action-list">
              <router-link to="/cases" class="action-item">
                <span class="action-icon">📋</span>
                <span>View Cases</span>
              </router-link>
              <router-link to="/incidents" class="action-item">
                <span class="action-icon">⚠️</span>
                <span>View Incidents</span>
              </router-link>
              <router-link to="/access-control" class="action-item">
                <span class="action-icon">🔐</span>
                <span>Access Control</span>
              </router-link>
              <router-link to="/guard-monitoring" class="action-item">
                <span class="action-icon">👮</span>
                <span>Guard Monitoring</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'Dashboard',
  setup() {
    const loading = ref(false)
    const modulesSection = ref(null)
    const stats = ref({
      cases: 0,
      incidents: 0,
      accessEvents: 0,
      guardShifts: 0
    })
    const recentCases = ref([])

    const modules = [
      { id: 'cases', name: 'Cases', icon: '📋', description: 'Manage security cases and incidents', route: '/cases' },
      { id: 'incidents', name: 'Incidents', icon: '⚠️', description: 'Track and report incidents', route: '/incidents' },
      { id: 'access-control', name: 'Access Control', icon: '🔐', description: 'Manage access permissions', route: '/access-control' },
      { id: 'guard-monitoring', name: 'Guard Monitoring', icon: '👮', description: 'Monitor guard activities', route: '/guard-monitoring' },
      { id: 'assets', name: 'Assets', icon: '🏢', description: 'Track company assets', route: '/assets' },
      { id: 'risk-assessment', name: 'Risk Assessment', icon: '📊', description: 'Assess security risks', route: '/risk-assessment' },
      { id: 'vehicle-management', name: 'Vehicle Management', icon: '🚗', description: 'Manage fleet vehicles', route: '/vehicle-management' },
      { id: 'visitor-management', name: 'Visitor Management', icon: '👥', description: 'Track visitor access', route: '/visitor-management' },
      { id: 'helpdesk', name: 'Helpdesk', icon: '💬', description: 'Support ticket management', route: '/helpdesk' },
      { id: 'support', name: 'Support', icon: '🆘', description: 'Technical support system', route: '/support' },
      { id: 'telephony', name: 'Telephony', icon: '☎️', description: 'Communication management', route: '/telephony' },
      { id: 'projects', name: 'Projects', icon: '📁', description: 'Project management', route: '/projects' },
      { id: 'crm', name: 'CRM', icon: '👔', description: 'Customer relationship management', route: '/crm' }
    ]

    const getStatusClass = (status) => {
      const statusMap = {
        'Open': 'primary',
        'In Progress': 'info',
        'Closed': 'success',
        'On Hold': 'warning'
      }
      return statusMap[status] || 'secondary'
    }

    const scrollToModules = () => {
      if (modulesSection.value) {
        modulesSection.value.scrollIntoView({ behavior: 'smooth' })
      }
    }

    const loadDashboardData = async () => {
      loading.value = true
      try {
        // Load statistics
        const casesResponse = await api.get('/api/resource/Case?fields=["name"]&limit_page_length=1')
        const incidentsResponse = await api.get('/api/resource/Incident Report?fields=["name"]&limit_page_length=1')
        const accessResponse = await api.get('/api/resource/Access Event?fields=["name"]&limit_page_length=1')
        const shiftsResponse = await api.get('/api/resource/Guard Shift?fields=["name"]&limit_page_length=1')

        stats.value.cases = casesResponse.data.data?.length || 0
        stats.value.incidents = incidentsResponse.data.data?.length || 0
        stats.value.accessEvents = accessResponse.data.data?.length || 0
        stats.value.guardShifts = shiftsResponse.data.data?.length || 0

        // Load recent cases
        const recentResponse = await api.get('/api/resource/Case?fields=["name","title","status"]&limit_page_length=5&order_by=`modified` desc')
        recentCases.value = recentResponse.data.data || []
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadDashboardData()
    })

    return {
      loading,
      modulesSection,
      stats,
      recentCases,
      modules,
      getStatusClass,
      scrollToModules
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, var(--kp-primary) 0%, var(--kp-primary-dark) 100%);
  color: white;
  padding: 80px 40px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  margin-bottom: 60px;
  border-radius: 0;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-title {
  font-size: 48px;
  font-weight: 800;
  margin: 0;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 18px;
  opacity: 0.95;
  margin: 0;
  line-height: 1.6;
}

.hero-cta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  white-space: nowrap;
}

.btn-primary {
  background-color: var(--kp-accent);
  color: var(--kp-primary);
}

.btn-primary:hover {
  background-color: #FFE066;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(255, 209, 0, 0.3);
}

.btn-outline {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn-outline:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.btn-lg {
  padding: 14px 32px;
  font-size: 16px;
}

.btn-arrow {
  font-size: 18px;
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-icon {
  font-size: 120px;
  opacity: 0.9;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

/* Stats Section */
.stats-section {
  padding: 60px 40px;
  background-color: var(--kp-bg);
}

.section-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--kp-text);
  margin: 0 0 40px 0;
  text-align: center;
}

.stat-card {
  background-color: var(--kp-surface);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  border-left: 4px solid;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.5) 0%, transparent 70%);
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-card-primary {
  border-left-color: var(--kp-primary);
}

.stat-card-primary .stat-icon {
  background-color: var(--kp-hover);
  color: var(--kp-primary);
}

.stat-card-warning {
  border-left-color: #F39200;
}

.stat-card-warning .stat-icon {
  background-color: #fff8e8;
  color: #F39200;
}

.stat-card-accent {
  border-left-color: #00A651;
}

.stat-card-accent .stat-icon {
  background-color: #e8f8f0;
  color: #00A651;
}

.stat-card-success {
  border-left-color: #28a745;
}

.stat-card-success .stat-icon {
  background-color: #e8f5e9;
  color: #28a745;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--kp-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--kp-muted);
  margin-top: 4px;
  font-weight: 500;
}

/* Modules Section */
.modules-section {
  padding: 60px 40px;
  background-color: var(--kp-surface);
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.module-card {
  background-color: var(--kp-surface);
  border: 2px solid var(--kp-border);
  border-radius: 12px;
  padding: 32px 24px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  overflow: hidden;
}

.module-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--kp-primary), var(--kp-secondary));
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.module-card:hover {
  border-color: var(--kp-primary);
  box-shadow: var(--shadow-lg);
  transform: translateY(-8px);
}

.module-card:hover::before {
  transform: scaleX(1);
}

.module-icon {
  font-size: 48px;
  line-height: 1;
}

.module-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--kp-text);
  margin: 0;
}

.module-description {
  font-size: 14px;
  color: var(--kp-muted);
  margin: 0;
  flex: 1;
}

.module-arrow {
  font-size: 20px;
  color: var(--kp-primary);
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.3s ease;
}

.module-card:hover .module-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* Activity Section */
.activity-section {
  padding: 60px 40px;
  background-color: var(--kp-bg);
}

.card {
  background-color: var(--kp-surface);
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: var(--shadow-lg);
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

.card-link {
  color: var(--kp-primary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.card-link:hover {
  color: var(--kp-primary-dark);
}

.card-body {
  padding: 24px;
}

.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.badge-primary {
  background-color: var(--kp-hover);
  color: var(--kp-primary);
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
  background-color: #fff8e8;
  color: #F39200;
}

.badge-secondary {
  background-color: var(--kp-bg);
  color: var(--kp-muted);
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 8px;
  background-color: var(--kp-bg);
  color: var(--kp-primary);
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  font-weight: 500;
}

.action-item:hover {
  background-color: var(--kp-hover);
  transform: translateX(4px);
  border-left-color: var(--kp-primary);
}

.action-icon {
  font-size: 20px;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table thead {
  background-color: var(--kp-bg);
}

.table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: var(--kp-text);
  border-bottom: 2px solid var(--kp-border);
}

.table td {
  padding: 12px;
  border-bottom: 1px solid var(--kp-border);
}

.table tbody tr:hover {
  background-color: var(--kp-hover);
}

.text-center { text-align: center; }
.p-3 { padding: 24px; }
.text-muted { color: var(--kp-muted); }

/* Responsive */
@media (max-width: 1024px) {
  .hero-section {
    grid-template-columns: 1fr;
    padding: 60px 40px;
  }

  .hero-icon {
    font-size: 80px;
  }

  .modules-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 20px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .hero-cta {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .stats-section,
  .modules-section,
  .activity-section {
    padding: 40px 20px;
  }

  .section-title {
    font-size: 24px;
  }

  .modules-grid {
    grid-template-columns: 1fr;
  }

  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }

  .grid-2 {
    grid-template-columns: 1fr;
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }

  .stat-value {
    font-size: 20px;
  }

  .hero-icon {
    font-size: 60px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 24px;
  }

  .hero-subtitle {
    font-size: 14px;
  }

  .section-title {
    font-size: 20px;
  }

  .module-card {
    padding: 20px 16px;
  }

  .module-icon {
    font-size: 36px;
  }

  .module-name {
    font-size: 16px;
  }

  .module-description {
    font-size: 12px;
  }
}
</style>

