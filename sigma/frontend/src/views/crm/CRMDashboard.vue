<template>
  <div class="crm-dashboard">
    <div class="page-header">
      <h1>CRM</h1>
      <p class="subtitle">Customer relationship management</p>
    </div>

    <div class="grid grid-4">
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon">👥</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.totalCustomers }}</div>
          <div class="kpi-label">Total Customers</div>
        </div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.activeLead }}</div>
          <div class="kpi-label">Active Leads</div>
        </div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon">💰</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.totalRevenue }}</div>
          <div class="kpi-label">Total Revenue</div>
        </div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon">📈</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.conversionRate }}</div>
          <div class="kpi-label">Conversion Rate</div>
        </div>
      </div>
    </div>

    <div class="grid grid-2 mt-3">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Recent Customers</h2>
          <button class="btn-small">+ Add Customer</button>
        </div>
        <div class="card-body">
          <div class="customer-list">
            <div v-for="customer in customers" :key="customer.id" class="customer-item">
              <div class="customer-header">
                <span class="customer-name">{{ customer.name }}</span>
                <span :class="['customer-status', `status-${customer.status}`]">{{ customer.status }}</span>
              </div>
              <div class="customer-info">
                <span class="customer-email">📧 {{ customer.email }}</span>
                <span class="customer-phone">📱 {{ customer.phone }}</span>
              </div>
              <div class="customer-meta">
                <span class="customer-value">Value: {{ customer.value }}</span>
                <span class="customer-date">Added: {{ customer.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">CRM Tools</h2>
        </div>
        <div class="card-body">
          <div class="tool-list">
            <button class="tool-btn">
              <span class="tool-icon">➕</span>
              <span>New Customer</span>
            </button>
            <button class="tool-btn">
              <span class="tool-icon">🎯</span>
              <span>Manage Leads</span>
            </button>
            <button class="tool-btn">
              <span class="tool-icon">📞</span>
              <span>Contact History</span>
            </button>
            <button class="tool-btn">
              <span class="tool-icon">📊</span>
              <span>Sales Reports</span>
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
  name: 'CRMDashboard',
  setup() {
    const stats = ref({
      totalCustomers: 342,
      activeLead: 28,
      totalRevenue: 'KES 2.5M',
      conversionRate: '18%'
    })

    const customers = ref([
      { id: 1, name: 'Kenya Power Ltd', email: 'contact@kp.co.ke', phone: '+254 712 345 678', status: 'Active', value: 'KES 500K', date: '2024-10-15' },
      { id: 2, name: 'Safaricom PLC', email: 'business@safaricom.co.ke', phone: '+254 723 456 789', status: 'Active', value: 'KES 750K', date: '2024-10-10' },
      { id: 3, name: 'Equity Bank', email: 'corporate@equitybank.co.ke', phone: '+254 734 567 890', status: 'Prospect', value: 'KES 300K', date: '2024-10-05' }
    ])

    return {
      stats,
      customers
    }
  }
}
</script>

<style scoped>
.crm-dashboard {
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

.customer-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.customer-item {
  padding: 16px;
  border: 1px solid var(--kp-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.customer-item:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
}

.customer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.customer-name {
  font-weight: 600;
  color: var(--kp-text);
}

.customer-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.status-Active { background-color: #DCFCE7; color: #16A34A; }
.status-Prospect { background-color: #E0E7FF; color: #4F46E5; }
.status-Inactive { background-color: #F3F4F6; color: #6B7280; }

.customer-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: var(--kp-muted);
  margin-bottom: 8px;
}

.customer-meta {
  display: flex;
  justify-content: space-between;
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

