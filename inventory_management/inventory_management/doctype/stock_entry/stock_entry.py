# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from pypika import functions as fn

class StockEntry(Document):
    def validate(self):
        for entry_item in self.items:
            if self.entry_type == "Receive":
                self.validate_dest_warehouse(entry_item)
                self.validate_value(entry_item)
            elif self.entry_type == "Consume":
                self.validate_src_warehouse(entry_item)
                self.validate_available_quantity(entry_item)
            else:
                self.validate_src_warehouse(entry_item)
                self.validate_dest_warehouse(entry_item)
                self.validate_available_quantity(entry_item)

    def validate_src_warehouse(self, entry_item):
        if not entry_item.from_warehouse:
            frappe.throw(_("Source Warehouse must be set."))

    def validate_dest_warehouse(self, entry_item):
        if not entry_item.to_warehouse:
            frappe.throw(_("Destination Warehouse must be set."))

    def validate_value(self, entry_item):
        if not entry_item.value:
            frappe.throw(_("Value of Item must be set."))

    def validate_available_quantity(self, entry_item):
        qty = frappe.db.get_values("Stock Ledger Entry", {
            "item": entry_item.item,
            "warehouse": entry_item.from_warehouse
        }, ["qty_change"])
        available_qty = sum([q[0] for q in qty])
        if available_qty < entry_item.quantity:
            frappe.throw(
                _(f"Quantity exceeds number of units available for {entry_item.item} in the inventory.")
            )

    def on_submit(self):
        if self.entry_type == 'Transfer':
            for entry_item in self.items:
                self.make_transfer_entries(entry_item)
        else:
            for entry_item in self.items:
                warehouse = entry_item.from_warehouse if self.entry_type == 'Consume' else entry_item.to_warehouse
                self.make_sle_entry(entry_item, warehouse, self.entry_type)
            
    def make_transfer_entries(self, entry_item):
        entry_type = 'Consume'
        sle = self.make_sle_entry(entry_item, entry_item.from_warehouse, entry_type)
        entry_item.value = sle.cost
        entry_type = 'Receive'
        self.make_sle_entry(entry_item, entry_item.to_warehouse, entry_type)
       
    def on_cancel(self):
        if self.entry_type == 'Transfer':
            for entry_item in self.items:
                self.make_rev_transfer_entries(entry_item)
        else:
            for entry_item in self.items:
                warehouse, entry_type = (entry_item.from_warehouse, 'Receive') if self.entry_type == 'Consume' else (entry_item.to_warehouse, 'Consume')
                self.make_sle_entry(entry_item, warehouse, entry_type)
                
    def make_rev_transfer_entries(self, entry_item):
        entry_type = 'Consume'
        sle = self.make_sle_entry(entry_item, entry_item.to_warehouse, entry_type)
        entry_item.value = sle.cost
        entry_type = 'Receive'
        self.make_sle_entry(entry_item, entry_item.from_warehouse, entry_type)
        
    def make_sle_entry(self, entry_item, warehouse, entry_type):
        sle = frappe.new_doc("Stock Ledger Entry")
        sle.voucher_name = self.name
        sle.item = entry_item.item
        sle.entry_date = self.entry_date
        sle.entry_time = self.entry_time
        sle.warehouse = warehouse
        if entry_type == 'Receive':
            sle.qty_change, sle.cost = entry_item.quantity, entry_item.value
        else:
            sle.qty_change = -(entry_item.quantity)
            if self.entry_type is 'Receive':
                sle.cost = entry_item.value
            else:
                sle.cost = self.calculate_moving_average(entry_item, sle.warehouse)
        sle.insert()
        return sle 

    def calculate_moving_average(self, entry_item, warehouse):
        sle = frappe.qb.DocType("Stock Ledger Entry")
    
        query = (frappe.qb.from_(sle)
            .select(
                fn.Sum(sle.qty_change * sle.cost).as_("value_change"),
                fn.Sum(sle.qty_change).as_("available_qty")
            )
            .where(sle.item == entry_item.item)
            .where(sle.warehouse == warehouse)
        )
        results = query.run(as_dict=True)
        moving_avg = results[0]["value_change"]/results[0]["available_qty"]
        return moving_avg
