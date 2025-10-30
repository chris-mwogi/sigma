<template>
  <div class="telephony-dashboard">
    <div class="page-header">
      <h1>Telephony</h1>
      <p class="subtitle">Communication and call management system</p>
    </div>

    <div class="grid grid-4">
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon">☎️</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.activeCalls }}</div>
          <div class="kpi-label">Active Calls</div>
        </div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon">📞</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.totalCalls }}</div>
          <div class="kpi-label">Total Today</div>
        </div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon">⏱️</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.avgCallDuration }}</div>
          <div class="kpi-label">Avg Duration</div>
        </div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon">📊</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.callQuality }}</div>
          <div class="kpi-label">Quality Score</div>
        </div>
      </div>
    </div>

    <div class="grid grid-2 mt-3">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Call Log</h2>
          <button class="btn-small">+ New Call</button>
        </div>
        <div class="card-body">
          <div class="call-list">
            <div v-for="call in callLog" :key="call.id" class="call-item">
              <div class="call-header">
                <span class="call-number">{{ call.number }}</span>
                <span :class="['call-type', `type-${call.type}`]">{{ call.type }}</span>
              </div>
              <div class="call-duration">Duration: {{ call.duration }}</div>
              <div class="call-meta">
                <span class="call-date">{{ call.date }}</span>
                <span class="call-status">{{ call.status }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Communication Tools</h2>
        </div>
        <div class="card-body">
          <div class="tool-list">
            <button class="tool-btn">
              <span class="tool-icon">📱</span>
              <span>Make Call</span>
            </button>
            <button class="tool-btn">
              <span class="tool-icon">💬</span>
              <span>Send SMS</span>
            </button>
            <button class="tool-btn">
              <span class="tool-icon">📧</span>
              <span>Send Email</span>
            </button>
            <button class="tool-btn">
              <span class="tool-icon">📋</span>
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
  name: 'TelephonyDashboard',
  setup() {
    const stats = ref({
      activeCalls: 5,
      totalCalls: 142,
      avgCallDuration: '4m 32s',
      callQuality: '98%'
    })

    const callLog = ref([
      { id: 1, number: '+254 712 345 678', type: 'Incoming', duration: '5m 23s', date: '10:30 AM', status: 'Completed' },
      { id: 2, number: '+254 723 456 789', type: 'Outgoing', duration: '3m 15s', date: '10:15 AM', status: 'Completed' },
      { id: 3, number: '+254 734 567 890', type: 'Incoming', duration: '2m 45s', date: '09:45 AM', status: 'Completed' }
    ])

    return {
      stats,
      callLog
    }
  }
}
</script>

<style scoped>
.telephony-dashboard {
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

.call-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.call-item {
  padding: 16px;
  border: 1px solid var(--kp-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.call-item:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
}

.call-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.call-number {
  font-weight: 600;
  color: var(--kp-primary);
}

.call-type {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.type-Incoming { background-color: #DCFCE7; color: #16A34A; }
.type-Outgoing { background-color: #E0E7FF; color: #4F46E5; }

.call-duration {
  font-size: 13px;
  color: var(--kp-text);
  margin-bottom: 8px;
}

.call-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--kp-muted);
}

.tool-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tool-btn {
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

.tool-btn:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
  color: var(--kp-primary);
}

.tool-icon {
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

