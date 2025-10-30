#!/usr/bin/env python3
"""
Comprehensive Workspace Fix Script
Fixes all null values in workspace-related tables
"""

import frappe

def fix_all_workspace_nulls():
    """Fix all null values in all workspace-related tables."""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE WORKSPACE NULL VALUE FIX")
    print("="*80 + "\n")
    
    # Define all workspace-related doctypes and their string fields
    doctype_fields = {
        "Workspace": [
            'icon', 'indicator_color', 'title', 'content', 'module',
            'restrict_to_domain', 'parent_page', 'for_user', 'color'
        ],
        "Workspace Link": [
            'icon', 'description', 'report_ref_doctype', 'only_for',
            'link_type', 'link_to', 'dependencies', 'label'
        ],
        "Workspace Shortcut": [
            'url', 'doc_view', 'kanban_board', 'icon', 'restrict_to_domain',
            'report_ref_doctype', 'stats_filter', 'link_to', 'label'
        ],
        "Workspace Number Card": [
            'label', 'document_type', 'report_function', 'aggregate_function_based_on',
            'stats_time_interval', 'filters_json'
        ],
        "Workspace Chart": [
            'label', 'chart_name'
        ],
        "Workspace Custom Block": [
            'label', 'html'
        ]
    }
    
    total_fixed = 0
    
    for doctype, fields in doctype_fields.items():
        try:
            print(f"\nProcessing {doctype}...")
            
            # Get all records
            records = frappe.get_all(doctype, fields=["name"])
            
            if not records:
                print(f"  No records found")
                continue
            
            print(f"  Found {len(records)} records")
            
            fixed_count = 0
            for record in records:
                try:
                    doc = frappe.get_doc(doctype, record.name)
                    needs_save = False
                    
                    for field in fields:
                        if hasattr(doc, field):
                            value = getattr(doc, field)
                            if value is None:
                                setattr(doc, field, "")
                                needs_save = True
                    
                    if needs_save:
                        doc.db_update()
                        fixed_count += 1
                
                except Exception as e:
                    print(f"  Error fixing {record.name}: {str(e)}")
            
            if fixed_count > 0:
                print(f"  ✓ Fixed {fixed_count} records")
                total_fixed += fixed_count
            else:
                print(f"  No fixes needed")
        
        except Exception as e:
            print(f"  Error processing {doctype}: {str(e)}")
    
    if total_fixed > 0:
        frappe.db.commit()
        print(f"\n{'='*80}")
        print(f"TOTAL: Fixed {total_fixed} records across all workspace tables")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'='*80}")
        print(f"No fixes needed - all workspace tables are clean!")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    fix_all_workspace_nulls()

