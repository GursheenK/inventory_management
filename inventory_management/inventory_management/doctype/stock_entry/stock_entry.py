# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


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
            frappe.throw("Source Warehouse must be set.")

    def validate_dest_warehouse(self, entry_item):
        if not entry_item.to_warehouse:
            frappe.throw("Destination Warehouse must be set.")

    def validate_value(self, entry_item):
        if not entry_item.value:
            frappe.throw("Value of Item must be set.")

    def validate_available_quantity(self, entry_item):
        available_qty = frappe.db.sql(
            f"SELECT sum(qty_change) FROM `tabStock Ledger Entry` WHERE item='{entry_item.item} and from_warehouse='{entry_item.from_warehouse}''"
        )
        if available_qty[0][0] < entry_item.quantity:
            frappe.throw(
                f"Quantity exceeds number of units available for {entry_item.item} in the inventory."
            )

    def on_submit(self):
        for entry_item in self.items:
            sle = frappe.new_doc("Stock Ledger Entry")
            self.set_sle_params(sle, entry_item)
            sle.insert()

    def on_cancel(self):
        for entry_item in self.items:
            sle = frappe.new_doc("Stock Ledger Entry")
            self.set_sle_params_on_cancel(sle, entry_item)
            sle.insert()

    def set_sle_params(self, sle, entry_item):
        sle.from_warehouse = entry_item.from_warehouse
        sle.to_warehouse = entry_item.to_warehouse
        sle.qty_change = entry_item.quantity
        self.set_item_details(sle, entry_item)

    def set_sle_params_on_cancel(self, sle, entry_item):
        sle.from_warehouse = entry_item.to_warehouse
        sle.to_warehouse = entry_item.from_warehouse
        sle.qty_change = -(entry_item.quantity)
        self.set_item_details(sle, entry_item)

    def set_item_details(self, sle, entry_item):
        sle.item = entry_item.item
        sle.date = self.entry_date
        sle.time = self.entry_time
        if entry_item.entry_type is not 'Receive':
            sle.cost = self.calculate_moving_average(entry_item)
        else:
            sle.cost = entry_item.value

    def calculate_moving_average(self, entry_item):
        moving_avg_rate = frappe.db.sql(
            f"SELECT sum(qty_change*cost)/sum(qty_change) FROM `tabStock Ledger Entry` WHERE item='{entry_item.item}'"
        )
        return moving_avg_rate[0][0]
