frappe.pages['asset-tree-viewer'] = frappe.pages['asset-tree-viewer'] || {};

frappe.pages['asset-tree-viewer'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Asset Tree Viewer',
        single_column: true
    });

    // Inject the page template content
    $(frappe.render_template('asset_tree_viewer')).appendTo(page.body);

    // Initialize the page
    initializeAssetTreeViewer(page);
};

function initializeAssetTreeViewer(page) {
    let selectedAsset = null;
    let currentTreeData = null;
    let selectedAssets = new Set();

    // Setup asset selector with autocomplete
    const assetInput = $('#asset-selector');

    frappe.ui.form.make_control({
        parent: assetInput.parent(),
        df: {
            fieldtype: 'Link',
            options: 'Asset',
            fieldname: 'asset',
            label: 'Asset',
            onchange: function() {
                selectedAsset = this.get_value();
            }
        },
        render_input: true
    });

    // Remove the original input and use the Frappe control
    assetInput.remove();

    // Load tree button handler
    $('#load-tree-btn').on('click', async function() {
        // If no asset selected, load all locations
        await loadLocationBasedTree(selectedAsset);
    });

    // Search functionality
    $('#asset-search').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        filterTreeNodes(searchTerm);
    });

    $('#clear-search-btn').on('click', function() {
        $('#asset-search').val('');
        filterTreeNodes('');
    });

    // Toggle filters
    $('#toggle-filters-btn').on('click', function() {
        $('#advanced-filters').slideToggle();
    });

    // Apply filters
    $('#apply-filters-btn').on('click', function() {
        applyAdvancedFilters();
    });

    // Clear filters
    $('#clear-filters-btn').on('click', function() {
        $('#filter-category').val('');
        $('#filter-status').val('');
        $('#filter-date-from').val('');
        $('#filter-date-to').val('');
        applyAdvancedFilters();
    });

    // Export button
    $('#export-btn').on('click', function() {
        showExportDialog();
    });

    // Bulk actions
    $('#bulk-actions-btn').on('click', function() {
        toggleBulkSelection();
    });

    $('#select-all-assets').on('change', function() {
        const isChecked = $(this).is(':checked');
        $('.asset-checkbox').prop('checked', isChecked);
        updateSelectedAssets();
    });

    $('#cancel-selection-btn').on('click', function() {
        cancelBulkSelection();
    });

    $('#bulk-export-btn').on('click', function() {
        exportSelectedAssets();
    });

    // Helper functions
    function filterTreeNodes(searchTerm) {
        if (!searchTerm) {
            $('.tree-node').show();
            return;
        }

        $('.tree-node').each(function() {
            const $node = $(this);
            const assetName = $node.find('.tree-node-title').text().toLowerCase();
            const assetId = $node.data('asset-id') ? $node.data('asset-id').toLowerCase() : '';
            const category = $node.find('.tree-node-subtitle').text().toLowerCase();

            if (assetName.includes(searchTerm) || assetId.includes(searchTerm) || category.includes(searchTerm)) {
                $node.show();
                // Show all parents
                $node.parents('.tree-node').show();
            } else {
                $node.hide();
            }
        });
    }

    function applyAdvancedFilters() {
        const categories = $('#filter-category').val() || [];
        const statuses = $('#filter-status').val() || [];
        const dateFrom = $('#filter-date-from').val();
        const dateTo = $('#filter-date-to').val();

        $('.tree-node').each(function() {
            const $node = $(this);
            let show = true;

            // Category filter
            if (categories.length > 0) {
                const nodeCategory = $node.find('.tree-node-subtitle').text().split('•')[0].trim();
                if (!categories.some(cat => nodeCategory.includes(cat))) {
                    show = false;
                }
            }

            // Status filter
            if (statuses.length > 0) {
                const nodeStatus = $node.find('.asset-status-badge').text().trim();
                if (!statuses.includes(nodeStatus)) {
                    show = false;
                }
            }

            if (show) {
                $node.show();
                $node.parents('.tree-node').show();
            } else {
                $node.hide();
            }
        });
    }

    function toggleBulkSelection() {
        if ($('#bulk-actions-bar').is(':visible')) {
            cancelBulkSelection();
        } else {
            // Add checkboxes to tree nodes
            $('.tree-node-header').each(function() {
                if (!$(this).find('.asset-checkbox').length) {
                    const assetId = $(this).closest('.tree-node').data('asset-id');
                    $(this).prepend(`<input type="checkbox" class="asset-checkbox mr-2" data-asset-id="${assetId}">`);
                }
            });
            $('#bulk-actions-bar').slideDown();

            // Bind checkbox change events
            $('.asset-checkbox').on('change', function() {
                updateSelectedAssets();
            });
        }
    }

    function cancelBulkSelection() {
        $('.asset-checkbox').remove();
        $('#bulk-actions-bar').slideUp();
        selectedAssets.clear();
        $('#selected-count').text('0');
    }

    function updateSelectedAssets() {
        selectedAssets.clear();
        $('.asset-checkbox:checked').each(function() {
            selectedAssets.add($(this).data('asset-id'));
        });
        $('#selected-count').text(selectedAssets.size);
    }

    function showExportDialog() {
        const dialog = new frappe.ui.Dialog({
            title: 'Export Asset Tree',
            fields: [
                {
                    fieldtype: 'Select',
                    label: 'Export Format',
                    fieldname: 'format',
                    options: ['JSON', 'CSV', 'Excel'],
                    default: 'JSON'
                },
                {
                    fieldtype: 'Check',
                    label: 'Include Child Assets',
                    fieldname: 'include_children',
                    default: 1
                }
            ],
            primary_action_label: 'Export',
            primary_action: function(values) {
                exportTree(values.format, values.include_children);
                dialog.hide();
            }
        });
        dialog.show();
    }

    function exportTree(format, includeChildren) {
        if (!currentTreeData) {
            frappe.msgprint('No tree data to export');
            return;
        }

        if (format === 'JSON') {
            exportAsJSON(currentTreeData);
        } else if (format === 'CSV' || format === 'Excel') {
            exportAsCSV(currentTreeData, includeChildren);
        }
    }

    function exportAsJSON(data) {
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `asset_tree_${data.location.name}_${frappe.datetime.now_date()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        frappe.show_alert({message: 'Exported as JSON', indicator: 'green'});
    }

    function exportAsCSV(data, includeChildren) {
        const rows = [];
        rows.push(['Type', 'ID', 'Name', 'Category', 'Status', 'Location', 'Parent System', 'Level']);

        function addNodeRows(nodes, level = 0, locationName = '') {
            nodes.forEach(node => {
                if (node.type === 'location') {
                    // Add location row
                    rows.push([
                        'Location',
                        node.id,
                        node.name,
                        node.location_type || '',
                        '',
                        '',
                        '',
                        level
                    ]);
                    // Process assets under this location
                    if (includeChildren && node.children && node.children.length > 0) {
                        addNodeRows(node.children, level + 1, node.name);
                    }
                } else {
                    // Add asset row
                    rows.push([
                        'Asset',
                        node.id,
                        node.name,
                        node.category || '',
                        node.status || '',
                        locationName || node.location || '',
                        node.parent_system || '',
                        level
                    ]);
                    if (includeChildren && node.children && node.children.length > 0) {
                        addNodeRows(node.children, level + 1, locationName);
                    }
                }
            });
        }

        addNodeRows(data.tree);

        const csvContent = rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const filename = data.location ? `asset_tree_${data.location.name}_${frappe.datetime.now_date()}.csv` : `asset_tree_all_locations_${frappe.datetime.now_date()}.csv`;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
        frappe.show_alert({message: 'Exported as CSV', indicator: 'green'});
    }

    function exportSelectedAssets() {
        if (selectedAssets.size === 0) {
            frappe.msgprint('No assets selected');
            return;
        }

        const selectedData = [];
        selectedAssets.forEach(assetId => {
            const $node = $(`.tree-node[data-asset-id="${assetId}"]`);
            if ($node.length) {
                selectedData.push({
                    id: assetId,
                    name: $node.find('.tree-node-title').text().trim(),
                    category: $node.find('.tree-node-subtitle').text().split('•')[0].trim(),
                    status: $node.find('.asset-status-badge').text().trim()
                });
            }
        });

        const jsonStr = JSON.stringify(selectedData, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `selected_assets_${frappe.datetime.now_date()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        frappe.show_alert({message: `Exported ${selectedAssets.size} asset(s)`, indicator: 'green'});
    }

    // Store reference for export
    window.currentTreeData = currentTreeData;
}

