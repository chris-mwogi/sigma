/**
 * Asset Tree View Override with Location Hierarchy
 *
 * This file overrides the standard ERPNext Asset tree view to add location-based hierarchy.
 * It intercepts the tree node fetching and reorganizes assets by location.
 */

frappe.provide("frappe.treeview_settings");

// Store the original Asset tree settings if they exist
const original_asset_settings = frappe.treeview_settings["Asset"] || {};

// Override Asset tree view settings
frappe.treeview_settings["Asset"] = $.extend({}, original_asset_settings, {
	// Add custom toolbar button for location view toggle
	onload: function(treeview) {
		// Call original onload if it exists
		if (original_asset_settings.onload) {
			original_asset_settings.onload(treeview);
		}

		// Add location hierarchy toggle button
		treeview.page.add_inner_button(__('Location Hierarchy'), function() {
			toggle_location_hierarchy(treeview);
		}, __('View'));

		// Add standard hierarchy button
		treeview.page.add_inner_button(__('Standard Hierarchy'), function() {
			toggle_standard_hierarchy(treeview);
		}, __('View'));

		// Initialize with location hierarchy by default
		treeview.location_hierarchy_mode = true;

		// Store reference to treeview in tree object
		if (treeview.tree) {
			treeview.tree.treeview = treeview;
		}
	},

	// Override get_tree_nodes to use location-based hierarchy
	get_tree_nodes: "sigma.sigma_asset_integrations.api.asset_management_api.get_tree_nodes_with_location",

	// Custom node rendering - OPTIMIZED for performance
	onrender: function(node) {
		// Use CSS classes instead of inline styles to avoid forced reflows
		if (node.data && node.data.is_location) {
			// Add class for CSS-based styling (no inline styles = no reflow)
			$(node.$tree_link).addClass('location-node');

			// Add location icon using data attribute (deferred rendering)
			const icon = get_location_icon(node.data.location_type);
			const $label = $(node.$tree_link).find('.tree-label');

			// Batch DOM operations to minimize reflows
			let html = `<span class="location-icon" style="margin-right: 8px;">${icon}</span>`;

			if (node.data.asset_count) {
				html += `<span class="asset-count-badge">
					<i class="fa fa-cubes"></i> ${node.data.asset_count} Assets
				</span>`;
			}

			// Single DOM operation instead of multiple
			$label.prepend(html);
		} else {
			// Use CSS class for standard asset styling
			$(node.$tree_link).addClass('standard-asset-node');
		}
	}
});



/**
 * Toggle location hierarchy mode
 */
function toggle_location_hierarchy(treeview) {
	treeview.location_hierarchy_mode = true;
	frappe.show_alert({
		message: __('Switched to Location Hierarchy View'),
		indicator: 'green'
	});
	treeview.make_tree();
}

/**
 * Toggle standard hierarchy mode
 */
function toggle_standard_hierarchy(treeview) {
	treeview.location_hierarchy_mode = false;
	frappe.show_alert({
		message: __('Switched to Standard Hierarchy View'),
		indicator: 'blue'
	});
	treeview.make_tree();
}

/**
 * Get location icon based on type
 */
function get_location_icon(location_type) {
	const icon_map = {
		'Office': '<i class="fa fa-building" style="color: white;"></i>',
		'Warehouse': '<i class="fa fa-warehouse" style="color: white;"></i>',
		'Factory': '<i class="fa fa-industry" style="color: white;"></i>',
		'Store': '<i class="fa fa-store" style="color: white;"></i>',
		'Site': '<i class="fa fa-map-marked-alt" style="color: white;"></i>',
		'Branch': '<i class="fa fa-code-branch" style="color: white;"></i>',
		'Substation': '<i class="fa fa-bolt" style="color: white;"></i>',
		'default': '<i class="fa fa-map-pin" style="color: white;"></i>'
	};
	
	return icon_map[location_type] || icon_map['default'];
}

// Add custom CSS for location nodes - OPTIMIZED
// Use document.head.appendChild instead of jQuery for better performance
frappe.ready(function() {
	// Check if styles already exist to avoid duplicate injection
	if (document.getElementById('sigma-asset-tree-styles')) {
		return;
	}

	const style = document.createElement('style');
	style.id = 'sigma-asset-tree-styles';
	style.textContent = `
		.location-node {
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
			color: white !important;
			font-weight: 700 !important;
			padding: 10px 15px !important;
			border-radius: 8px !important;
			margin-bottom: 10px !important;
			box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
			transition: all 0.3s ease !important;
		}

		.location-node:hover {
			transform: translateY(-2px) !important;
			box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
		}

		.standard-asset-node {
			background: white !important;
			border-left: 4px solid #667eea !important;
			padding: 8px 12px !important;
			margin-bottom: 5px !important;
		}

		.location-icon {
			margin-right: 8px;
		}

		.asset-count-badge {
			margin-left: 10px;
			background: rgba(255, 255, 255, 0.3);
			padding: 2px 6px;
			border-radius: 3px;
			font-size: 0.85em;
		}

		.tree-node-toolbar {
			background: transparent !important;
		}
	`;

	document.head.appendChild(style);
});

