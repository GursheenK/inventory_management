# Copyright (c) 2023, Gursheen Anand and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ..item.test_item import create_item
from ..warehouse.test_warehouse import create_warehouse


def create_entry(entry_name, entry_type, items):
    entry = frappe.db.get_value("Stock Entry", {"name": entry_name})
    if not entry:
        entry_items = []
        if entry_type is "Receive":
            for item in items:
                entry_items.append(
                    {
                        "item": item[0],
                        "to_warehouse": item[1],
                        "quantity": item[2],
                        "value": item[3],
                    }
                )
        else:
            for item in items:
                entry_items.append(
                    {
                        "item": item[0],
                        "from_warehouse": item[1],
                        "quantity": item[2],
                        "value": item[3],
                    }
                )
        entry = (
            frappe.get_doc(
                {
                    "doctype": "Stock Entry",
                    "docstatus": 1,
                    "entry_type": entry_type,
                    "entry_date": "2023-01-01",
                    "entry_time": "00:00:00",
                    "items": entry_items,
                }
            )
            .insert()
            .name
        )
    return entry


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        self.item1 = create_item("Test Item 1")
        self.item2 = create_item("Test Item 2")
        self.warehouse = create_warehouse("Test Warehouse", is_group=0)


    def test_create_receive_entry(self):
        items = [
            (self.item1, self.warehouse, 10, 5.00),
            (self.item2, self.warehouse, 20, 10.00),
        ]
        self.receive_entry = create_entry("Test Entry", "Receive", items)
        self.assertTrue(frappe.db.exists("Stock Entry", self.receive_entry))
        sle = frappe.get_last_doc(
            "Stock Ledger Entry",
            filters={"item": self.item1, "warehouse": self.warehouse}
        )
        self.assertEqual(sle.qty_change, 10)
        self.assertEqual(sle.cost, 5.00)
        sle = frappe.get_last_doc(
            "Stock Ledger Entry",
            filters={"item": self.item2, "warehouse": self.warehouse}
        )
        self.assertEqual(sle.qty_change, 20)
        self.assertEqual(sle.cost, 10.00)


    def test_cancel_receive_entry(self):
        items = [
            (self.item1, self.warehouse, 10, 5.00),
            (self.item2, self.warehouse, 20, 10.00),
        ]
        self.receive_entry = create_entry("Test Entry", "Receive", items)
        stock_entry = frappe.get_doc("Stock Entry", self.receive_entry)
        stock_entry.cancel()
        sle = frappe.get_last_doc(
            "Stock Ledger Entry",
            filters={"item": self.item1, "warehouse": self.warehouse}
        )
        self.assertEqual(sle.qty_change, -10)
        self.assertEqual(sle.cost, 5.00)
        sle = frappe.get_last_doc(
            "Stock Ledger Entry",
            filters={"item": self.item2, "warehouse": self.warehouse}
        )
        self.assertEqual(sle.qty_change, -20)
        self.assertEqual(sle.cost, 10.00)
    

    def test_create_consume_entry(self):
        items = [
            (self.item1, self.warehouse, 10, 5.00),
            (self.item2, self.warehouse, 20, 10.00),
        ]
        create_entry("Receive Entry", "Receive", items)
        items = [
            (self.item1, self.warehouse, 10, 10.00),
            (self.item2, self.warehouse, 20, 20.00),
        ]
        create_entry("Receive Entry", "Receive", items)
        self.consume_entry = create_entry("Consume Entry", "Consume", items)
        sle = frappe.get_last_doc(
            "Stock Ledger Entry",
            filters={"item": self.item1, "warehouse": self.warehouse}
        )
        self.assertEqual(sle.qty_change, -10)
        self.assertEqual(sle.cost, 7.50)
        sle = frappe.get_last_doc(
            "Stock Ledger Entry",
            filters={"item": self.item2, "warehouse": self.warehouse}
        )
        self.assertEqual(sle.qty_change, -20)
        self.assertEqual(sle.cost, 15.00)

        
