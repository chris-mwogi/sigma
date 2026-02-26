<template>
  <div class="dashboard patrol-dashboard">
    <header class="dashboard__header">
      <div class="dashboard__title-section">
        <h1 class="dashboard__title">🚶 Patrol Monitoring Dashboard</h1>
        <p class="dashboard__subtitle">Visual & data-driven patrol compliance tracking</p>
      </div>
      <div class="dashboard__actions">
        <select v-model="dateRange" class="form-select">
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
        <button class="btn btn--primary" @click="refreshData">🔄 Refresh</button>
      </div>
    </header>

    <!-- Patrol KPIs -->
    <section class="dashboard__section">
      <div class="kpi-grid kpi-grid--6">
        <KPICard icon="📅" :value="data.scheduledPatrols" label="Scheduled Patrols" variant="primary" :loading="loading" />
        <KPICard icon="✅" :value="data.completedPatrols" label="Completed Patrols" variant="success" :loading="loading" />
        <KPICard icon="⏰" :value="data.onTimePatrols" label="On-time Patrols" variant="success" :loading="loading" />
        <KPICard icon="⚠️" :value="data.anomalies" label="Patrol Anomalies" variant="warning" :loading="loading" />
        <KPICard icon="⏭️" :value="data.skippedCheckpoints" label="Skipped Checkpoints" variant="danger" :loading="loading" />
        <KPICard icon="📱" :value="data.deviceTampering" label="Device Tampering" variant="danger" :loading="loading" />
      </div>
    </section>

    <!-- Charts Row 1 -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <ChartCard title="📊 Scheduled vs Completed Patrols" type="bar" :labels="scheduledVsCompleted.labels" :datasets="scheduledVsCompleted.datasets" :loading="loading" />
        <ChartCard title="⏱️ Patrol Timing (On-time vs Late vs Skipped)" type="doughnut" :labels="patrolTiming.labels" :datasets="patrolTiming.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Heatmap & Anomalies -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <div class="heatmap-card">
          <div class="heatmap-card__header">
            <h3>🗓️ Hour-of-Day Patrol Heatmap</h3>
          </div>
          <div class="heatmap-card__body">
            <div class="heatmap-grid">
              <div v-for="hour in 24" :key="hour" class="heatmap-cell" :style="{ backgroundColor: getHeatmapColor(data.heatmapData?.[hour-1] || 0) }" :title="`${hour-1}:00 - ${data.heatmapData?.[hour-1] || 0} patrols`">
                <span class="heatmap-cell__hour">{{ hour - 1 }}</span>
              </div>
            </div>
            <div class="heatmap-legend">
              <span>Low</span>
              <div class="heatmap-legend__gradient"></div>
              <span>High</span>
            </div>
          </div>
        </div>
        <DataTable title="⚠️ Patrol Anomalies" :columns="anomalyColumns" :rows="data.anomalyList" :loading="loading" />
      </div>
    </section>

    <!-- Problem Routes & Early/Late -->
    <section class="dashboard__section">
      <div class="chart-grid chart-grid--2">
        <DataTable title="🔴 Most Problematic Patrol Routes" :columns="routeColumns" :rows="data.problematicRoutes" :loading="loading" />
        <ChartCard title="⏰ Early/Late Scan Analysis" type="bar" :labels="earlyLateChart.labels" :datasets="earlyLateChart.datasets" :loading="loading" />
      </div>
    </section>

    <!-- Checkpoint Performance -->
    <section class="dashboard__section">
      <DataTable title="📍 Checkpoint Performance" :columns="checkpointColumns" :rows="data.checkpointPerformance" :loading="loading" />
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import { KPICard, ChartCard, DataTable } from './components'

