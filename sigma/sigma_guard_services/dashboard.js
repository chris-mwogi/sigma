// Sigma Guard Monitoring Dashboard
// Handles dashboard initialization, data loading, and chart rendering

frappe.provide('sigma.dashboard');

sigma.dashboard.Dashboard = class {
	constructor() {
		this.charts = {};
		this.data = {};
		this.init();
	}

	init() {
		this.loadDashboardData();
		this.initializeCharts();
		this.setupRefreshInterval();
	}

	loadDashboardData() {
		// Load all dashboard data
		frappe.call({
			method: 'sigma.sigma_guard_monitoring.dashboard_sources.get_provider_performance_data',
			callback: (r) => {
				if (r.message) {
					this.data.provider_performance = r.message.data;
					this.updateProviderCharts();
				}
			}
		});

		frappe.call({
			method: 'sigma.sigma_guard_monitoring.dashboard_sources.get_sla_compliance_trends',
			callback: (r) => {
				if (r.message) {
					this.data.compliance_trends = r.message.data;
					this.updateComplianceCharts();
				}
			}
		});

		frappe.call({
			method: 'sigma.sigma_guard_monitoring.dashboard_sources.get_financial_impact_data',
			callback: (r) => {
				if (r.message) {
					this.data.financial_impact = r.message.data;
					this.updateFinancialCharts();
				}
			}
		});

		frappe.call({
			method: 'sigma.sigma_guard_monitoring.dashboard_sources.get_patrol_summary_data',
			callback: (r) => {
				if (r.message) {
					this.data.patrol_summary = r.message.data;
					this.updatePatrolCharts();
				}
			}
		});

		frappe.call({
			method: 'sigma.sigma_guard_monitoring.dashboard_sources.get_resource_deployment_data',
			callback: (r) => {
				if (r.message) {
					this.data.resource_deployment = r.message.data;
					this.updateResourceCharts();
				}
			}
		});

		frappe.call({
			method: 'sigma.sigma_guard_monitoring.dashboard_sources.get_visitor_management_data',
			callback: (r) => {
				if (r.message) {
					this.data.visitor_management = r.message.data;
					this.updateVisitorCharts();
				}
			}
		});
	}

	initializeCharts() {
		// Initialize Chart.js instances for all charts
		this.createResourceDeploymentChart();
		this.createResourceAvailabilityChart();
		this.createComplianceTrendChart();
		this.createComplianceStatusChart();
		this.createPatrolCompletionChart();
		this.createDiscrepancySeverityChart();
		this.createSurchargesChart();
		this.createSurchargeMethodChart();
		this.createVisitorAssignmentChart();
		this.createEvacuationStatusChart();
	}

	createResourceDeploymentChart() {
		const ctx = document.getElementById('resourceDeploymentChart');
		if (!ctx) return;

		this.charts.resourceDeployment = new Chart(ctx, {
			type: 'doughnut',
			data: {
				labels: ['Guard', 'K9', 'Vehicle', 'Equipment', 'Station'],
				datasets: [{
					data: [0, 0, 0, 0, 0],
					backgroundColor: [
						'#FF6384',
						'#36A2EB',
						'#FFCE56',
						'#4BC0C0',
						'#9966FF'
					]
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Resource Deployment by Type'
					}
				}
			}
		});
	}

	createResourceAvailabilityChart() {
		const ctx = document.getElementById('resourceAvailabilityChart');
		if (!ctx) return;

		this.charts.resourceAvailability = new Chart(ctx, {
			type: 'bar',
			data: {
				labels: ['Guard', 'K9', 'Vehicle', 'Equipment', 'Station'],
				datasets: [
					{
						label: 'Active',
						data: [0, 0, 0, 0, 0],
						backgroundColor: '#4CAF50'
					},
					{
						label: 'Inactive',
						data: [0, 0, 0, 0, 0],
						backgroundColor: '#F44336'
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Resource Availability'
					}
				},
				scales: {
					x: { stacked: true },
					y: { stacked: true }
				}
			}
		});
	}

	createComplianceTrendChart() {
		const ctx = document.getElementById('complianceTrendChart');
		if (!ctx) return;

		this.charts.complianceTrend = new Chart(ctx, {
			type: 'line',
			data: {
				labels: [],
				datasets: [{
					label: 'Compliance Score',
					data: [],
					borderColor: '#007bff',
					backgroundColor: 'rgba(0, 123, 255, 0.1)',
					tension: 0.4,
					fill: true
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'SLA Compliance Trend (30 Days)'
					}
				},
				scales: {
					y: {
						beginAtZero: true,
						max: 100
					}
				}
			}
		});
	}

	createComplianceStatusChart() {
		const ctx = document.getElementById('complianceStatusChart');
		if (!ctx) return;

		this.charts.complianceStatus = new Chart(ctx, {
			type: 'pie',
			data: {
				labels: ['Compliant', 'Non-Compliant'],
				datasets: [{
					data: [0, 0],
					backgroundColor: ['#4CAF50', '#F44336']
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Compliance Status Distribution'
					}
				}
			}
		});
	}

	createPatrolCompletionChart() {
		const ctx = document.getElementById('patrolCompletionChart');
		if (!ctx) return;

		this.charts.patrolCompletion = new Chart(ctx, {
			type: 'doughnut',
			data: {
				labels: ['Completed', 'In Progress', 'Scheduled', 'Cancelled'],
				datasets: [{
					data: [0, 0, 0, 0],
					backgroundColor: ['#4CAF50', '#2196F3', '#FFC107', '#F44336']
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Patrol Schedule Status'
					}
				}
			}
		});
	}

	createDiscrepancySeverityChart() {
		const ctx = document.getElementById('discrepancySeverityChart');
		if (!ctx) return;

		this.charts.discrepancySeverity = new Chart(ctx, {
			type: 'bar',
			data: {
				labels: ['Low', 'Medium', 'High', 'Critical'],
				datasets: [{
					label: 'Discrepancies',
					data: [0, 0, 0, 0],
					backgroundColor: ['#FFC107', '#FF9800', '#F44336', '#9C27B0']
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Discrepancies by Severity'
					}
				}
			}
		});
	}

	createSurchargesChart() {
		const ctx = document.getElementById('surchargesChart');
		if (!ctx) return;

		this.charts.surcharges = new Chart(ctx, {
			type: 'line',
			data: {
				labels: [],
				datasets: [{
					label: 'Surcharges',
					data: [],
					borderColor: '#F44336',
					backgroundColor: 'rgba(244, 67, 54, 0.1)',
					tension: 0.4,
					fill: true
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Surcharges Over Time'
					}
				}
			}
		});
	}

	createSurchargeMethodChart() {
		const ctx = document.getElementById('surchargeMethodChart');
		if (!ctx) return;

		this.charts.surchargeMethod = new Chart(ctx, {
			type: 'pie',
			data: {
				labels: [],
				datasets: [{
					data: [],
					backgroundColor: [
						'#FF6384',
						'#36A2EB',
						'#FFCE56',
						'#4BC0C0'
					]
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Surcharges by Method'
					}
				}
			}
		});
	}

	createVisitorAssignmentChart() {
		const ctx = document.getElementById('visitorAssignmentChart');
		if (!ctx) return;

		this.charts.visitorAssignment = new Chart(ctx, {
			type: 'doughnut',
			data: {
				labels: ['Active', 'Checked Out'],
				datasets: [{
					data: [0, 0],
					backgroundColor: ['#2196F3', '#4CAF50']
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Visitor Assignment Status'
					}
				}
			}
		});
	}

	createEvacuationStatusChart() {
		const ctx = document.getElementById('evacuationStatusChart');
		if (!ctx) return;

		this.charts.evacuationStatus = new Chart(ctx, {
			type: 'bar',
			data: {
				labels: ['Completed', 'In Progress', 'Initiated'],
				datasets: [{
					label: 'Evacuations',
					data: [0, 0, 0],
					backgroundColor: ['#4CAF50', '#2196F3', '#FFC107']
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					title: {
						display: true,
						text: 'Evacuation Status'
					}
				}
			}
		});
	}

	updateProviderCharts() {
		// Update provider performance charts
		if (this.data.provider_performance) {
			// Update charts with provider data
		}
	}

	updateComplianceCharts() {
		// Update compliance charts
		if (this.data.compliance_trends && this.charts.complianceTrend) {
			const labels = this.data.compliance_trends.map(d => d.date);
			const scores = this.data.compliance_trends.map(d => d.avg_score);
			
			this.charts.complianceTrend.data.labels = labels;
			this.charts.complianceTrend.data.datasets[0].data = scores;
			this.charts.complianceTrend.update();
		}
	}

	updateFinancialCharts() {
		// Update financial charts
		if (this.data.financial_impact) {
			// Update charts with financial data
		}
	}

	updatePatrolCharts() {
		// Update patrol charts
		if (this.data.patrol_summary && this.charts.patrolCompletion) {
			const summary = this.data.patrol_summary;
			this.charts.patrolCompletion.data.datasets[0].data = [
				summary.completed_schedules,
				summary.in_progress_schedules,
				summary.scheduled_schedules,
				0
			];
			this.charts.patrolCompletion.update();
		}
	}

	updateResourceCharts() {
		// Update resource charts
		if (this.data.resource_deployment) {
			// Update charts with resource data
		}
	}

	updateVisitorCharts() {
		// Update visitor charts
		if (this.data.visitor_management) {
			// Update charts with visitor data
		}
	}

	refreshDashboard() {
		this.loadDashboardData();
	}

	exportDashboard() {
		// Export dashboard data to CSV/PDF
		frappe.msgprint('Dashboard export functionality coming soon');
	}

	setupRefreshInterval() {
		// Auto-refresh dashboard every 5 minutes
		setInterval(() => {
			this.refreshDashboard();
		}, 5 * 60 * 1000);
	}
};

// Initialize dashboard when page loads
frappe.ready(() => {
	if (document.getElementById('sigma-dashboard')) {
		new sigma.dashboard.Dashboard();
	}
});

