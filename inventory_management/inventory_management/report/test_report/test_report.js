// Copyright (c) 2023, Gursheen Anand and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Test Report"] = {
	"filters": [
		{
			"fieldname":"type",
			"label": __("Entry Type"),
			"fieldtype": "Select",
			"options": ["Receive", "Consume", "Transfer"]
		}
	]
};
