# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {
            "label": _("Date"),
            "fieldname": "entry_date",
            "fieldtype": "Date",
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
            "label": _("Qty Change"),
            "fieldname": "qty_change",
            "fieldtype": "Int",
            "width": 150,
        },
        {
            "label": _("Cost"),
            "fieldname": "cost",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": _("Value Change"),
            "fieldtype": "Float",
            "fieldname":"value",
            "width": 150,
        },
        {
            "label": _("Available Qty"),
            "fieldtype": "Int",
            "fieldname":"available_qty",
            "width": 150,
        },
        {
            "label": _("From Warehouse"),
            "fieldname": "from_warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        },
        {
            "label": _("To Warehouse"),
            "fieldname": "to_warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        }
    ]
    return columns

def get_data(filters):
    ledger_entries = get_ledger_entries(filters)
    ledger_entries[0]["available_qty"] = ledger_entries[0]["qty_change"]
    for i in range(1, len(ledger_entries)):
        ledger_entries[i]["available_qty"] = ledger_entries[i-1]["available_qty"] + ledger_entries[i]["qty_change"]
    return ledger_entries

def get_ledger_entries(filters):
    sle = frappe.qb.DocType("Stock Ledger Entry")
    
    query = (frappe.qb.from_(sle)
    		.select(
        		sle.entry_date,
                sle.item,
                sle.qty_change,
                sle.cost,
               	(sle.qty_change * sle.cost).as_("value"),
                sle.from_warehouse,
                sle.to_warehouse,
                sle.creation
            )
    		.where(sle.docstatus < 2)
            #.orderby(sle.item)
            .orderby(sle.creation)
            )
    query = apply_filters(filters, sle, query)
    
    results = query.run(as_dict=True, debug=True)
    return results

def apply_filters(filters, sle, query):
    if "item" in filters and filters["item"]:
        query = query.where(sle.item == filters["item"])
    if "entry_date" in filters and filters["entry_date"]:
        query = query.where(sle.entry_date == filters["entry_date"])
    if "from_warehouse" in filters and filters["from_warehouse"]:
        query = query.where(sle.from_warehouse == filters["from_warehouse"])
    if "to_warehouse" in filters and filters["to_warehouse"]:
        query = query.where(sle.to_warehouse == filters["to_warehouse"])
    return query

