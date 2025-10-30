frappe.pages['case-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Case Management Dashboard',
        single_column: true
    });

    $(frappe.render_template("case_dashboard", {})).appendTo(page.body);

    frappe.call({
        method: "sigma.sigma.sigma_case_management.page.case_dashboard.case_dashboard.get_case_summary",
        callback: function(r) {
            if (r.message) {
                $("#case-stats").html(`
                    <div><b>Open Cases:</b> ${r.message.open}</div>
                    <div><b>Resolved Cases:</b> ${r.message.resolved}</div>
                    <div><b>Pending Legal:</b> ${r.message.awaiting_legal}</div>
                `);
            }
        }
    });
};
