/**
 * Patch for Frappe LinksWidget to handle null link_type in Card Breaks
 * 
 * Issue: When workspace links include Card Break items with null link_type,
 * the LinksWidget tries to call .toLowerCase() on null, causing:
 * "TypeError: can't access property "toLowerCase", name2 is null"
 * 
 * Solution: Filter out Card Break items before processing links
 */

(function() {
  // Wait for frappe to be loaded
  if (typeof frappe === 'undefined') {
    setTimeout(arguments.callee, 100);
    return;
  }

  // Patch the LinksWidget to skip Card Break items
  if (frappe.ui && frappe.ui.form && frappe.ui.form.ControlLink) {
    // This is a workaround - we'll patch at the widget level
  }

  // More direct approach: patch the widget rendering
  const originalSetBody = frappe.widget?.LinksWidget?.prototype?.set_body;
  
  if (originalSetBody) {
    frappe.widget.LinksWidget.prototype.set_body = function() {
      // Filter out Card Break items before processing
      if (this.links && Array.isArray(this.links)) {
        this.links = this.links.filter(item => item.type !== 'Card Break');
      }
      
      // Call original set_body
      return originalSetBody.call(this);
    };
  }

  // Alternative: Patch at the map level
  frappe.provide('frappe.widget');
  
  // Override the LinksWidget if it exists
  if (frappe.widget && frappe.widget.LinksWidget) {
    const OriginalLinksWidget = frappe.widget.LinksWidget;
    
    frappe.widget.LinksWidget = class PatchedLinksWidget extends OriginalLinksWidget {
      set_body() {
        // Filter out Card Break items
        if (this.links && Array.isArray(this.links)) {
          this.links = this.links.filter(item => item.type !== 'Card Break');
        }
        
        // Call parent set_body
        super.set_body();
      }
    };
  }

  console.log('[Sigma Patch] LinksWidget fix applied - Card Break items will be filtered');
})();

