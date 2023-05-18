# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt
from frappe import _
import frappe
from pypika import functions as fn


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
            "width": 200
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "width": 200
        },
        {
            "label": _("Balance Qty"),
            "fieldname": "balance_qty",
            "width": 200
        },
        {
            "label": _("Item Value"),
            "fieldname": "item_value",
            "width": 200
        },
        {
            "label": _("Total Balance Value"),
            "fieldname": "balance_value",
            "width": 200
        }
    ]
    return columns


def get_data(filters):
    results = get_ledger_entries(filters)
    for entry_item in results:
        sle = frappe.qb.DocType("Stock Ledger Entry")
    
        query = (frappe.qb.from_(sle)
            .select(
                fn.Sum(sle.qty_change).as_("available_qty"),
                fn.Sum(sle.qty_change * sle.cost).as_("curr_value")
            )
            .where(sle.item == entry_item["item"])
            .where(sle.warehouse == entry_item["warehouse"])
            )
        query = apply_filters(filters, sle, query)
        
        itemResults = query.run(as_dict=True, debug=True)
        curr_value = itemResults[0]["curr_value"]/itemResults[0]["available_qty"]
        entry_item["item_value"] = round(curr_value, 3)
        entry_item["balance_value"] = round(entry_item["balance_qty"] * curr_value, 3)
    return results


def get_ledger_entries(filters):
    sle = frappe.qb.DocType("Stock Ledger Entry")
    
    query = (frappe.qb.from_(sle)
        .select(
            sle.item,
            sle.warehouse,
            fn.Sum(sle.qty_change).as_("balance_qty")
        )
        .where(sle.docstatus < 2)
        .groupby(sle.warehouse, sle.item)
        )
    query = apply_filters(filters, sle, query)
    
    results = query.run(as_dict=True)
    return results

def apply_filters(filters, sle, query):
    if "item" in filters and filters["item"]:
        query = query.where(sle.item == filters["item"])
    if "warehouse" in filters and filters["warehouse"]:
        query = query.where(sle.warehouse == filters["warehouse"])
    if "on_date" in filters and filters["on_date"]:
        query = query.where(sle.entry_date <= filters["on_date"])
    return query