# Copyright (c) 2023, Gursheen Anand and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ..item.test_item import create_item
from ..warehouse.test_warehouse import create_warehouse


def create_receive_entry(entry_name, items, warehouse):
    entry = frappe.db.get_value("Stock Entry", {"name": entry_name})
    if not entry:
        entry = (
            frappe.get_doc(
                {
                    "doctype": "Stock Entry",
                    "entry_type": "Receive",
                    "entry_date": "2023-01-01",
                    "entry_time": "00:00:00",
                    "items": [
                        {
                            "item": items[0],
                            "to_warehouse": warehouse,
                            "quantity": 10,
                            "value": 5.00,
                        },
                        {
                            "item": items[1],
                            "to_warehouse": warehouse,
                            "quantity": 20,
                            "value": 10.00,
                        },
                    ]
                }
            )
            .insert()
            .name
        )
    return entry


# def create_consume_entry(item, warehouse):
# 	entry = frappe.get_doc({
# 		"doctype": "Stock Entry",
# 		"entry_type": "Consume",
# 		"entry_date": "2023-01-01",
# 		"entry_time": "00:00:00",
# 		"items":[{
# 			"item": item,
# 			"from_warehouse": warehouse,
# 			"quantity": 5
# 		}]
# 	}).insert()
# 	return entry


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        self.item1 = create_item("Test Item 1")
        self.item2 = create_item("Test Item 2")
        self.warehouse = create_warehouse("Test Warehouse", is_group=0)

    def test_create_receive_entry(self):
        items = [self.item1, self.item2]
        self.receive_entry = create_receive_entry("Test Entry", items, self.warehouse)
        self.assertTrue(frappe.db.exists("Stock Entry", self.receive_entry))
        self.assertTrue(
            frappe.db.exists(
                "Stock Ledger Entry",
                {
                    "item": self.item1,
                    "warehouse": self.warehouse,
                    "qty_change": 10,
                    "cost": 5.00,
                }
            )
        )
        self.assertTrue(
            frappe.db.exists(
                "Stock Ledger Entry",
                {
                    "item": self.item2,
                    "warehouse": self.warehouse,
                    "qty_change": 20,
                    "cost": 10.00,
                }
            )
        )
        

    # def test_create_consume_entry(self, item, warehouse):
    # 	crea
    # 	entry = create_consume_entry(item, warehouse)
    # 	self.assertTrue(frappe.db.exists("Stock Entry", entry))
    # 	sle = frappe.get_last_doc("Stock Ledger Entry")
    # 	self.assertEqual(sle.qty_change, -5)
    # 	self.assertEqual(sle.cost, 5.00)
