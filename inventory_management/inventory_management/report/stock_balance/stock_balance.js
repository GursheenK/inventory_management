// Copyright (c) 2023, Gursheen Anand and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Balance"] = {
	"filters": [
		{
			"fieldname":"reqd_warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		}	
	]
};
