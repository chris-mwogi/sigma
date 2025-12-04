// Copyright (c) 2025, Sigma Security Management System
// License: MIT

frappe.ui.form.on('Asset', {
	refresh: function(frm) {
		// Set custom buttons and actions
		if (frm.doc.docstatus === 1) {
			// Add custom buttons for submitted assets
			frm.add_custom_button(__('View Components'), function() {
				if (frm.doc.is_composite_asset && frm.doc.components) {
					frappe.msgprint({
						title: __('Asset Components'),
						message: __('This asset has {0} components', [frm.doc.components.length]),
						indicator: 'blue'
					});
				} else {
					frappe.msgprint(__('This asset has no components'));
				}
			});
		}

		// Set field properties based on document state
		set_field_properties(frm);
		
		// Calculate and display component statistics
		if (frm.doc.is_composite_asset && frm.doc.components) {
			show_component_statistics(frm);
		}
	},

	item_code: function(frm) {
		// Fetch item details when item code is selected
		if (frm.doc.item_code) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Item',
					name: frm.doc.item_code
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('item_name', r.message.item_name);
						if (!frm.doc.asset_name) {
							frm.set_value('asset_name', r.message.item_name);
						}
					}
				}
			});
		}
	},

	is_composite_asset: function(frm) {
		// Show/hide components section based on is_composite_asset flag
		frm.toggle_display('components_section', frm.doc.is_composite_asset);
		
		if (frm.doc.is_composite_asset) {
			frappe.msgprint({
				title: __('Composite Asset'),
				message: __('You can now add components to this asset in the Components section below.'),
				indicator: 'blue'
			});
		}
	},

	purchase_amount: function(frm) {
		// Auto-set gross purchase amount if not set
		if (frm.doc.purchase_amount && !frm.doc.gross_purchase_amount) {
			frm.set_value('gross_purchase_amount', frm.doc.purchase_amount);
		}
	},

	requires_maintenance: function(frm) {
		// Show/hide maintenance frequency based on requires_maintenance flag
		frm.toggle_reqd('maintenance_frequency', frm.doc.requires_maintenance);
	}
});

// Child table: Asset Component
frappe.ui.form.on('Asset Component', {
	component_cost: function(frm, cdt, cdn) {
		// Recalculate total component cost
		calculate_total_component_cost(frm);
	},

	components_remove: function(frm) {
		// Recalculate total component cost when component is removed
		calculate_total_component_cost(frm);
	},

	is_networked_component: function(frm, cdt, cdn) {
		// Show message when networked component is checked
		let row = locals[cdt][cdn];
		if (row.is_networked_component) {
			frappe.msgprint({
				title: __('Networked Component'),
				message: __('You can now add network information for this component.'),
				indicator: 'blue'
			});
		}
	},

	is_iot_component: function(frm, cdt, cdn) {
		// Show message when IoT component is checked
		let row = locals[cdt][cdn];
		if (row.is_iot_component) {
			frappe.msgprint({
				title: __('IoT Component'),
				message: __('You can now add IoT configuration for this component.'),
				indicator: 'blue'
			});
		}
	},

	is_tracked_component: function(frm, cdt, cdn) {
		// Show message when tracked component is checked
		let row = locals[cdt][cdn];
		if (row.is_tracked_component) {
			frappe.msgprint({
				title: __('GPS Tracked Component'),
				message: __('You can now add GPS coordinates for this component.'),
				indicator: 'blue'
			});
		}
	}
});

// Helper functions
function set_field_properties(frm) {
	// Set field properties based on document state
	if (frm.doc.docstatus === 1) {
		// Make certain fields read-only after submission
		frm.set_df_property('item_code', 'read_only', 1);
		frm.set_df_property('asset_category', 'read_only', 1);
		frm.set_df_property('company', 'read_only', 1);
	}
}

function calculate_total_component_cost(frm) {
	// Calculate total cost of all components
	if (frm.doc.is_composite_asset && frm.doc.components) {
		let total = 0;
		frm.doc.components.forEach(function(component) {
			total += flt(component.component_cost);
		});
		
		// Update purchase amount if not manually set
		if (total > 0 && !frm.doc.purchase_amount) {
			frm.set_value('purchase_amount', total);
		}
		
		// Show total in a message
		frm.dashboard.set_headline_alert(
			__('Total Component Cost: {0}', [format_currency(total, frm.doc.currency)]),
			'blue'
		);
	}
}

function show_component_statistics(frm) {
	// Show component statistics
	let total_components = frm.doc.components.length;
	let active_components = frm.doc.components.filter(c => c.status === 'Active').length;
	let networked_components = frm.doc.components.filter(c => c.is_networked_component).length;
	let iot_components = frm.doc.components.filter(c => c.is_iot_component).length;
	let tracked_components = frm.doc.components.filter(c => c.is_tracked_component).length;
	
	let stats_html = `
		<div class="row">
			<div class="col-sm-3">
				<div class="alert alert-info">
					<strong>${total_components}</strong><br>Total Components
				</div>
			</div>
			<div class="col-sm-3">
				<div class="alert alert-success">
					<strong>${active_components}</strong><br>Active
				</div>
			</div>
			<div class="col-sm-3">
				<div class="alert alert-primary">
					<strong>${networked_components}</strong><br>Networked
				</div>
			</div>
			<div class="col-sm-3">
				<div class="alert alert-warning">
					<strong>${iot_components}</strong><br>IoT Devices
				</div>
			</div>
		</div>
	`;
	
	frm.dashboard.add_section(stats_html, __('Component Statistics'));
}

