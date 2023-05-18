# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from pypika import functions as fn

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {
            "label": _("Voucher"),
            "fieldname": "voucher_name",
            "fieldtype": "Link",
            "options": "Stock Entry",
            "width": 100,
        },
        {
            "label": _("Date"),
            "fieldname": "entry_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
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
            "width": 100,
        },
        {
            "label": _("Cost"),
            "fieldname": "cost",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("Valuation Rate"),
            "fieldname": "valuation_rate",
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
        }
    ]
    return columns

def get_data(filters):
    ledger_entries = get_ledger_entries(filters)
    for ledger_entry in ledger_entries:
        sle = frappe.qb.DocType("Stock Ledger Entry")
    
        query = (
            frappe.qb.from_(sle)
            .select(
                fn.Sum(sle.qty_change).as_("available_qty"),
                fn.Sum(sle.qty_change * sle.cost).as_("total_value")
            )
            .where(sle.item == ledger_entry["item"])
            .where(sle.warehouse == ledger_entry["warehouse"])
            .where(sle.creation <= ledger_entry["creation"])
        )
        
        results = query.run(as_dict=True)
        ledger_entry["available_qty"] = results[0]["available_qty"]
        ledger_entry["valuation_rate"] = results[0]["total_value"]/results[0]["available_qty"]
    return ledger_entries

def get_ledger_entries(filters):
    sle = frappe.qb.DocType("Stock Ledger Entry")
    
    query = (frappe.qb.from_(sle)
    		.select(
                sle.voucher_name,
        		sle.entry_date,
                sle.item,
                sle.qty_change,
                sle.cost,
               	(sle.qty_change * sle.cost).as_("value"),
                sle.warehouse,
                sle.creation
            )
    		.where(sle.docstatus < 2)
            .orderby(sle.creation)
            )
    query = apply_filters(filters, sle, query)
    
    results = query.run(as_dict=True)
    return results

def apply_filters(filters, sle, query):
    if "voucher_name" in filters and filters["voucher_name"]:
        query = query.where(sle.voucher_name == filters["voucher_name"])
    if "item" in filters and filters["item"]:
        query = query.where(sle.item == filters["item"])
    if "entry_date" in filters and filters["entry_date"]:
        query = query.where(sle.entry_date == filters["entry_date"])
    if "warehouse" in filters and filters["warehouse"]:
        query = query.where(sle.warehouse == filters["warehouse"])
    return query