async function loadLocationBasedTree(assetId) {
    try {
        frappe.show_progress('Loading Tree...', 50, 100);

        const response = await frappe.call({
            method: 'sigma.sigma_asset_integrations.api.asset_management_api.get_location_based_asset_tree',
            args: {
                asset_id: assetId || null
            }
        });

        frappe.hide_progress();

        if (response.message && response.message.status === 'success') {
            displayTree(response.message);
        } else {
            frappe.msgprint('Failed to load asset tree');
        }
    } catch (error) {
        frappe.hide_progress();
        console.error('Error loading tree:', error);
        frappe.msgprint({
            title: 'Error',
            message: error.message || 'Failed to load asset tree',
            indicator: 'red'
        });
    }
}

function displayTree(data) {
    const treeNodes = data.tree;
    const viewMode = data.view_mode || 'location_hierarchy';

    // Store tree data for export
    window.currentTreeData = data;

    // Display summary information
    $('#location-info-card').show();
    $('#location-details').html(`
        <div class="location-root">
            <div class="location-root-title">
                <i class="fa fa-building"></i> Location-Based Asset Tree
            </div>
            <div class="location-root-subtitle">
                Hierarchical view organized by location
            </div>
            <div class="mt-2">
                <span class="badge badge-primary">${data.location_count || 0} Location(s)</span>
                <span class="badge badge-info ml-2">${data.total_asset_count || 0} Total Asset(s)</span>
            </div>
        </div>
    `);

    // Display tree
    const treeContainer = $('#tree-container');
    treeContainer.empty();

    if (treeNodes.length === 0) {
        treeContainer.html('<p class="text-muted">No assets found at this location</p>');
        return;
    }

    const treeHtml = treeNodes.map(node => renderTreeNode(node, 0)).join('');
    treeContainer.html(treeHtml);

    // Add click handlers for collapsible nodes
    treeContainer.on('click', '.tree-node-header', function(e) {
        // Don't collapse if clicking on checkbox or button
        if ($(e.target).hasClass('asset-checkbox') || $(e.target).closest('.view-details-btn').length) {
            return;
        }
        e.stopPropagation();
        $(this).closest('.tree-node').toggleClass('collapsed');
    });

    // Add click handler for view details button
    treeContainer.on('click', '.view-details-btn', function(e) {
        e.stopPropagation();
        const assetId = $(this).data('asset-id');
        const integrationData = $(this).closest('.tree-node').data('integrationData');
        showAssetDetailsDialog(assetId, integrationData);
    });

    // Show tree controls and search bar
    $('#tree-controls').show();
    $('#search-filter-bar').show();

    // Populate category filter
    populateCategoryFilter(data.tree);

    // Expand all button
    $('#expand-all-btn').off('click').on('click', function() {
        $('.tree-node').removeClass('collapsed');
    });

    // Collapse all button
    $('#collapse-all-btn').off('click').on('click', function() {
        $('.tree-node').addClass('collapsed');
    });
}

