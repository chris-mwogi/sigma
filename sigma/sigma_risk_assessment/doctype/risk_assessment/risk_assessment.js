frappe.ui.form.on('Risk Assessment', {
    refresh: function(frm) {
        if (frm.doc.assessment_type == 'Location-Based') {
            frm.toggle_reqd('linked_location', true);
            frm.toggle_reqd('responsible_department', false);
        } else if (frm.doc.assessment_type == 'Corporate') {
            frm.toggle_reqd('linked_location', false);
            frm.toggle_reqd('responsible_department', true);
        }
    },
    assessment_type: function(frm) {
        frm.refresh_fields();
    },
    likelihood: function(frm) { frm.trigger('recalculate'); },
    impact: function(frm) { frm.trigger('recalculate'); },
    recalculate: function(frm) {
        const score_map = {"Rare":1,"Unlikely":2,"Possible":3,"Likely":4,"Almost Certain":5};
        const impact_map = {"Insignificant":1,"Minor":2,"Moderate":3,"Major":4,"Catastrophic":5};
        let l = score_map[frm.doc.likelihood] || 0;
        let i = impact_map[frm.doc.impact] || 0;
        frm.set_value('risk_score', l * i);
        let s = l * i;
        let level = '';
        if (s <= 5) level = 'Low'; else if (s <= 10) level = 'Medium'; else if (s <= 15) level = 'High'; else level = 'Critical';
        frm.set_value('risk_level', level);
    }
});
