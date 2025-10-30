import frappe
from frappe.model.document import Document

risk_matrix = {
    "Rare": 1,
    "Unlikely": 2,
    "Possible": 3,
    "Likely": 4,
    "Almost Certain": 5
}

impact_matrix = {
    "Insignificant": 1,
    "Minor": 2,
    "Moderate": 3,
    "Major": 4,
    "Catastrophic": 5
}

class RiskAssessment(Document):
    def validate(self):
        self.calculate_risk_score()
        if self.assessment_type == 'Location-Based' and not self.linked_location:
            frappe.throw('Linked Location is required for Location-Based assessments')
        if self.assessment_type == 'Corporate' and not self.responsible_department:
            frappe.throw('Responsible Department is required for Corporate assessments')

    def calculate_risk_score(self):
        likelihood_score = risk_matrix.get(self.likelihood, 0)
        impact_score = impact_matrix.get(self.impact, 0)
        self.risk_score = likelihood_score * impact_score

        if self.risk_score <= 5:
            self.risk_level = "Low"
        elif self.risk_score <= 10:
            self.risk_level = "Medium"
        elif self.risk_score <= 15:
            self.risk_level = "High"
        else:
            self.risk_level = "Critical"
