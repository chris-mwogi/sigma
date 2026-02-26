<template>
  <div class="dashboard performance-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">🏆 Guard Force Performance Dashboard</h1>
        <p class="dashboard__subtitle">Efficiency evaluation and performance tracking</p>
      </div>
      <div class="dashboard__actions">
        <select v-model="dateRange" class="form-select">
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="quarter">This Quarter</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Performance KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--5">
        <KPICard icon="✅" :value="data.patrolCompletion" label="Patrol Completion %" format="percent" :variant="data.patrolCompletion >= 90 ? 'success' : 'warning'" :loading="loading" />
        <KPICard icon="⏱️" :value="data.avgResponseTime" label="Avg Response Time (min)" variant="info" :loading="loading" />
        <KPICard icon="📅" :value="data.attendanceScore" label="Attendance Score %" format="percent" :variant="data.attendanceScore >= 95 ? 'success' : 'warning'" :loading="loading" />
        <KPICard icon="🎓" :value="data.trainingCompliance" label="Training Compliance %" format="percent" :variant="data.trainingCompliance >= 80 ? 'success' : 'danger'" :loading="loading" />
        <KPICard icon="⭐" :value="data.overallScore" label="Overall Performance" variant="primary" :loading="loading" />
      </div>
    </section>

    <!-- Charts -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📈 Performance Trend" type="line" :labels="performanceTrend.labels" :datasets="performanceTrend.datasets" :loading="loading" />
        <ChartCard title="🎯 Performance by Category" type="radar" :labels="categoryPerformance.labels" :datasets="categoryPerformance.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Leaderboard & Training -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <div class="leaderboard-card">
          <div class="leaderboard-card__header">
            <h3>🏅 Top Performers</h3>
          </div>
          <div class="leaderboard-card__body">
            <div v-for="(guard, idx) in data.topPerformers" :key="idx" class="leaderboard-item">
              <span class="leaderboard-item__rank">{{ idx + 1 }}</span>
              <span class="leaderboard-item__medal">{{ idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : '👮' }}</span>
              <span class="leaderboard-item__name">{{ guard.name }}</span>
              <span class="leaderboard-item__score">{{ guard.score }}%</span>
            </div>
          </div>
        </div>
        <DataTable title="🎓 Training Status" :columns="trainingColumns" :rows="data.trainingStatus" :loading="loading" />
      </div>
    </section>

    <!-- Detailed Performance -->
    <section class="dashboard__section">
      <DataTable title="📊 Guard Performance Scorecard" :columns="scorecardColumns" :rows="data.scorecard" :loading="loading" />
    </section>

    <!-- Attendance Chart -->
    <section class="dashboard__section">
      <ChartCard title="📅 Attendance Scorecard" type="bar" :labels="attendanceChart.labels" :datasets="attendanceChart.datasets" height="300px" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'GuardPerformanceDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const dateRange = ref('month')
    const data = ref({
      patrolCompletion: 0, avgResponseTime: 0, attendanceScore: 0, trainingCompliance: 0,
      overallScore: 0, topPerformers: [], trainingStatus: [], scorecard: [],
      performanceData: [], categoryData: [], attendanceData: []
    })

    const trainingColumns = [
      { key: 'guard', label: 'Guard' }, { key: 'course', label: 'Course' },
      { key: 'due_date', label: 'Due Date', type: 'date' }, { key: 'status', label: 'Status', type: 'badge' }
    ]
    const scorecardColumns = [
      { key: 'guard', label: 'Guard' }, { key: 'patrol_score', label: 'Patrol %', type: 'percent' },
      { key: 'attendance', label: 'Attendance %', type: 'percent' }, { key: 'response_time', label: 'Resp. Time' },
      { key: 'training', label: 'Training %', type: 'percent' }, { key: 'overall', label: 'Overall', type: 'badge' }
    ]

    const performanceTrend = computed(() => ({
      labels: data.value.performanceData?.map(p => p.period) || [],
      datasets: [{ label: 'Performance Score', data: data.value.performanceData?.map(p => p.score) || [] }]
    }))
    const categoryPerformance = computed(() => ({
      labels: data.value.categoryData?.map(c => c.category) || [],
      datasets: [{ label: 'Score', data: data.value.categoryData?.map(c => c.score) || [] }]
    }))
    const attendanceChart = computed(() => ({
      labels: data.value.attendanceData?.map(a => a.guard) || [],
      datasets: [{ label: 'Attendance %', data: data.value.attendanceData?.map(a => a.percentage) || [] }]
    }))

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_guard_performance_dashboard', { date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load performance dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, dateRange, data, trainingColumns, scorecardColumns, performanceTrend, categoryPerformance, attendanceChart, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>
<style scoped>
.leaderboard-card { background: var(--kp-surface, #fff); border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.leaderboard-card__header { padding: 16px 20px; border-bottom: 1px solid var(--kp-border); }
.leaderboard-card__header h3 { margin: 0; font-size: 16px; }
.leaderboard-card__body { padding: 16px; }
.leaderboard-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 8px; margin-bottom: 8px; background: var(--kp-bg); }
.leaderboard-item__rank { font-weight: 700; color: var(--kp-muted); width: 24px; }
.leaderboard-item__medal { font-size: 24px; }
.leaderboard-item__name { flex: 1; font-weight: 500; }
.leaderboard-item__score { font-weight: 700; color: var(--kp-primary); }
</style>

