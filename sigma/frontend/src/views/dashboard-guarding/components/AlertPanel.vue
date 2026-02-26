<template>
  <div class="alert-panel">
    <div class="alert-panel__header">
      <h3 class="alert-panel__title">
        <span class="alert-panel__icon">{{ icon }}</span>
        {{ title }}
      </h3>
      <span v-if="alerts.length > 0" class="alert-panel__count">{{ alerts.length }}</span>
    </div>
    <div class="alert-panel__body">
      <div v-if="loading" class="alert-panel__loading">
        <div class="spinner"></div>
      </div>
      <div v-else-if="alerts.length === 0" class="alert-panel__empty">
        No alerts
      </div>
      <div v-else class="alert-panel__list">
        <div 
          v-for="(alert, idx) in alerts" 
          :key="idx" 
          :class="['alert-item', `alert-item--${alert.severity || 'info'}`]"
          @click="$emit('alert-click', alert)"
        >
          <div class="alert-item__indicator"></div>
          <div class="alert-item__content">
            <div class="alert-item__title">{{ alert.title }}</div>
            <div v-if="alert.description" class="alert-item__desc">{{ alert.description }}</div>
            <div class="alert-item__meta">
              <span v-if="alert.location">📍 {{ alert.location }}</span>
              <span v-if="alert.time">🕐 {{ formatTime(alert.time) }}</span>
            </div>
          </div>
          <div v-if="alert.action" class="alert-item__action">
            <button class="btn-action" @click.stop="$emit('action', alert)">{{ alert.action }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlertPanel',
  props: {
    title: { type: String, default: 'Alerts' },
    icon: { type: String, default: '🔔' },
    alerts: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  emits: ['alert-click', 'action'],
  setup() {
    const formatTime = (time) => {
      if (!time) return ''
      const date = new Date(time)
      const now = new Date()
      const diff = (now - date) / 1000 / 60
      if (diff < 60) return `${Math.floor(diff)}m ago`
      if (diff < 1440) return `${Math.floor(diff / 60)}h ago`
      return date.toLocaleDateString()
    }
    return { formatTime }
  }
}
</script>

<style scoped>
.alert-panel { background: var(--kp-surface, #fff); border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.alert-panel__header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--kp-border, #e0e0e0); }
.alert-panel__title { margin: 0; font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.alert-panel__icon { font-size: 20px; }
.alert-panel__count { background: #dc3545; color: #fff; font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.alert-panel__body { max-height: 400px; overflow-y: auto; }
.alert-panel__loading, .alert-panel__empty { padding: 40px; text-align: center; color: var(--kp-muted, #666); }
.alert-panel__list { padding: 8px; }
.alert-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px; border-radius: 8px; margin-bottom: 8px; background: var(--kp-bg, #f8f9fa); cursor: pointer; transition: all 0.2s; }
.alert-item:hover { transform: translateX(4px); }
.alert-item__indicator { width: 4px; height: 100%; min-height: 40px; border-radius: 2px; }
.alert-item--critical .alert-item__indicator { background: #dc3545; }
.alert-item--high .alert-item__indicator { background: #fd7e14; }
.alert-item--medium .alert-item__indicator { background: #ffc107; }
.alert-item--low .alert-item__indicator { background: #28a745; }
.alert-item--info .alert-item__indicator { background: #17a2b8; }
.alert-item__content { flex: 1; }
.alert-item__title { font-weight: 600; font-size: 14px; color: var(--kp-text, #1a1a1a); }
.alert-item__desc { font-size: 12px; color: var(--kp-muted, #666); margin-top: 4px; }
.alert-item__meta { font-size: 11px; color: var(--kp-muted, #999); margin-top: 6px; display: flex; gap: 12px; }
.btn-action { background: var(--kp-primary, #003366); color: #fff; border: none; padding: 6px 12px; border-radius: 4px; font-size: 11px; cursor: pointer; }
.spinner { width: 24px; height: 24px; border: 3px solid var(--kp-border); border-top-color: var(--kp-primary); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>

