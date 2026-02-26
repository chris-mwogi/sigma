// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manning Allocation', {
    refresh: function(frm) {
        // Add button to create guard assignments
        if (frm.doc.docstatus === 1 && frm.doc.status !== 'Fully Staffed') {
            frm.add_custom_button(__('Create Guard Assignment'), function() {
                frappe.new_doc('Guard Assignment', {
                    manning_allocation: frm.doc.name,
                    security_firm: frm.doc.security_firm,
                    location: frm.doc.location
                });
            }, __('Actions'));
        }

        // Show allocation summary
        if (frm.doc.manning_slots && frm.doc.manning_slots.length > 0) {
            let summary = get_allocation_summary(frm.doc.manning_slots);
            frm.set_df_property('manning_slots', 'description', summary);
        }

        // Set zone filter based on location
        frm.set_query('zone', function() {
            return {
                filters: {
                    'location': frm.doc.location,
                    'is_active': 1
                }
            };
        });
    },

    location: function(frm) {
        // Clear zone when location changes
        if (frm.doc.zone) {
            frm.set_value('zone', '');
        }
        // Re-apply zone filter
        frm.set_query('zone', function() {
            return {
                filters: {
                    'location': frm.doc.location,
                    'is_active': 1
                }
            };
        });
    },

    service_contract: function(frm) {
        // Auto-fill security firm (party) and project from contract
        if (frm.doc.service_contract) {
            frappe.db.get_doc('Contract', frm.doc.service_contract)
                .then(contract => {
                    if (contract.party_type === 'Supplier') {
                        frm.set_value('security_firm', contract.party_name);
                    }
                    // If contract is linked to a project, set it
                    if (contract.document_type === 'Project' && contract.document_name) {
                        frm.set_value('project', contract.document_name);
                    }
                });
        }
    },

    security_firm: function(frm) {
        // Filter security resources by supplier
        frm.set_query('security_firm', function() {
            return {
                filters: {
                    'supplier_group': 'Security Services'
                }
            };
        });
    },

    setup: function(frm) {
        // Filter contract to show only supplier contracts
        frm.set_query('service_contract', function() {
            let filters = {
                'party_type': 'Supplier',
                'status': 'Active',
                'docstatus': 1
            };
            if (frm.doc.security_firm) {
                filters['party_name'] = frm.doc.security_firm;
            }
            return { filters: filters };
        });

        // Filter project
        frm.set_query('project', function() {
            return {
                filters: {
                    'status': ['not in', ['Completed', 'Cancelled']]
                }
            };
        });
    }
});

frappe.ui.form.on('Manning Slot Item', {
    resource_type: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },
    
    quantity: function(frm, cdt, cdn) {
        calculate_totals(frm);
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
        } else if (row.shift_type === '24 Hour') {
            frappe.model.set_value(cdt, cdn, 'start_time', '00:00:00');
            frappe.model.set_value(cdt, cdn, 'end_time', '23:59:59');
        }
    },
    
    manning_slots_remove: function(frm) {
        calculate_totals(frm);
    }
});

function calculate_totals(frm) {
    let total_guards = 0;
    let total_k9 = 0;
    let total_supervisors = 0;
    
    (frm.doc.manning_slots || []).forEach(function(row) {
        if (['Security Guard', 'Armed Guard', 'Access Controller'].includes(row.resource_type)) {
            total_guards += row.quantity || 0;
        } else if (['K9 Unit', 'K9 Handler'].includes(row.resource_type)) {
            total_k9 += row.quantity || 0;
        } else if (row.resource_type === 'Security Supervisor') {
            total_supervisors += row.quantity || 0;
        }
    });
    
    frm.set_value('total_guards', total_guards);
    frm.set_value('total_k9_units', total_k9);
    frm.set_value('total_supervisors', total_supervisors);
}

function get_allocation_summary(slots) {
    let day_count = 0;
    let night_count = 0;
    let k9_count = 0;
    
    slots.forEach(function(slot) {
        if (slot.shift_type === 'Day Shift') {
            day_count += slot.quantity || 0;
        } else if (slot.shift_type === 'Night Shift') {
            night_count += slot.quantity || 0;
        }
        if (['K9 Unit', 'K9 Handler'].includes(slot.resource_type)) {
            k9_count += slot.quantity || 0;
        }
    });
    
    return `<b>Summary:</b> Day: ${day_count}, Night: ${night_count}, K9: ${k9_count}`;
}

