"""Sync Risk Assessment Dashboards to the database."""
import json
import os
import frappe


def sync_risk_dashboards():
    """Synchronize Risk Assessment dashboards from JSON files to the database."""
    app_path = frappe.get_app_path('sigma')
    dashboard_dir = os.path.join(app_path, 'sigma_risk_assessment', 'dashboard')
    
    if not os.path.exists(dashboard_dir):
        print(f"Dashboard directory not found: {dashboard_dir}")
        return
    
    for dirname in os.listdir(dashboard_dir):
        dir_path = os.path.join(dashboard_dir, dirname)
        if not os.path.isdir(dir_path):
            continue
        
        json_file = os.path.join(dir_path, f'{dirname}.json')
        if not os.path.exists(json_file):
            continue
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        name = data.get('name') or data.get('dashboard_name')
        print(f'Processing: {name}')
        
        if frappe.db.exists('Dashboard', name):
            print(f'  Dashboard {name} exists, updating...')
            doc = frappe.get_doc('Dashboard', name)
        else:
            print(f'  Creating new dashboard: {name}')
            doc = frappe.new_doc('Dashboard')
            doc.name = name
        
        doc.dashboard_name = data.get('dashboard_name', name)
        doc.module = data.get('module', 'Sigma Risk Assessment')
        doc.is_standard = data.get('is_standard', 1)
        
        # Update cards
        doc.cards = []
        for card in data.get('cards', []):
            if isinstance(card, dict) and card.get('card'):
                doc.append('cards', {'card': card['card']})
        
        # Update charts
        doc.charts = []
        for chart in data.get('charts', []):
            if isinstance(chart, dict) and chart.get('chart'):
                row = {'chart': chart['chart']}
                if chart.get('width'):
                    row['width'] = chart['width']
                doc.append('charts', row)
        
        doc.save()
        print(f'  Saved: {name}')
    
    frappe.db.commit()
    print('Done syncing risk dashboards!')

