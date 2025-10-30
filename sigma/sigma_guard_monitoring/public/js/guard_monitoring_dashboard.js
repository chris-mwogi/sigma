frappe.pages['guard-monitoring-dashboard'] = {
    on_page_load: function(wrapper) {
        let page = frappe.ui.make_app_page({
            parent: wrapper,
            title: 'Guard Monitoring Dashboard',
            single_column: true
        });

        $(frappe.render_template(`
            <div class="p-4">
                <h3>Guard Monitoring Overview</h3>
                <div id="guard-stats"></div>
            </div>
        `)).appendTo(page.body);

        frappe.call({
            method: 'sigma.sigma.sigma_guard_monitoring.sigma_guard_monitoring.api.guard_monitoring_api.get_overview',
            callback: function(r) {
                $('#guard-stats').html(r.message || 'No data yet.');
            }
        });
    }
};