function populateCategoryFilter(treeNodes) {
    const categories = new Set();

    function extractCategories(nodes) {
        nodes.forEach(node => {
            if (node.category) {
                categories.add(node.category);
            }
            if (node.children && node.children.length > 0) {
                extractCategories(node.children);
            }
        });
    }

    extractCategories(treeNodes);

    const $categoryFilter = $('#filter-category');
    $categoryFilter.find('option:not(:first)').remove();

    Array.from(categories).sort().forEach(category => {
        $categoryFilter.append(`<option value="${category}">${category}</option>`);
    });
}

function renderTreeNode(node, level) {
    const hasChildren = node.children && node.children.length > 0;
    const isLocation = node.type === 'location';

    // Render location node differently
    if (isLocation) {
        return renderLocationNode(node, level);
    }

    // Render asset node
    const icon = getAssetIcon(node.category);
    const statusBadge = getStatusBadge(node.status);
    const expandIcon = hasChildren ? '<i class="fa fa-chevron-down tree-expand-icon"></i>' : '';

    let html = `
        <div class="tree-node asset-node ${level === 0 ? 'root-asset' : ''} level-${level}" data-asset-id="${node.id}" data-level="${level}">
            <div class="tree-node-header ${hasChildren ? 'has-children' : ''}">
                ${expandIcon}
                <span class="tree-node-icon">${icon}</span>
                <div class="tree-node-content">
                    <div class="tree-node-title">
                        ${node.name}
                        <span class="tree-node-id">(${node.id})</span>
                    </div>
                    <div class="tree-node-subtitle">
                        <i class="fa fa-tag"></i> ${node.category || 'No Category'}
                        ${node.installation_point ? '<i class="fa fa-map-pin ml-2"></i> ' + node.installation_point : ''}
                    </div>
                    <div class="tree-node-integration-badges" id="integration-badges-${node.id}">
                        <!-- Integration badges will be loaded here -->
                    </div>
                </div>
                <div class="tree-node-badges">
                    ${statusBadge}
                    ${hasChildren ? `<span class="badge badge-light tree-child-count"><i class="fa fa-sitemap"></i> ${node.child_count}</span>` : ''}
                    <button class="btn btn-xs btn-info ml-2 view-details-btn" data-asset-id="${node.id}" title="View Details">
                        <i class="fa fa-info-circle"></i>
                    </button>
                </div>
            </div>
    `;

    if (hasChildren) {
        html += '<div class="tree-node-children">';
        node.children.forEach(child => {
            html += renderTreeNode(child, level + 1);
        });
        html += '</div>';
    }

    html += '</div>';

    // Load integration data asynchronously for assets only
    setTimeout(() => loadIntegrationBadges(node.id), 100);

    return html;
}

