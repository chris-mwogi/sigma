// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Guard Assignment', {
    refresh: function(frm) {
        // Filter security resources by supplier
        frm.set_query('security_resource', 'assigned_guards', function() {
            return {
                filters: {
                    'supplier': frm.doc.security_firm,
                    'status': ['in', ['Available', 'Deployed']],
                    'resource_type': ['in', ['Security Guard', 'Security Supervisor', 'Guard Dog', 'K9 Handler', 'Armed Guard']]
                }
            };
        });

        // Filter zone by location
        frm.set_query('zone', function() {
            return {
                filters: {
                    'location': frm.doc.location,
                    'is_active': 1
                }
            };
        });

        // Show allocation summary
        if (frm.doc.manning_allocation) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Manning Allocation',
                    name: frm.doc.manning_allocation
                },
                callback: function(r) {
                    if (r.message) {
                        let allocation = r.message;
                        let summary = `<b>Required:</b> Guards: ${allocation.total_guards}, K9: ${allocation.total_k9_units}, Supervisors: ${allocation.total_supervisors}`;
                        frm.set_value('allocation_details', summary);
                    }
                }
            });
        }
    },

    location: function(frm) {
        // Clear zone when location changes
        if (frm.doc.zone) {
            frm.set_value('zone', '');
        }
    },
    
    manning_allocation: function(frm) {
        if (frm.doc.manning_allocation) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Manning Allocation',
                    name: frm.doc.manning_allocation
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('security_firm', r.message.security_firm);
                        frm.set_value('location', r.message.location);
                        frm.set_value('zone', r.message.zone);
                    }
                }
            });
        }
    },
    
    security_firm: function(frm) {
        // Clear assigned guards when security firm changes
        if (frm.doc.assigned_guards && frm.doc.assigned_guards.length > 0) {
            frappe.confirm(
                __('Changing security firm will clear assigned guards. Continue?'),
                function() {
                    frm.clear_table('assigned_guards');
                    frm.refresh_field('assigned_guards');
                },
                function() {
                    // Revert to previous value
                    frm.reload_doc();
                }
            );
        }
    }
});

frappe.ui.form.on('Guard Assignment Item', {
    security_resource: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.security_resource) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Security Resource',
                    name: row.security_resource
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'resource_name', r.message.resource_name);
                        frappe.model.set_value(cdt, cdn, 'resource_type', r.message.resource_type);
                    }
                }
            });
        }
        calculate_stats(frm);
    },
    
    shift_type: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Set default times based on shift type
        if (row.shift_type === 'Day Shift') {
            frappe.model.set_value(cdt, cdn, 'start_time', '06:00:00');
            frappe.model.set_value(cdt, cdn, 'end_time', '18:00:00');
        } else if (row.shift_type === 'Night Shift') {
            frappe.model.set_value(cdt, cdn, 'start_time', '18:00:00');
            frappe.model.set_value(cdt, cdn, 'end_time', '06:00:00');
        }
        calculate_stats(frm);
    },
    
    assigned_guards_remove: function(frm) {
        calculate_stats(frm);
    }
});

function calculate_stats(frm) {
    let total = (frm.doc.assigned_guards || []).length;
    let day_shift = (frm.doc.assigned_guards || []).filter(g => g.shift_type === 'Day Shift').length;
    let night_shift = (frm.doc.assigned_guards || []).filter(g => g.shift_type === 'Night Shift').length;
    
    frm.set_value('total_assigned', total);
    frm.set_value('day_shift_count', day_shift);
    frm.set_value('night_shift_count', night_shift);
}

