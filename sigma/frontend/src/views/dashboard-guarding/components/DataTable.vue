<template>
  <div class="data-table-container">
    <div v-if="title" class="data-table__header">
      <h3 class="data-table__title">{{ title }}</h3>
      <slot name="actions"></slot>
    </div>
    <div class="data-table__wrapper">
      <div v-if="loading" class="data-table__loading">
        <div class="spinner"></div>
        <span>Loading data...</span>
      </div>
      <table v-else-if="rows.length > 0" class="data-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key" :class="col.class" :style="{ width: col.width }">
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in rows" :key="idx" @click="$emit('row-click', row)">
            <td v-for="col in columns" :key="col.key" :class="col.class">
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                <span v-if="col.type === 'badge'" :class="['badge', `badge--${getBadgeVariant(row[col.key])}`]">
                  {{ row[col.key] }}
                </span>
                <span v-else-if="col.type === 'number'">{{ formatNumber(row[col.key]) }}</span>
                <span v-else-if="col.type === 'percent'">{{ formatPercent(row[col.key]) }}</span>
                <span v-else-if="col.type === 'date'">{{ formatDate(row[col.key]) }}</span>
                <span v-else>{{ row[col.key] }}</span>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="data-table__empty">
        <span class="data-table__empty-icon">📭</span>
        <span>{{ emptyMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  props: {
    title: { type: String, default: '' },
    columns: { type: Array, required: true },
    rows: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    emptyMessage: { type: String, default: 'No data available' }
  },
  emits: ['row-click'],
  setup() {
    const formatNumber = (val) => (Number(val) || 0).toLocaleString()
    const formatPercent = (val) => `${(Number(val) || 0).toFixed(1)}%`
    const formatDate = (val) => val ? new Date(val).toLocaleDateString() : '-'
    const getBadgeVariant = (status) => {
      const map = {
        'Active': 'success', 'Completed': 'success', 'Compliant': 'success', 'Low': 'success',
        'Open': 'primary', 'In Progress': 'info', 'Partial': 'warning', 'Medium': 'warning',
        'Closed': 'secondary', 'Resolved': 'secondary',
        'High': 'danger', 'Critical': 'danger', 'Non-Compliant': 'danger', 'Failed': 'danger'
      }
      return map[status] || 'default'
    }
    return { formatNumber, formatPercent, formatDate, getBadgeVariant }
  }
}
</script>

<style scoped>
.data-table-container { background: var(--kp-surface, #fff); border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.data-table__header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--kp-border, #e0e0e0); }
.data-table__title { margin: 0; font-size: 16px; font-weight: 600; color: var(--kp-text, #1a1a1a); }
.data-table__wrapper { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--kp-border, #e0e0e0); }
.data-table th { background: var(--kp-bg, #f8f9fa); font-weight: 600; font-size: 12px; text-transform: uppercase; color: var(--kp-muted, #666); }
.data-table tbody tr:hover { background: var(--kp-hover, #f0f4f8); cursor: pointer; }
.data-table__loading, .data-table__empty { padding: 40px; text-align: center; color: var(--kp-muted, #666); display: flex; flex-direction: column; align-items: center; gap: 12px; }
.data-table__empty-icon { font-size: 32px; }
.badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.badge--default { background: #e0e0e0; color: #666; }
.badge--primary { background: #e3f2fd; color: #1976d2; }
.badge--success { background: #e8f5e9; color: #388e3c; }
.badge--warning { background: #fff8e1; color: #f57c00; }
.badge--danger { background: #ffebee; color: #d32f2f; }
.badge--info { background: #e0f7fa; color: #0097a7; }
.badge--secondary { background: #eceff1; color: #546e7a; }
.spinner { width: 24px; height: 24px; border: 3px solid var(--kp-border); border-top-color: var(--kp-primary, #003366); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>

