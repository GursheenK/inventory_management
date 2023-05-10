# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StockEntry(Document):

	def before_save(self):
		for entry_item in self.items:
			if self.type == 'Receive':
				if entry_item.to_warehouse == None or entry_item.value == None:
					frappe.throw("Destination Warehouse & Value must be set for Receive Entries.")
				self.update_item_value(entry_item)
			if self.type == 'Consume':
				if entry_item.from_warehouse == None:
					frappe.throw("Source Warehouse must be set for Consume Entries.")
				self.validate_available_quantity(entry_item)
			if self.type == 'Transfer':
				if (entry_item.from_warehouse == None or entry_item.to_warehouse == None):
					frappe.throw("Source and Destination Warehouse must be set for Transfer Entries.")
				self.validate_available_quantity(entry_item)

	def validate_available_quantity(self, entry_item):
		item = entry_item.item
		warehouse = entry_item.from_warehouse
		received_units = frappe.db.get_list('Stock Entry', filters={'type': 'Receive', 'item': item, 'to_warehouse': warehouse}, fields=['items.quantity'], pluck='quantity')
		received_units = sum(received_units)
		consumed_units = frappe.db.get_list('Stock Entry', filters={'type': 'Consume' or 'Transfer', 'item': item, 'from_warehouse': warehouse}, fields=['items.quantity'], pluck='quantity')
		consumed_units = sum(consumed_units)
		current_units = received_units - consumed_units
		if current_units < entry_item.quantity:
			frappe.throw(f"Quantity exceeds number of units available for {item} in the inventory.")
		
	def update_item_value(self, entry_item):
		#((old_quantity * old_value) + (added_quantity * new_value)) / total_quantity
		item = entry_item.item
		received_units = frappe.db.get_list('Stock Entry', filters={'type': 'Receive', 'item': item}, fields=['items.quantity'], pluck='quantity')
		received_units = sum(received_units)
		consumed_units = frappe.db.get_list('Stock Entry', filters={'type': 'Consume' or 'Transfer', 'item': item}, fields=['items.quantity'], pluck='quantity')
		consumed_units = sum(consumed_units)
		current_units = received_units - consumed_units
		if current_units == 0:
			return
		old_value = frappe.get_last_doc('Stock Entry', filters={'item': item}, order_by="entry_time desc").items[0].value
		new_value = ((current_units * old_value) + (entry_item.quantity * entry_item.value)) / (current_units + entry_item.quantity)
		new_value = round(new_value, 2)
		entry_item.value = new_value
		frappe.db.sql(f"UPDATE `tabStock Ledger Entry` SET value={new_value} WHERE item='{item}'")
		frappe.db.commit()