export default {
  name: 'PatrolMonitoringDashboard',
  components: { KPICard, ChartCard, DataTable },
  setup() {
    const loading = ref(true)
    const dateRange = ref('today')
    const data = ref({
      scheduledPatrols: 0, completedPatrols: 0, onTimePatrols: 0, anomalies: 0,
      skippedCheckpoints: 0, deviceTampering: 0, heatmapData: [], anomalyList: [],
      problematicRoutes: [], checkpointPerformance: [], scheduledCompletedData: [],
      timingData: [], earlyLateData: []
    })

    const anomalyColumns = [
      { key: 'patrol', label: 'Patrol' }, { key: 'guard', label: 'Guard' },
      { key: 'anomaly', label: 'Anomaly Type', type: 'badge' }, { key: 'time', label: 'Time' }
    ]
    const routeColumns = [
      { key: 'route', label: 'Route' }, { key: 'issues', label: 'Issues', type: 'number' },
      { key: 'completion_rate', label: 'Completion %', type: 'percent' }, { key: 'status', label: 'Status', type: 'badge' }
    ]
    const checkpointColumns = [
      { key: 'checkpoint', label: 'Checkpoint' }, { key: 'scans', label: 'Total Scans', type: 'number' },
      { key: 'on_time', label: 'On-time %', type: 'percent' }, { key: 'skipped', label: 'Skipped', type: 'number' },
      { key: 'avg_time', label: 'Avg Time' }
    ]

    const scheduledVsCompleted = computed(() => ({
      labels: data.value.scheduledCompletedData?.map(d => d.date) || [],
      datasets: [
        { label: 'Scheduled', data: data.value.scheduledCompletedData?.map(d => d.scheduled) || [] },
        { label: 'Completed', data: data.value.scheduledCompletedData?.map(d => d.completed) || [] }
      ]
    }))
    const patrolTiming = computed(() => ({
      labels: data.value.timingData?.map(t => t.category) || [],
      datasets: [{ data: data.value.timingData?.map(t => t.count) || [] }]
    }))
    const earlyLateChart = computed(() => ({
      labels: data.value.earlyLateData?.map(e => e.checkpoint) || [],
      datasets: [
        { label: 'Early', data: data.value.earlyLateData?.map(e => e.early) || [] },
        { label: 'Late', data: data.value.earlyLateData?.map(e => e.late) || [] }
      ]
    }))

    const getHeatmapColor = (val) => {
      const max = Math.max(...(data.value.heatmapData || [1]))
      const intensity = val / (max || 1)
      return `rgba(0, 51, 102, ${0.1 + intensity * 0.8})`
    }

    const fetchData = async () => {
      loading.value = true
      try {
        const res = await api.post('/api/method/sigma.sigma_guard_services.api.guarding_dashboard_api.get_patrol_monitoring_dashboard', { date_range: dateRange.value })
        if (res.data.message) data.value = res.data.message
      } catch (e) { console.error('Failed to load patrol dashboard:', e) }
      finally { loading.value = false }
    }

    const refreshData = () => fetchData()
    onMounted(fetchData)

    return { loading, dateRange, data, anomalyColumns, routeColumns, checkpointColumns, scheduledVsCompleted, patrolTiming, earlyLateChart, getHeatmapColor, refreshData }
  }
}
</script>

<style src="./dashboard-common.css"></style>
<style scoped>
.heatmap-card { background: var(--kp-surface, #fff); border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.heatmap-card__header { padding: 16px 20px; border-bottom: 1px solid var(--kp-border); }
.heatmap-card__header h3 { margin: 0; font-size: 16px; }
.heatmap-card__body { padding: 20px; }
.heatmap-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 4px; }
.heatmap-cell { aspect-ratio: 1; border-radius: 4px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: transform 0.2s; }
.heatmap-cell:hover { transform: scale(1.1); }
.heatmap-cell__hour { font-size: 10px; color: #fff; font-weight: 600; }
.heatmap-legend { display: flex; align-items: center; gap: 8px; margin-top: 16px; justify-content: center; font-size: 12px; color: var(--kp-muted); }
.heatmap-legend__gradient { width: 100px; height: 8px; background: linear-gradient(to right, rgba(0,51,102,0.1), rgba(0,51,102,0.9)); border-radius: 4px; }
</style>

