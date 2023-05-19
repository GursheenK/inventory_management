import frappe

def execute():
    stock_entries = frappe.db.get_list('Stock Entry', pluck='name')
    for entry in stock_entries:
        frappe.db.set_value("Stock Entry", entry, "valuation_method", "Moving Average")
        frappe.db.set_value("Stock Entry", entry, "purpose", "Regular")
