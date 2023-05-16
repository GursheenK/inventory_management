// Copyright (c) 2023, Gursheen Anand and contributors
// For license information, please see license.txt

frappe.ui.form.on("Warehouse", "onload", function(frm) {
    frm.set_query("parent_warehouse", function() {
        return {
            "filters": {
                "is_group": 1
            }
        };
    });
});
