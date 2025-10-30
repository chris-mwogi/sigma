frappe.provide("sigma.case_utils");

sigma.case_utils.notify = function(message, indicator="blue") {
    frappe.show_alert({message, indicator});
};
