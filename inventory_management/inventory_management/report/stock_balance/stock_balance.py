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
    
    results = query.run(as_dict=True, debug=True)
    for entry_item in results:
        sle = frappe.qb.DocType("Stock Ledger Entry")
    
        query = (frappe.qb.from_(sle)
            .select(
                fn.Sum(sle.qty_change).as_("available_qty"),
                fn.Sum(sle.qty_change * sle.cost).as_("curr_value")
            )
            .where(sle.docstatus < 2)
            .where(sle.item == entry_item["item"])
            )
        query = apply_filters(filters, sle, query)
        
        itemResults = query.run(as_dict=True, debug=True)
        curr_value = itemResults[0]["curr_value"]/itemResults[0]["available_qty"]
        entry_item["item_value"] = curr_value
        entry_item["balance_value"] = entry_item["balance_qty"] * curr_value
    return results

def apply_filters(filters, sle, query):
    if "to_date" in filters and filters["to_date"]:
        to_date = filters["to_date"]
    else:
        to_date = frappe.utils.today()
    query = query.where(sle.entry_date <= to_date)
    if "from_date" in filters and filters["from_date"]:
        query = query.where(sle.entry_date >= filters["from_date"])
    return query