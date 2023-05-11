# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt
from frappe import _
import frappe


def execute(filters=None):
	columns = [
		{
			"label": _("Type"), 
			"fieldname": "Entry Type", 
			"fieldtype": "Select",
			"options": "Receive Consume Transfer", 
			"width": 200
		},
		{
			"label": _("Date"),
			"fieldname": "entry_date",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"label": _("Time"),
			"fieldname": "entry_time",
			"fieldtype": "Time",
			"width": 150,
		},
		{
			"label": _("Item"),
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{
			"label": _("Source Warehouse"),
			"fieldname": "from_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 200,
		},
		{
			"label": _("Destination Warehouse"),
			"fieldname": "to_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 200,
		},
		{
			"label": _("Quantity"),
			"fieldname": "quantity",
			"fieldtype": "Int",
			"width": 150,
		}
	]

	stock_entry = frappe.qb.DocType('Stock Entry')
	stock_ledger_entry = frappe.qb.DocType('Stock Ledger Entry')
	q = frappe.qb.from_(stock_entry).inner_join(stock_ledger_entry).on(stock_entry.name==stock_ledger_entry.parent).select(stock_entry.type, stock_entry.entry_date, stock_entry.entry_time, stock_ledger_entry.item, stock_ledger_entry.from_warehouse, stock_ledger_entry.to_warehouse, stock_ledger_entry.quantity)
	data = q.run()
	return columns, data