function renderLocationNode(node, level) {
    const hasChildren = node.children && node.children.length > 0;
    const expandIcon = hasChildren ? '<i class="fa fa-chevron-down tree-expand-icon"></i>' : '';
    const locationIcon = getLocationIcon(node.location_type);

    let html = `
        <div class="tree-node location-node level-${level}" data-location-id="${node.id}" data-level="${level}">
            <div class="tree-node-header location-header ${hasChildren ? 'has-children' : ''}">
                ${expandIcon}
                <span class="tree-node-icon location-icon">${locationIcon}</span>
                <div class="tree-node-content">
                    <div class="tree-node-title location-title">
                        ${node.name}
                        <span class="tree-node-id">(${node.id})</span>
                    </div>
                    <div class="tree-node-subtitle">
                        <i class="fa fa-map-marker-alt"></i> ${node.location_type || 'Location'}
                        ${node.parent_location ? '<i class="fa fa-level-up-alt ml-2"></i> Parent: ' + node.parent_location : ''}
                    </div>
                </div>
                <div class="tree-node-badges">
                    <span class="badge badge-primary location-badge">
                        <i class="fa fa-building"></i> Location
                    </span>
                    ${hasChildren ? `<span class="badge badge-info ml-2"><i class="fa fa-cubes"></i> ${node.asset_count} Asset(s)</span>` : ''}
                </div>
            </div>
    `;

    if (hasChildren) {
        html += '<div class="tree-node-children">';
        node.children.forEach(child => {
            html += renderTreeNode(child, level + 1);
        });
        html += '</div>';
    }

    html += '</div>';
    return html;
}

function getLocationIcon(locationType) {
    const iconMap = {
        'Office': '<i class="fa fa-building" style="color: #2196F3;"></i>',
        'Warehouse': '<i class="fa fa-warehouse" style="color: #FF9800;"></i>',
        'Factory': '<i class="fa fa-industry" style="color: #9C27B0;"></i>',
        'Store': '<i class="fa fa-store" style="color: #4CAF50;"></i>',
        'Site': '<i class="fa fa-map-marked-alt" style="color: #F44336;"></i>',
        'Branch': '<i class="fa fa-code-branch" style="color: #00BCD4;"></i>',
        'Substation': '<i class="fa fa-bolt" style="color: #FFC107;"></i>',
        'default': '<i class="fa fa-map-pin" style="color: #607D8B;"></i>'
    };

    return iconMap[locationType] || iconMap['default'];
}

