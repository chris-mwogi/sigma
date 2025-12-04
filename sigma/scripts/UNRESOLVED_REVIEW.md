# Unresolved Workspace Mappings - Review & Approval

## Summary
29 unresolved shortcut/link entries remain across 10 workspaces after auto-fixing and fuzzy matching.

### Categories:

**Descriptive Names (10 items)** — Can likely be mapped by name:
1. Settings → "Monitoring Settings" (DocType? Report? Page?)
2. Asset Management → "Asset Tree Viewer" (Page asset-tree-viewer — **RESOLVED** via fuzzy)
3. Asset Management → "Asset List" (DocType Asset?)
4. Asset Management → "Active Alerts" (Custom Page?)
5. Asset Management → "Recent Telemetry" (Custom Page?)
6. Asset Management → "Monitoring Settings" (DocType?)
7. Projects → "Project Billing Summary" (Report?)
8. Acquisition (Buying) → "RFQ" (DocType Request for Quotation?)
9. Case Management → "Case List" (Custom Page?)
10. Guard Monitoring → "Patrol Verifications" (Custom Page?)

**Opaque IDs (19 items)** — Legacy encoded IDs, need context:
- Projects: 7ubp9090u4, 7ubiaat731, 7ubirknjpd
- Quality: 7uarp1ge0k, 7uajovag60, 7uai5fuudb
- Support: 7ua4a3gf07, 7ua2qtrrnc, 7ua77hv8lc
- CRM: 7u928qkm3j, 7u9vgslpu9, 7u9h9l70ms, 7u9haubfl5
- Helpdesk: 7u8dc4c39n, 7u8hv62ncb, 7u929jak0g, 7u9pha0q2n
- Telephony: 7u8iqfabhi, 7u8im4rplh, 7u8prb0svm

---

## Recommended Approach

**Option A: Auto-remove unresolved items**
- Delete all 29 unresolved shortcut blocks from workspaces
- Workspaces will display cleaner; users won't see broken/blank shortcuts
- Recommended for: Quick cleanup, MVP, focus on working content

**Option B: Manual mapping review**
- You provide exact mappings (DocType/Report/Dashboard/Page + name)
- I'll apply them to workspaces and persist as patch
- Recommended for: Production, full feature parity

**Option C: Create placeholder DocTypes/Pages**
- I create minimal placeholder DocTypes/Pages for each unresolved name
- Wire shortcuts to placeholders
- Workspaces will be complete; placeholders can be filled in later
- Recommended for: Preserve workspace layout, future enhancement

**Option D: Leave as-is**
- Keep current state; unresolved items remain in DB backups
- Workspaces function; users see card/shortcut warnings in smoke-check
- Recommended for: Gradual migration, manual fixes per-team

---

## My Recommendation
**Option A + B (Hybrid):**
1. **Auto-remove the 19 opaque IDs** (7u... items) — they're undecodable without context
2. **Map the 10 descriptive names manually** (you tell me the targets, I'll apply them)

This gives you:
- Clean, working workspaces (no broken opaque shortcuts)
- Preserved descriptive shortcuts (mapped to actual targets)
- Quick implementation (no new DocTypes needed)

**What I need from you:**
For each of the 10 descriptive items, tell me the DocType, Report, Dashboard, or Page name:
- Asset Tree Viewer → ?
- Asset List → ?
- Active Alerts → ?
- Recent Telemetry → ?
- Monitoring Settings → ?
- Project Billing Summary → ?
- RFQ → ?
- Case List → ?
- Patrol Verifications → ?

Or just say "**Option A: Remove all 29**" or "**Option B: Full manual review**" and I'll proceed accordingly.
