frappe.pages['access-command-center'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Access Control Command Center',
		single_column: true
	});

	// Add refresh button
	page.set_primary_action(__('Refresh'), () => refreshDashboard(), 'refresh');
	
	// Add date filter
	page.add_field({
		fieldname: 'date_filter',
		label: __('Date Range'),
		fieldtype: 'Select',
		options: 'Today\nLast 7 Days\nThis Month',
		default: 'Today',
		change: () => refreshDashboard()
	});

	// Auto-refresh interval selector
	page.add_field({
		fieldname: 'refresh_interval',
		label: __('Auto Refresh'),
		fieldtype: 'Select',
		options: 'Off\n10 seconds\n30 seconds\n1 minute\n5 minutes',
		default: '30 seconds',
		change: () => setAutoRefresh()
	});

	let refreshInterval = null;
	let charts = {};

	// Initialize dashboard
	$(wrapper).find('.layout-main-section').html(getDashboardHTML());
	refreshDashboard();
	setAutoRefresh();

	function getDashboardHTML() {
		return `
		<div class="command-center-dashboard">
			<style>
				.command-center-dashboard { padding: 15px; }
				.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
				.kpi-card { background: var(--card-bg); border-radius: 8px; padding: 20px; box-shadow: var(--shadow-sm); }
				.kpi-card.alert { border-left: 4px solid var(--red-500); }
				.kpi-card.success { border-left: 4px solid var(--green-500); }
				.kpi-card.warning { border-left: 4px solid var(--yellow-500); }
				.kpi-card.info { border-left: 4px solid var(--blue-500); }
				.kpi-value { font-size: 2.5rem; font-weight: 700; margin-bottom: 5px; }
				.kpi-label { color: var(--text-muted); font-size: 0.9rem; }
				.section-title { font-size: 1.1rem; font-weight: 600; margin: 20px 0 15px; padding-bottom: 10px; border-bottom: 1px solid var(--border-color); }
				.chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 20px; }
				.chart-card { background: var(--card-bg); border-radius: 8px; padding: 20px; box-shadow: var(--shadow-sm); }
				.chart-title { font-weight: 600; margin-bottom: 15px; }
				.events-feed { background: var(--card-bg); border-radius: 8px; padding: 15px; max-height: 400px; overflow-y: auto; }
				.event-item { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid var(--border-color); }
				.event-item:last-child { border-bottom: none; }
				.event-item.denied { background: rgba(239, 68, 68, 0.1); }
				.event-item.alert { background: rgba(245, 158, 11, 0.1); }
				.event-icon { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; }
				.event-icon.granted { background: var(--green-100); color: var(--green-600); }
				.event-icon.denied { background: var(--red-100); color: var(--red-600); }
				.event-details { flex: 1; }
				.event-time { color: var(--text-muted); font-size: 0.8rem; }
				.status-indicator { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
				.status-green { background: var(--green-500); }
				.status-yellow { background: var(--yellow-500); }
				.status-red { background: var(--red-500); }
				.last-updated { color: var(--text-muted); font-size: 0.8rem; text-align: right; margin-bottom: 10px; }
			</style>
			
			<div class="last-updated">Last updated: <span id="last-update-time">-</span></div>
			
			<!-- KPI Cards -->
			<div class="kpi-grid">
				<div class="kpi-card info" id="kpi-employees"><div class="kpi-value">-</div><div class="kpi-label">Employees Onsite</div></div>
				<div class="kpi-card success" id="kpi-visitors"><div class="kpi-value">-</div><div class="kpi-label">Visitors Onsite</div></div>
				<div class="kpi-card warning" id="kpi-contractors"><div class="kpi-value">-</div><div class="kpi-label">Contractors Onsite</div></div>
				<div class="kpi-card info" id="kpi-vehicles"><div class="kpi-value">-</div><div class="kpi-label">Vehicles in Parking</div></div>
				<div class="kpi-card alert" id="kpi-alarms"><div class="kpi-value">-</div><div class="kpi-label">Active Alarms</div></div>
				<div class="kpi-card warning" id="kpi-incidents"><div class="kpi-value">-</div><div class="kpi-label">Open Incidents</div></div>
				<div class="kpi-card info" id="kpi-events"><div class="kpi-value">-</div><div class="kpi-label">Access Events Today</div></div>
				<div class="kpi-card alert" id="kpi-denied"><div class="kpi-value">-</div><div class="kpi-label">Denied Today</div></div>
			</div>

			<div class="section-title">📊 Real-Time Analytics</div>
			<div class="chart-grid">
				<div class="chart-card"><div class="chart-title">Access Events (Last 7 Days)</div><div id="chart-events-trend"></div></div>
				<div class="chart-card"><div class="chart-title">Access by Result</div><div id="chart-by-result"></div></div>
			</div>
			
			<div class="chart-grid">
				<div class="chart-card"><div class="chart-title">Access by Zone</div><div id="chart-by-zone"></div></div>
				<div class="chart-card"><div class="chart-title">Device Health Status</div><div id="chart-device-health"></div></div>
			</div>

			<div class="section-title">📋 Live Access Events Feed</div>
			<div class="events-feed" id="events-feed">
				<div class="text-muted text-center">Loading events...</div>
			</div>
		</div>`;
	}

	function setAutoRefresh() {
		if (refreshInterval) {
			clearInterval(refreshInterval);
			refreshInterval = null;
		}

		const interval = page.fields_dict.refresh_interval.get_value();
		let ms = 0;

		switch(interval) {
			case '10 seconds': ms = 10000; break;
			case '30 seconds': ms = 30000; break;
			case '1 minute': ms = 60000; break;
			case '5 minutes': ms = 300000; break;
		}

		if (ms > 0) {
			refreshInterval = setInterval(refreshDashboard, ms);
		}
	}

	function refreshDashboard() {
		loadKPIData();
		loadChartData();
		loadEventsFeed();
		$('#last-update-time').text(frappe.datetime.now_datetime());
	}

	function loadKPIData() {
		frappe.call({
			method: 'sigma.sigma_access_control.api.dashboard_api.get_command_center_kpis',
			callback: (r) => {
				if (r.message) {
					const data = r.message;
					$('#kpi-employees .kpi-value').text(data.employees_onsite || 0);
					$('#kpi-visitors .kpi-value').text(data.visitors_onsite || 0);
					$('#kpi-contractors .kpi-value').text(data.contractors_onsite || 0);
					$('#kpi-vehicles .kpi-value').text(data.vehicles_in_parking || 0);
					$('#kpi-alarms .kpi-value').text(data.active_alarms || 0);
					$('#kpi-incidents .kpi-value').text(data.open_incidents || 0);
					$('#kpi-events .kpi-value').text(data.events_today || 0);
					$('#kpi-denied .kpi-value').text(data.denied_today || 0);
				}
			}
		});
	}

	function loadChartData() {
		// Events Trend Chart
		frappe.call({
			method: 'sigma.sigma_access_control.api.dashboard_api.get_events_trend',
			callback: (r) => {
				if (r.message && r.message.labels) {
					if (charts.eventsTrend) {
						charts.eventsTrend.update(r.message);
					} else {
						charts.eventsTrend = new frappe.Chart('#chart-events-trend', {
							type: 'line',
							height: 250,
							data: r.message,
							colors: ['#3b82f6']
						});
					}
				}
			}
		});

		// By Result Chart
		frappe.call({
			method: 'sigma.sigma_access_control.api.dashboard_api.get_access_by_result',
			callback: (r) => {
				if (r.message && r.message.labels) {
					if (charts.byResult) {
						charts.byResult.update(r.message);
					} else {
						charts.byResult = new frappe.Chart('#chart-by-result', {
							type: 'pie',
							height: 250,
							data: r.message,
							colors: ['#22c55e', '#ef4444', '#f59e0b', '#3b82f6']
						});
					}
				}
			}
		});

		// By Zone Chart
		frappe.call({
			method: 'sigma.sigma_access_control.api.dashboard_api.get_access_by_zone',
			callback: (r) => {
				if (r.message && r.message.labels) {
					if (charts.byZone) {
						charts.byZone.update(r.message);
					} else {
						charts.byZone = new frappe.Chart('#chart-by-zone', {
							type: 'bar',
							height: 250,
							data: r.message,
							colors: ['#8b5cf6']
						});
					}
				}
			}
		});

		// Device Health Chart
		frappe.call({
			method: 'sigma.sigma_access_control.api.dashboard_api.get_device_health',
			callback: (r) => {
				if (r.message && r.message.labels) {
					if (charts.deviceHealth) {
						charts.deviceHealth.update(r.message);
					} else {
						charts.deviceHealth = new frappe.Chart('#chart-device-health', {
							type: 'donut',
							height: 250,
							data: r.message,
							colors: ['#22c55e', '#f59e0b', '#ef4444']
						});
					}
				}
			}
		});
	}

	function loadEventsFeed() {
		frappe.call({
			method: 'sigma.sigma_access_control.api.dashboard_api.get_recent_events',
			args: { limit: 20 },
			callback: (r) => {
				if (r.message) {
					renderEventsFeed(r.message);
				}
			}
		});
	}

	function renderEventsFeed(events) {
		const container = $('#events-feed');
		if (!events.length) {
			container.html('<div class="text-muted text-center">No recent events</div>');
			return;
		}

		let html = '';
		events.forEach(event => {
			const isAlert = event.result === 'Denied' || event.anomaly_detected;
			const iconClass = event.result === 'Granted' ? 'granted' : 'denied';
			const itemClass = isAlert ? (event.result === 'Denied' ? 'denied' : 'alert') : '';

			html += `
			<div class="event-item ${itemClass}">
				<div class="event-icon ${iconClass}">
					<i class="fa fa-${event.result === 'Granted' ? 'check' : 'times'}"></i>
				</div>
				<div class="event-details">
					<div><strong>${event.event_type}</strong> - ${event.person_name || 'Unknown'}</div>
					<div class="text-muted">${event.access_point_name || event.access_point} | ${event.zone || '-'}</div>
				</div>
				<div class="event-time">${frappe.datetime.prettyDate(event.event_time)}</div>
			</div>`;
		});
		container.html(html);
	}
};

