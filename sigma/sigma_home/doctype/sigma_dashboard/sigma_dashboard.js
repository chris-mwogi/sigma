// Copyright (c) 2025
// Prismod Technologies Limited / Nevel Enterprises
// Sigma Unified Dashboard Desk Script

frappe.ui.form.on('Sigma Dashboard', {
    refresh(frm) {
        frm.disable_save();

        // --- Add Refresh Button ---
        frm.add_custom_button(__('Refresh Data'), function() {
            frappe.call({
                method: "sigma.sigma.doctype.sigma_dashboard.sigma_dashboard.refresh_cache",
                callback: function() {
                    frappe.show_alert({
                        message: __("Dashboard cache refreshed"),
                        indicator: "green"
                    });
                    frm.reload_doc();
                }
            });
        }).addClass("btn-primary");

        // --- Fetch and Render Dashboard Data ---
        frm.call('get_summary_data', {}, function(r) {
            if (!r.message) return;
            const data = r.message;

            // Build KPI HTML
            let html = `
                <div class="dashboard-section">
                    <div class="widget" style="display:flex; flex-wrap:wrap; gap:20px;">
                        ${make_box("Open Calls", data.open_calls, "#dce8ff")}
                        ${make_box("Support Tickets", data.open_tickets, "#e1ffd6")}
                        ${make_box("Active Guards", data.active_guards, "#ffe6cc")}
                        ${make_box("Pending Cases", data.pending_cases, "#ffe0e0")}
                        ${make_box("Access Events Today", data.access_events_today, "#e8e8e8")}
                        ${make_box("Open Risks", data.open_risks, "#fff7d6")}
                    </div>
                </div>
                <hr>
                <div id="chart-calls" style="height:250px;"></div>
                <div id="chart-cases" style="height:250px;"></div>
                <div id="chart-guards" style="height:250px;"></div>
                <div id="chart-risk" style="height:250px;"></div>
            `;

            frm.fields_dict.dashboard_html.$wrapper.html(html);

            // --- Chart Helper ---
            function render_chart(container, title, labels, values, type="line", colors=["blue"]) {
                if (!labels || !values) return;
                new frappe.Chart(container, {
                    title: title,
                    data: {
                        labels: labels,
                        datasets: [{ values: values }]
                    },
                    type: type,
                    colors: colors,
                    height: 240
                });
            }

            // --- Render Charts ---
            render_chart("#chart-calls", "Call Volume (Last 7 Days)", data.call_chart.labels, data.call_chart.values, "line", ["#1E90FF"]);
            render_chart("#chart-cases", "Case Status Distribution", data.case_chart.labels, data.case_chart.values, "bar", ["#9370DB"]);
            render_chart("#chart-guards", "Guard Activity", data.guard_chart.labels, data.guard_chart.values, "pie", ["#FF8C00", "#B0C4DE"]);
            render_chart("#chart-risk", "Risk Levels", data.risk_chart.labels, data.risk_chart.values, "donut", ["#DC143C", "#FFD700", "#32CD32"]);
        });

        // --- KPI Card Builder ---
        function make_box(label, value, color) {
            return `
                <div class="stat-box" style="background:${color}; padding:15px; border-radius:8px; flex:1;">
                    <h4>${label}</h4><h2>${value ?? 0}</h2>
                </div>`;
        }

        // --- Optional Auto-Refresh every 60s ---
        if (!frm.auto_refresh_set) {
            frm.auto_refresh_set = true;
            setInterval(() => {
                if (cur_frm && cur_frm.doc.doctype === "Sigma Dashboard") {
                    frm.reload_doc();
                }
            }, 60000);
        }
    }
});
