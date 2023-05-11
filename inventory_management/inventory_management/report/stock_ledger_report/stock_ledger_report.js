// Copyright (c) 2023, Gursheen Anand and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Ledger Report"] = {
	"filters": [
		{
			"fieldname":"item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			reqd: 1
		},
		{
			"fieldname":"entry_date",
			"label": __("Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname":"from_warehouse",
			"label": __("From Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"fieldname":"to_warehouse",
			"label": __("To Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
	]
};
