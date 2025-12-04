frappe.pages['sigma-dashboard'].on_page_load = function(wrapper) {
	// Create Frappe page
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Sigma Dashboard',
		single_column: true
	});

	// Add custom CSS files
	frappe.require([
		'/assets/sigma/css/enhanced-sidebar.css',
		'/assets/sigma/css/dashboard-layout.css',
		'/assets/sigma/css/dashboard-widgets.css'
	], function() {
		// CSS loaded
	});

	// Create dashboard container
	const $container = $('<div id="sigma-dashboard-app"></div>').appendTo(page.main);

	// Initialize dashboard with standard Frappe patterns
	initializeDashboard($container, page);
};

function initializeDashboard($container, page) {
	// Dashboard state
	let metrics = {
		open_cases: 0,
		access_events_today: 0,
		denied_access_today: 0,
		active_guards: 0,
		active_visitors: 0,
		vehicles_in_premises: 0
	};

	let isConnected = false;
	let lastUpdated = '';
	let charts = {};

	// Build dashboard HTML structure
	const dashboardHTML = `
		<div class="sigma-dashboard-wrapper">
			<div class="sigma-dashboard-enhanced">
				<!-- Dashboard Page Header -->
				<div class="dashboard-page-header">
					<div class="page-title-section">
						<h1 class="page-title">Security Operations Dashboard</h1>
						<p class="page-subtitle">Real-time overview of your security operations</p>
					</div>
					<div class="header-actions">
						<button id="refresh-btn" class="btn btn-primary btn-sm">
							<i class="ti ti-refresh"></i>
							<span>Refresh</span>
						</button>
					</div>
				</div>

				<!-- KPI Cards Grid -->
				<div class="kpi-grid" id="kpi-grid"></div>

				<!-- Charts Section -->
				<div class="charts-grid">
					<div class="chart-card">
						<div class="chart-header">
							<div>
								<h3 class="chart-title">Cases by Status</h3>
								<p class="chart-subtitle">Current case distribution</p>
							</div>
						</div>
						<div class="chart-body">
							<div id="casesChart"></div>
						</div>
					</div>

					<div class="chart-card">
						<div class="chart-header">
							<div>
								<h3 class="chart-title">Access Events Trend</h3>
								<p class="chart-subtitle">Last 7 days</p>
							</div>
						</div>
						<div class="chart-body">
							<div id="accessChart"></div>
						</div>
					</div>
				</div>

				<!-- Real-time Status Bar -->
				<div class="realtime-status-bar">
					<div class="status-indicator" id="status-indicator">
						<i class="ti ti-circle-filled"></i>
						<span id="status-text">Disconnected</span>
					</div>
					<div class="last-updated">
						Last updated: <span id="last-updated-time">--:--:--</span>
					</div>
				</div>
			</div>
		</div>
	`;

	$container.html(dashboardHTML);

	// Helper function to create KPI card
	function createKPICard(config) {
		const $card = $(`
			<div class="kpi-card ${config.type}">
				<div class="kpi-header">
					<div class="kpi-icon">
						<i class="${config.icon}"></i>
					</div>
					<div class="kpi-trend ${config.trendType}">
						<i class="ti ti-trending-${config.trendType === 'up' ? 'up' : config.trendType === 'down' ? 'down' : 'minus'}"></i>
						<span>${config.trend}</span>
					</div>
				</div>
				<div class="kpi-body">
					<div class="kpi-value">${config.value}</div>
					<div class="kpi-label">${config.label}</div>
				</div>
				<div class="kpi-footer">
					<a class="kpi-link">
						View all <i class="ti ti-arrow-right"></i>
					</a>
				</div>
			</div>
		`);

		$card.on('click', () => frappe.set_route(config.route));
		return $card;
	}

	// Render KPI cards
	function renderKPICards() {
		const kpiConfigs = [
			{
				type: 'critical',
				icon: 'ti ti-alert-circle',
				trendType: 'up',
				trend: '+12%',
				value: metrics.open_cases,
				label: 'Open Cases',
				route: '/app/case-record'
			},
			{
				type: 'warning',
				icon: 'ti ti-lock-x',
				trendType: 'down',
				trend: '-5%',
				value: metrics.denied_access_today,
				label: 'Access Denied Today',
				route: '/app/access-event'
			},
			{
				type: 'success',
				icon: 'ti ti-shield-check',
				trendType: 'up',
				trend: '+8%',
				value: metrics.active_guards,
				label: 'Active Guards',
				route: '/app/guard-shift'
			},
			{
				type: 'info',
				icon: 'ti ti-door-enter',
				trendType: 'up',
				trend: '+23%',
				value: metrics.access_events_today,
				label: 'Access Events Today',
				route: '/app/access-event'
			},
			{
				type: 'purple',
				icon: 'ti ti-users',
				trendType: 'up',
				trend: '+15%',
				value: metrics.active_visitors,
				label: 'Active Visitors',
				route: '/app/visitor'
			},
			{
				type: 'orange',
				icon: 'ti ti-car',
				trendType: 'neutral',
				trend: '0%',
				value: metrics.vehicles_in_premises,
				label: 'Vehicles in Premises',
				route: '/app/vehicle-log'
			}
		];

		const $kpiGrid = $('#kpi-grid');
		$kpiGrid.empty();
		kpiConfigs.forEach(config => {
			$kpiGrid.append(createKPICard(config));
		});
	}

	// Initialize charts using Frappe Charts
	function initializeCharts() {
		// Cases by Status Chart
		if (!charts.casesChart) {
			charts.casesChart = new frappe.Chart('#casesChart', {
				type: 'donut',
				height: 240,
				data: {
					labels: ['Open', 'In Progress', 'Resolved', 'Closed'],
					datasets: [{
						values: [12, 19, 8, 5]
					}]
				},
				colors: ['#ef4444', '#f59e0b', '#22c55e', '#3b82f6']
			});
		}

		// Access Events Trend Chart
		if (!charts.accessChart) {
			charts.accessChart = new frappe.Chart('#accessChart', {
				type: 'line',
				height: 240,
				data: {
					labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
					datasets: [{
						name: 'Access Events',
						values: [65, 59, 80, 81, 56, 55, 40]
					}]
				},
				colors: ['#3b82f6']
			});
		}
	}

	// Update last updated timestamp
	function updateLastUpdated() {
		const now = new Date();
		lastUpdated = now.toLocaleTimeString();
		$('#last-updated-time').text(lastUpdated);
	}

	// Update connection status
	function updateConnectionStatus(connected) {
		isConnected = connected;
		const $indicator = $('#status-indicator');
		const $statusText = $('#status-text');

		if (connected) {
			$indicator.addClass('connected');
			$statusText.text('Real-time Connected');
		} else {
			$indicator.removeClass('connected');
			$statusText.text('Disconnected');
		}
	}

	// Load dashboard data from backend
	function loadDashboardData() {
		frappe.call({
			method: 'sigma.api.dashboard.get_dashboard_data',
			callback: (r) => {
				if (r.message && r.message.data) {
					metrics = r.message.data;
					renderKPICards();
					updateLastUpdated();
					initializeCharts();
				}
			},
			error: (r) => {
				frappe.show_alert({
					message: 'Failed to load dashboard data',
					indicator: 'red'
				});
			}
		});
	}

	// Refresh dashboard data
	function refreshData() {
		loadDashboardData();
		frappe.show_alert({
			message: 'Dashboard refreshed',
			indicator: 'green'
		});
	}

	// Event handlers
	$('#refresh-btn').on('click', refreshData);

	// Initialize dashboard
	loadDashboardData();
	updateConnectionStatus(true);

	// Update timestamp every minute
	setInterval(() => {
		updateLastUpdated();
	}, 60000);
}

