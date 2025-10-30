frappe.pages['tracking-dashboard'] = frappe.pages['tracking-dashboard'] || {};

frappe.pages['tracking-dashboard'].on_page_load = async function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Smart Asset Tracking Dashboard',
        single_column: true
    });

    // Inject the page template content
    $(frappe.render_template('tracking_dashboard')).appendTo(page.body);

    // Load data and render UI
    loadUnifiedAssets();
};

async function loadUnifiedAssets() {
    try {
        const res = await frappe.call({
            method: 'sigma.sigma_integrations.api.unified_asset_stream_api.get_unified_assets',
        });

        const assets = (res.message && res.message.assets) ? res.message.assets : [];
        const tabsEl = $('#asset-category-tabs');
        const contentEl = $('#asset-maps');
        tabsEl.empty();
        contentEl.empty();

        // Group assets by category
        const grouped = {};
        assets.forEach(a => {
            const cat = a.asset_category || 'Uncategorized';
            if (!grouped[cat]) grouped[cat] = [];
            grouped[cat].push(a);
        });

        // Build simple category buttons and panels
        let first = true;
        for (const [category, items] of Object.entries(grouped)) {
            const safeId = category.replace(/\s+/g, '-').toLowerCase();
            const icon = (items[0] && items[0].category_icon) ? items[0].category_icon : '📦';

            // Add tab button
            tabsEl.append(`
                <button class="${first ? 'active' : ''}" data-target="#${safeId}">${icon} ${category}</button>
            `);

            const list = items.map(a => `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${a.asset_name}</strong><br>
                        <small>${a.status || 'Unknown'} ${a.alarm ? ' | ' + a.alarm : ''}</small>
                    </div>
                    <span>${a.category_icon || ''}</span>
                </li>
            `).join('');

            // Add panel
            contentEl.append(`
                <div class="category-panel ${first ? '' : 'd-none'}" id="${safeId}">
                    <div class="card p-3 mt-3">
                        <h5>${icon} ${category}</h5>
                        <ul class="list-group mt-2">${list}</ul>
                    </div>
                </div>
            `);

            first = false;
        }

        // Tab switching behavior
        tabsEl.on('click', 'button', function() {
            const target = $(this).data('target');
            tabsEl.find('button').removeClass('active');
            $(this).addClass('active');
            contentEl.find('.category-panel').addClass('d-none');
            contentEl.find(target).removeClass('d-none');
        });

    } catch (err) {
        frappe.msgprint('Error loading unified assets');
        // Still log to console for developers
        // but avoid breaking the page for end users
        console.error(err);
    }
}
