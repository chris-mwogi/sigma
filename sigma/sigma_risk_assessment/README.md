Sigma Risk Assessment Module

Install:
1. Place this folder under apps/sigma/sigma/ (so path ends with sigma_risk_assessment)
2. Run: `bench --site <site> install-app sigma && bench --site <site> migrate`

Notes:
- Doctype JSON files are included under `doctype/`.
- Adjust Role permissions and Workflow as needed for your instance.
- Sample client dashboard JS is minimal; replace with charts (frappe charts) as needed.
