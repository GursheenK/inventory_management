# Copyright (c) 2023, Gursheen Anand and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Item(Document):
	def validate(self):
		if self.opening_stock:
			self.validate_value()
			self.validate_warehouse()
	
	def validate_value(self):
		if not self.opening_valuation_rate:
			frappe.throw(_("Opening Value of Item must be set."))
		
	def validate_warehouse(self):
		if not self.opening_stock_warehouse:
			frappe.throw(_("Target Warehouse for Item must be set."))

	def before_save(self):
		if self.opening_stock:
			self.make_stock_entry()

	def make_stock_entry(self):
		stock_entry = frappe.get_doc({
			"doctype": "Stock Entry",
			"entry_type": "Receive",
			"entry_date": frappe.utils.today(),
			"entry_time": frappe.utils.now(),
			"purpose": "Opening",
			"valuation_method": 'Moving Average',
			"items": [
				frappe._dict(
					item=self,
					quantity=self.opening_stock,
					value=self.opening_valuation_rate,
					to_warehouse=self.opening_stock_warehouse,
				)
			]
		})
		stock_entry.insert()
		stock_entry.submit()
