// Copyright (c) 2023, Gursheen Anand and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Entry Item', {
    // cdt is Child DocType name i.e Quotation Item
    // cdn is the row name for e.g bbfcb8da6a
    item(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': 'Item',
                'filters': { 'name': row.item },
                'fieldname': [
                    'default_warehouse',
                ]
            },
            callback: function(r) {
                if (!r.exc) {
                    if (frm.doc.entry_type == 'Receive'){
                        frappe.model.set_value(cdt, cdn, "to_warehouse", (r.message.default_warehouse));
                    }
                    else {
                        frappe.model.set_value(cdt, cdn, "from_warehouse", (r.message.default_warehouse));
                    }
                }
            }
        });        
    }
})