// Copyright (c) 2023, Gursheen Anand and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Balance"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		}
	]
};
