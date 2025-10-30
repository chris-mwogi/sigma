// Sigma Dashboard Page - sigma_desk.js
// This file initializes the sigma-desk page and creates an iframe for the dashboard

frappe.pages['sigma-desk'] = {
  on_page_load: function (wrapper) {
    const page = frappe.ui.make_app_page({
      parent: wrapper,
      title: __('Sigma Dashboard'),
      single_column: true,
    });

    const container = $(
      '<div style="height: calc(100vh - 160px);"><iframe src="/sigma-dashboard" style="width:100%; height:100%; border:0; border-radius:6px; background:white;"></iframe></div>'
    );

    $(page.body).empty().append(container);
  },
};