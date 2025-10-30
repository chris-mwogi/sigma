frappe.pages['access-control-dashboard'] = frappe.pages['access-control-dashboard'] || {};

frappe.pages['access-control-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Access Control Dashboard',
        single_column: true
    });

    const $body = $("<div class='access-control-dashboard p-3'></div>")
    $body.append("<h4>Recent Access Events</h4>")
    $body.append("<div id='recent_access_events'></div>")
    $(page.body).append($body)

    frappe.realtime.on('access_denied', data => {
        $('#recent_access_events').prepend($('<div>').text('Denied at: ' + (data.point || 'unknown')))
        frappe.show_alert({message: 'Access denied: ' + (data.point || ''), indicator: 'red'})
    })
}
