# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

app_name = "sigma"
app_title = "Sigma Personnel"
app_publisher = "Prismod Technologies Limited"
app_description = "Personnel Tracking Module (PTM) for KPLC - ISO 27001, ISO 45001, ISO 31000, ISO 22301 compliant"
app_icon = "icon-user-check"
app_color = "#FF5722"
app_email = "support@prismod.co.ke"
app_license = "MIT"
app_version = "1.0.0"

# Scheduled Tasks
# ---------------
scheduler_events = {
    "all": [
        "sigma.sigma_personnel.automation.scheduled_jobs.check_lone_workers_every_5_minutes"
    ],
    "hourly": [
        "sigma.sigma_personnel.automation.scheduled_jobs.check_overdue_checkouts",
        "sigma.sigma_personnel.automation.scheduled_jobs.check_zone_max_duration"
    ],
    "daily": [
        "sigma.sigma_personnel.automation.scheduled_jobs.daily_personnel_cleanup",
        "sigma.sigma_personnel.automation.scheduled_jobs.generate_daily_attendance_summary"
    ]
}

# Document Events
# ---------------
doc_events = {
    "Human Profile": {
        "before_save": "sigma.sigma_personnel.automation.personnel_hooks.calculate_risk_score",
        "on_submit": "sigma.sigma_personnel.automation.personnel_hooks.activate_tracking_devices"
    },
    "Personnel Check-In": {
        "on_submit": "sigma.sigma_personnel.automation.personnel_hooks.create_initial_zone_presence"
    },
    "Personnel Check-Out": {
        "on_submit": "sigma.sigma_personnel.automation.personnel_hooks.close_zone_presence"
    },
    "Human Location Event": {
        "after_insert": "sigma.sigma_personnel.automation.personnel_hooks.update_zone_presence"
    }
}

