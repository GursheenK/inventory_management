import frappe

def execute():

    # your patch code here
    stock_entries = frappe.db.get_list('Stock Entry', pluck='name')
    for entry in stock_entries:
        frappe.db.set_value("Stock Entry", entry, "valuation_method", "Moving Average")
