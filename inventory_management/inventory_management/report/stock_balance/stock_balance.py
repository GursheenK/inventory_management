# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt
from frappe import _
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{
            "label": _("Item"),
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
		{
            "label": _("Balance Qty"),
            "fieldname": "balance_qty",
            "width": 200,
        },
		{
            "label": _("Balance Value"),
            "fieldname": "balance_value",
            "width": 200,
        }
	]
	return columns

def get_data(filters):
	results = frappe.db.sql(f"select distinct(item) as item, sum(qty_change) over(partition by item) as balance_qty FROM `tabStock Ledger Entry`", as_dict=True, debug=True)
	for entry_item in results:
		doc = frappe.get_last_doc('Stock Ledger Entry', filters={"item": entry_item.item})
		entry_item["balance_value"] = entry_item["balance_qty"]*doc.cost
	return results