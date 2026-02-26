# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, get_datetime, nowtime, today
from datetime import datetime, time


class AccessSchedule(Document):
    def validate(self):
        self.validate_time_slots()
        self.validate_effective_dates()
    
    def validate_time_slots(self):
        """Validate time slot entries"""
        for slot in self.time_slots:
            if slot.start_time and slot.end_time:
                start = datetime.strptime(str(slot.start_time), "%H:%M:%S").time()
                end = datetime.strptime(str(slot.end_time), "%H:%M:%S").time()
                if start >= end:
                    frappe.throw(f"Start time must be before end time for {slot.day_of_week}")
    
    def validate_effective_dates(self):
        """Validate effective date range"""
        if self.effective_from and self.effective_to:
            if getdate(self.effective_from) > getdate(self.effective_to):
                frappe.throw("Effective From date must be before Effective To date")
    
    def is_access_allowed(self, check_datetime=None):
        """Check if access is allowed at the given datetime"""
        if not check_datetime:
            check_datetime = get_datetime()
        
        check_date = check_datetime.date()
        check_time = check_datetime.time()
        check_day = check_datetime.strftime("%A")  # Monday, Tuesday, etc.
        
        # Check validity period
        if self.effective_from and check_date < getdate(self.effective_from):
            return False
        if self.effective_to and check_date > getdate(self.effective_to):
            return False
        
        # Check holidays first
        for holiday in self.holidays:
            if getdate(holiday.holiday_date) == check_date:
                if holiday.override_schedule:
                    return holiday.access_allowed
        
        # Check time slots
        for slot in self.time_slots:
            if self._day_matches(slot.day_of_week, check_day):
                start = datetime.strptime(str(slot.start_time), "%H:%M:%S").time()
                end = datetime.strptime(str(slot.end_time), "%H:%M:%S").time()
                if start <= check_time <= end:
                    return slot.access_allowed
        
        return False  # No matching slot found
    
    def _day_matches(self, slot_day, check_day):
        """Check if the slot day matches the check day"""
        if slot_day == "All Days":
            return True
        if slot_day == "All Weekdays" and check_day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            return True
        return slot_day == check_day

