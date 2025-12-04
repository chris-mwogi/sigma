# Sigma Workspace Consolidation & Cleanup Changelog
Date: November 10, 2025
Site: prismod.localhost

## Summary
Consolidated all Sigma app workspaces from the `sigma` module to the `sigma_home` module. Removed duplicate workspaces, assimilated ERPNext workspace definitions, normalized legacy shortcut references, and set Sigma Home as the default entry point.

## Workspaces Deleted (Duplicates)
The following workspaces were identified as duplicates and removed:
- Sigma Projects (deleted; kept "Projects")
- Sigma Quality (deleted; kept "Quality")
- Sigma Support (deleted; kept "Support")
- Sigma CRM (deleted; kept "CRM")
- Sigma Helpdesk (deleted; kept "Helpdesk")

Duplicate detection used content hash comparison. Duplicates had identical content; workspaces with "Sigma " prefix were deleted in favor of base names.

## Workspaces Consolidated (Module: Sigma → sigma_home)
- CRM
- Helpdesk
- Home
- Projects
- Quality
- Sigma Home
- Support
- Telephony

All 8 workspaces now belong to `sigma_home` module. The original `sigma` module is no longer used.

## Workspace Content Assimilated from ERPNext
- **Quality**: Copied from `apps/erpnext/quality_management/workspace/quality/quality.json`
  - Added DocType shortcuts: Quality Goal, Quality Procedure, Quality Inspection, Quality Review, Quality Action, Non Conformance
  - Added Report shortcuts: Ticket Analytics, Ticket Summary
  
- **Helpdesk**: Copied from `apps/helpdesk/helpdesk/workspace/helpdesk/helpdesk.json`
  - Added DocType shortcuts: HD Agent, HD Team, Notification Settings, Assignment Rule, Email Account, HD Ticket Type, HD Service Level Agreement, HD Settings
  - Added Report shortcuts: Ticket Analytics, Ticket Summary

## Workspace Content Normalized
Auto-fixer (`apps/sigma/sigma/scripts/auto_fix_workspaces.py`) successfully normalized shortcuts in Quality workspace:
- Quality Goal → DocType "Quality Goal"
- Quality Procedure → DocType "Quality Procedure"
- Quality Inspection → DocType "Quality Inspection"
- Quality Review → DocType "Quality Review"
- Quality Action → DocType "Quality Action"
- Non Conformance → DocType "Non Conformance"

## Remaining Issues (Smoke Check)
18 out of 19 workspaces still have validation issues, primarily:
- **Unresolved shortcuts** (e.g., "Project Billing Summary", "Learn Project Management", opaque IDs like "7u8iqfabhi")
- **Card name warnings** (card_name entries that are not Dashboard/Report objects; these are presentational and don't break UI)

Backups for all modified workspaces are available at:
- `<site>/public/files/workspace_backups/`
  - Subdirectories: `fuzzy_apply/`, `auto_fix/`, `assimilate/`, `assimilate_helpdesk/`, `assimilate_erpnext_quality/`

## Files Created/Modified
- Created: `apps/sigma/sigma/sigma_home/module.txt` (registers sigma_home module)
- Created: `apps/sigma/sigma/scripts/recreate_sigma_home.py` (recreates Sigma Home workspace)
- Created: `apps/sigma/sigma/scripts/consolidate_to_sigma_home.py` (consolidates workspaces to sigma_home)
- Modified: Workspace module assignments (8 workspaces updated to sigma_home)
- Updated: Workspace JSON files written to disk in `apps/sigma/sigma/sigma_home/workspace/`

## Sigma Home Now Default
- Sigma Home workspace is now the primary entry point for the Sigma app
- `is_hidden` = 0 (visible)
- Module: sigma_home
- 46 content blocks: Welcome header, Quick Actions, Workspace Navigation, Key Modules, Integration & Monitoring, Settings

## Next Steps (Optional)
1. Manual review of 29 unresolved mapping entries in `apps/sigma/sigma/scripts/unresolved_mappings.json`
2. Generate candidate suggestions for Projects unresolved shortcuts
3. Create migration patch to persist changes across environments
4. Test workspaces in UI to verify display and functionality