async function loadIntegrationBadges(assetId) {
    try {
        // Load all integration data in parallel
        const [maintenanceData, iotData, caseData] = await Promise.all([
            frappe.call({
                method: 'sigma.sigma_asset_integrations.api.asset_management_api.get_asset_maintenance_info',
                args: { asset_id: assetId }
            }),
            frappe.call({
                method: 'sigma.sigma_asset_integrations.api.asset_management_api.get_asset_iot_info',
                args: { asset_id: assetId }
            }),
            frappe.call({
                method: 'sigma.sigma_asset_integrations.api.asset_management_api.get_asset_case_info',
                args: { asset_id: assetId }
            })
        ]);

        const badges = [];

        // Maintenance badge
        if (maintenanceData.message.has_maintenance && maintenanceData.message.upcoming_count > 0) {
            badges.push(`
                <span class="badge badge-warning integration-badge" title="Upcoming Maintenance">
                    <i class="fa fa-wrench"></i> ${maintenanceData.message.upcoming_count}
                </span>
            `);
        }

        // IoT badge
        if (iotData.message.is_iot_device) {
            const statusColor = iotData.message.status === 'Online' ? 'success' :
                               iotData.message.status === 'Active' ? 'info' : 'secondary';
            badges.push(`
                <span class="badge badge-${statusColor} integration-badge" title="IoT Device: ${iotData.message.status}">
                    <i class="fa fa-wifi"></i> ${iotData.message.status}
                </span>
            `);

            if (iotData.message.unprocessed_count > 0) {
                badges.push(`
                    <span class="badge badge-danger integration-badge" title="Unprocessed Alerts">
                        <i class="fa fa-exclamation-triangle"></i> ${iotData.message.unprocessed_count}
                    </span>
                `);
            }
        }

        // Case badge
        if (caseData.message.has_cases && caseData.message.open_count > 0) {
            badges.push(`
                <span class="badge badge-danger integration-badge" title="Open Cases">
                    <i class="fa fa-ticket-alt"></i> ${caseData.message.open_count}
                </span>
            `);
        }

        // Update the badges container
        const badgesContainer = $(`#integration-badges-${assetId}`);
        if (badgesContainer.length && badges.length > 0) {
            badgesContainer.html(badges.join(' '));
        }

        // Store integration data for details view
        $(`[data-asset-id="${assetId}"]`).data('integrationData', {
            maintenance: maintenanceData.message,
            iot: iotData.message,
            cases: caseData.message
        });

    } catch (error) {
        console.error(`Failed to load integration badges for ${assetId}:`, error);
    }
}

function getAssetIcon(category) {
    // Enhanced icon mapping with Font Awesome icons and colors
    const icons = {
        'HVAC System': '<i class="fa fa-wind" style="color: #00bcd4;"></i>',
        'Electrical System': '<i class="fa fa-bolt" style="color: #ffc107;"></i>',
        'Security System': '<i class="fa fa-shield-alt" style="color: #f44336;"></i>',
        'Fire Safety System': '<i class="fa fa-fire-extinguisher" style="color: #ff5722;"></i>',
        'Access Control System': '<i class="fa fa-key" style="color: #9c27b0;"></i>',
        'CCTV': '<i class="fa fa-video" style="color: #607d8b;"></i>',
        'Network Equipment': '<i class="fa fa-network-wired" style="color: #3f51b5;"></i>',
        'Surveillance Camera': '<i class="fa fa-camera" style="color: #607d8b;"></i>',
        'Server': '<i class="fa fa-server" style="color: #009688;"></i>',
        'Switch': '<i class="fa fa-exchange-alt" style="color: #4caf50;"></i>',
        'Router': '<i class="fa fa-wifi" style="color: #2196f3;"></i>',
        'Access Point': '<i class="fa fa-broadcast-tower" style="color: #03a9f4;"></i>',
        'Sensor': '<i class="fa fa-sensor" style="color: #8bc34a;"></i>',
        'Vehicle': '<i class="fa fa-car" style="color: #795548;"></i>',
        'Generator': '<i class="fa fa-plug" style="color: #ff9800;"></i>'
    };
    return icons[category] || '<i class="fa fa-cube" style="color: #9e9e9e;"></i>';
}

