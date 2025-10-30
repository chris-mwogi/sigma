<template>
  <div class="vehicle-dashboard">
    <div class="page-header">
      <h1>Vehicle Management</h1>
      <p class="subtitle">Fleet management and vehicle tracking</p>
    </div>

    <div class="grid grid-4">
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon">🚗</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.totalVehicles }}</div>
          <div class="kpi-label">Total Vehicles</div>
        </div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon">🔧</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.inMaintenance }}</div>
          <div class="kpi-label">In Maintenance</div>
        </div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon">✅</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.available }}</div>
          <div class="kpi-label">Available</div>
        </div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon">📍</div>
        <div class="kpi-content">
          <div class="kpi-value">{{ stats.onRoad }}</div>
          <div class="kpi-label">On Road</div>
        </div>
      </div>
    </div>

    <div class="grid grid-2 mt-3">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Fleet Status</h2>
          <button class="btn-small">+ Add Vehicle</button>
        </div>
        <div class="card-body">
          <div class="vehicle-list">
            <div v-for="vehicle in vehicles" :key="vehicle.id" class="vehicle-item">
              <div class="vehicle-header">
                <span class="vehicle-plate">{{ vehicle.plate }}</span>
                <span :class="['vehicle-status', `status-${vehicle.status}`]">{{ vehicle.status }}</span>
              </div>
              <div class="vehicle-info">
                <span class="vehicle-model">{{ vehicle.model }}</span>
                <span class="vehicle-driver">👤 {{ vehicle.driver }}</span>
              </div>
              <div class="vehicle-meta">
                <span class="vehicle-mileage">Mileage: {{ vehicle.mileage }}</span>
                <span class="vehicle-fuel">Fuel: {{ vehicle.fuel }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Vehicle Actions</h2>
        </div>
        <div class="card-body">
          <div class="action-list">
            <button class="action-btn">
              <span class="action-icon">➕</span>
              <span>Register Vehicle</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">📍</span>
              <span>Track Location</span>
            </button>
            <button class="action-btn">
              <span class="action-icon">🔧</span>
              <span>Schedule Maintenance</span>
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
  name: 'VehicleManagementDashboard',
  setup() {
    const stats = ref({
      totalVehicles: 45,
      inMaintenance: 3,
      available: 28,
      onRoad: 14
    })

    const vehicles = ref([
      { id: 1, plate: 'KCA 123A', model: 'Toyota Hilux 2020', status: 'Available', driver: 'John Mwangi', mileage: '45,230 km', fuel: '85%' },
      { id: 2, plate: 'KCA 124B', model: 'Ford Transit 2019', status: 'On Road', driver: 'Peter Kipchoge', mileage: '62,150 km', fuel: '60%' },
      { id: 3, plate: 'KCA 125C', model: 'Isuzu NPR 2021', status: 'Maintenance', driver: 'N/A', mileage: '28,900 km', fuel: '40%' }
    ])

    return {
      stats,
      vehicles
    }
  }
}
</script>

<style scoped>
.vehicle-dashboard {
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

.vehicle-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.vehicle-item {
  padding: 16px;
  border: 1px solid var(--kp-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.vehicle-item:hover {
  background-color: var(--kp-hover);
  border-color: var(--kp-primary);
}

.vehicle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.vehicle-plate {
  font-weight: 700;
  color: var(--kp-primary);
  font-size: 14px;
}

.vehicle-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.status-Available { background-color: #DCFCE7; color: #16A34A; }
.status-On\ Road { background-color: #E0E7FF; color: #4F46E5; }
.status-Maintenance { background-color: #FEF3C7; color: #D97706; }

.vehicle-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: var(--kp-text);
  margin-bottom: 8px;
}

.vehicle-model {
  font-weight: 600;
}

.vehicle-driver {
  color: var(--kp-muted);
}

.vehicle-meta {
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

