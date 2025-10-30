frappe.provide('sigma.risk_dashboard');

sigma.risk_dashboard.render = function(wrapper) {
    wrapper.innerHTML = '<div>Loading risk dashboard...</div>';
    frappe.call({
        method: 'sigma.sigma_risk_assessment.api.get_risk_summary',
        callback: function(r) {
            let data = r.message || {};
            let html = '<h3>Risk Summary</h3>';
            html += '<h4>By Level</h4><ul>';
            (data.by_level || []).forEach(function(d){ html += `<li>${d.risk_level}: ${d.count}</li>`});
            html += '</ul>';
            html += '<h4>Top Open Risks</h4><ol>';
            (data.top_open || []).forEach(function(t){ html += `<li>${t.assessment_title} (${t.risk_level}) - ${t.risk_score}</li>`});
            html += '</ol>';
            wrapper.innerHTML = html;
        }
    })
}