function getStatusBadge(status) {
    // Enhanced status badges with icons and custom colors
    const statusConfig = {
        'In Use': { class: 'success', icon: 'fa-check-circle', color: '#4caf50' },
        'Available': { class: 'info', icon: 'fa-circle', color: '#2196f3' },
        'Under Maintenance': { class: 'warning', icon: 'fa-wrench', color: '#ff9800' },
        'Disposed': { class: 'danger', icon: 'fa-trash', color: '#f44336' },
        'Decommissioned': { class: 'dark', icon: 'fa-ban', color: '#607d8b' },
        'Draft': { class: 'secondary', icon: 'fa-file', color: '#9e9e9e' }
    };

    const config = statusConfig[status] || { class: 'secondary', icon: 'fa-question-circle', color: '#9e9e9e' };
    return `<span class="badge badge-${config.class} asset-status-badge" style="background-color: ${config.color};">
                <i class="fa ${config.icon}"></i> ${status || 'Unknown'}
            </span>`;
}

function showAssetDetailsDialog(assetId, integrationData) {
    if (!integrationData) {
        frappe.msgprint('Integration data not loaded yet. Please wait a moment and try again.');
        return;
    }

    const { maintenance, iot, cases } = integrationData;

    // Build dialog content
    let content = `<div class="asset-details-dialog">`;

    // Maintenance Section
    content += `
        <div class="integration-section">
            <h5><i class="fa fa-wrench text-warning"></i> Maintenance Information</h5>
            ${maintenance.has_maintenance ? `
                <div class="mb-3">
                    <strong>Upcoming Maintenance (${maintenance.upcoming_count}):</strong>
                    ${maintenance.upcoming_tasks.length > 0 ? `
                        <ul class="list-unstyled mt-2">
                            ${maintenance.upcoming_tasks.map(task => `
                                <li class="mb-2">
                                    <span class="badge badge-warning">${task.next_due_date}</span>
                                    <strong>${task.task_name}</strong> - ${task.task_type}
                                    <br><small class="text-muted">Periodicity: ${task.periodicity}</small>
                                </li>
                            `).join('')}
                        </ul>
                    ` : '<p class="text-muted">No upcoming maintenance</p>'}

                    <strong>Recent History (${maintenance.history_count}):</strong>
                    ${maintenance.history.length > 0 ? `
                        <ul class="list-unstyled mt-2">
                            ${maintenance.history.slice(0, 5).map(log => `
                                <li class="mb-2">
                                    <span class="badge badge-secondary">${log.completion_date || log.due_date}</span>
                                    ${log.task} - <span class="badge badge-${log.status === 'Completed' ? 'success' : 'warning'}">${log.status}</span>
                                    ${log.actions ? `<br><small>${log.actions}</small>` : ''}
                                </li>
                            `).join('')}
                        </ul>
                    ` : '<p class="text-muted">No maintenance history</p>'}

                    <button class="btn btn-sm btn-primary mt-2" onclick="scheduleMaintenanceForAsset('${assetId}')">
                        <i class="fa fa-calendar-plus"></i> Schedule Maintenance
                    </button>
                </div>
            ` : '<p class="text-muted">No maintenance schedule configured</p>'}
        </div>
    `;

    // IoT Section
    content += `
        <div class="integration-section">
            <h5><i class="fa fa-wifi text-info"></i> IoT Device Information</h5>
            ${iot.is_iot_device ? `
                <div class="mb-3">
                    <p><strong>Device ID:</strong> ${iot.device_id}</p>
                    <p><strong>Status:</strong> <span class="badge badge-${iot.status === 'Online' ? 'success' : iot.status === 'Active' ? 'info' : 'secondary'}">${iot.status}</span></p>

                    <strong>Recent Alerts (${iot.alert_count}):</strong>
                    ${iot.alerts.length > 0 ? `
                        <ul class="list-unstyled mt-2">
                            ${iot.alerts.slice(0, 5).map(alert => `
                                <li class="mb-2">
                                    <span class="badge badge-${alert.severity === 'High' ? 'danger' : alert.severity === 'Medium' ? 'warning' : 'info'}">
                                        ${alert.severity}
                                    </span>
                                    <strong>${alert.alert_type}</strong>
                                    <br><small class="text-muted">${alert.timestamp}</small>
                                    ${alert.sensor_value ? `<br><small>Value: ${alert.sensor_value}</small>` : ''}
                                    ${!alert.processed ? '<span class="badge badge-danger ml-2">Unprocessed</span>' : ''}
                                </li>
                            `).join('')}
                        </ul>
                    ` : '<p class="text-muted">No recent alerts</p>'}

                    ${iot.unprocessed_count > 0 ? `
                        <button class="btn btn-sm btn-warning mt-2" onclick="viewUnprocessedAlerts('${assetId}')">
                            <i class="fa fa-exclamation-triangle"></i> View ${iot.unprocessed_count} Unprocessed Alert(s)
                        </button>
                    ` : ''}
                </div>
            ` : '<p class="text-muted">This asset is not an IoT device</p>'}
        </div>
    `;

    // Cases Section
    content += `
        <div class="integration-section">
            <h5><i class="fa fa-ticket-alt text-danger"></i> Cases & Issues</h5>
            ${cases.has_cases ? `
                <div class="mb-3">
                    <strong>Open Cases (${cases.open_count}):</strong>
                    ${cases.open_cases.length > 0 ? `
                        <ul class="list-unstyled mt-2">
                            ${cases.open_cases.map(c => `
                                <li class="mb-2">
                                    <a href="/app/${c.type.toLowerCase()}/${c.id}" target="_blank">
                                        <strong>${c.id}</strong>
                                    </a>
                                    - ${c.subject}
                                    <br><span class="badge badge-${c.status === 'Open' ? 'danger' : 'warning'}">${c.status}</span>
                                    ${c.priority ? `<span class="badge badge-secondary ml-1">${c.priority}</span>` : ''}
                                    <small class="text-muted ml-2">${c.created}</small>
                                </li>
                            `).join('')}
                        </ul>
                    ` : '<p class="text-muted">No open cases</p>'}

                    ${cases.closed_count > 0 ? `
                        <strong>Recently Closed (${cases.closed_count}):</strong>
                        <ul class="list-unstyled mt-2">
                            ${cases.closed_cases.slice(0, 3).map(c => `
                                <li class="mb-2">
                                    <a href="/app/${c.type.toLowerCase()}/${c.id}" target="_blank">
                                        <strong>${c.id}</strong>
                                    </a>
                                    - ${c.subject}
                                    <br><span class="badge badge-success">${c.status}</span>
                                    <small class="text-muted ml-2">${c.resolution_date || c.created}</small>
                                </li>
                            `).join('')}
                        </ul>
                    ` : ''}

                    <button class="btn btn-sm btn-primary mt-2" onclick="createCaseForAsset('${assetId}')">
                        <i class="fa fa-plus"></i> Create New Case
                    </button>
                </div>
            ` : `
                <p class="text-muted">No cases or issues found</p>
                <button class="btn btn-sm btn-primary mt-2" onclick="createCaseForAsset('${assetId}')">
                    <i class="fa fa-plus"></i> Create New Case
                </button>
            `}
        </div>
    `;

    content += `</div>`;

    // Show dialog
    const dialog = new frappe.ui.Dialog({
        title: `Asset Details: ${assetId}`,
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'details_html',
                options: content
            }
        ],
        size: 'large'
    });

    dialog.show();
}

// Helper functions for actions
window.scheduleMaintenanceForAsset = function(assetId) {
    frappe.new_doc('Asset Maintenance', {
        asset_name: assetId
    });
};

window.createCaseForAsset = function(assetId) {
    frappe.new_doc('Case', {
        subject: `Issue with Asset ${assetId}`
    });
};

window.viewUnprocessedAlerts = function(assetId) {
    frappe.set_route('List', 'Asset Event Log', {
        asset: assetId,
        processed: 0
    });
};

