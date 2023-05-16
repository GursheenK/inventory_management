# Copyright (c) 2023, Gursheen Anand and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ..item.test_item import create_item
from ..warehouse.test_warehouse import create_warehouse

def create_entry(entry_name, entry_type, items):
    entry = frappe.db.get_value("Stock Entry", {"name": entry_name})
    if not entry:
        entry_items = create_entry_items(entry_type, items)
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


def create_entry_items(entry_type, items):
    entry_items = []
    for entryitem in items:
        i = frappe._dict(
            item=entryitem[0],
            quantity=entryitem[2],
            value=entryitem[3],
        )
        if entry_type is "Receive":
            i["to_warehouse"] = entryitem[1]
        elif entry_type is "Consume":
            i["from_warehouse"] = entryitem[1]
        else:
            i["from_warehouse"] = entryitem[1][0]
            i["to_warehouse"] = entryitem[1][1]
        entry_items.append(i)
    return entry_items


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        self.item1 = create_item("Test Item 1")
        self.item2 = create_item("Test Item 2")
        self.warehouse1 = create_warehouse("Test Warehouse 1", is_group=0)
        self.warehouse2 = create_warehouse("Test Warehouse 2", is_group=0)


    def test_create_receive_entry(self):
        items = [
            (self.item1, self.warehouse1, 10, 5.00),
            (self.item2, self.warehouse1, 20, 10.00),
        ]
        self.receive_entry = create_entry("Test Entry", "Receive", items)
        self.assertTrue(frappe.db.exists("Stock Entry", self.receive_entry))
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.receive_entry,
                "item": self.item1,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, 10)
        self.assertEqual(cost, 5.00)
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.receive_entry,
                "item": self.item2,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, 20)
        self.assertEqual(cost, 10.00)


    def test_cancel_receive_entry(self):
        items = [
            (self.item1, self.warehouse1, 10, 5.00),
            (self.item2, self.warehouse1, 20, 10.00),
        ]
        self.receive_entry = create_entry("Test Entry", "Receive", items)
        stock_entry = frappe.get_doc("Stock Entry", self.receive_entry)
        stock_entry.cancel()
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.receive_entry,
                "item": self.item1,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, -10)
        self.assertEqual(cost, 5.00)
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.receive_entry,
                "item": self.item2,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, -20)
        self.assertEqual(cost, 10.00)


    def test_create_consume_entry(self):
        items = [
            (self.item1, self.warehouse1, 10, 5.00),
            (self.item2, self.warehouse1, 20, 10.00),
        ]
        create_entry("Receive Entry", "Receive", items)
        items = [
            (self.item1, self.warehouse1, 10, 10.00),
            (self.item2, self.warehouse1, 20, 20.00),
        ]
        create_entry("Receive Entry", "Receive", items)
        self.consume_entry = create_entry("Consume Entry", "Consume", items)
        self.assertTrue(frappe.db.exists("Stock Entry", self.consume_entry))
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.consume_entry,
                "item": self.item1,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, -10)
        self.assertEqual(cost, 7.50)
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.consume_entry,
                "item": self.item2,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, -20)
        self.assertEqual(cost, 15.00)


    def test_cancel_consume_entry(self):
        items = [
            (self.item1, self.warehouse1, 10, 5.00),
            (self.item2, self.warehouse1, 20, 10.00),
        ]
        create_entry("Receive Entry", "Receive", items)
        self.consume_entry = create_entry("Consume Entry", "Consume", items)
        stock_entry = frappe.get_doc("Stock Entry", self.consume_entry)
        stock_entry.cancel()
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.consume_entry,
                "item": self.item1,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, 10)
        self.assertEqual(cost, 5.00)


    def test_create_transfer_entry(self):
        create_entry(
            "Receive Entry", "Receive", [(self.item1, self.warehouse1, 10, 5.00)]
        )
        create_entry(
            "Receive Entry 1", "Receive", [(self.item1, self.warehouse1, 10, 15.00)]
        )
        self.transfer_entry = create_entry(
            "Transfer Entry",
            "Transfer",
            (self.item1, (self.warehouse1, self.warehouse2), 3, 5.00),
        )
        self.assertTrue(frappe.db.exists("Stock Entry", self.transfer_entry))
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.transfer_entry,
                "item": self.item1,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, -3)
        self.assertEqual(cost, 10.00)
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.transfer_entry,
                "item": self.item1,
                "warehouse": self.warehouse2,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, 3)
        self.assertEqual(cost, 10.00)

    def test_cancel_transfer_entry(self):
        create_entry(
            "Receive Entry", "Receive", [(self.item1, self.warehouse1, 10, 5.00)]
        )
        self.transfer_entry = create_entry(
            "Transfer Entry",
            "Transfer",
            [(self.item1, (self.warehouse1, self.warehouse2), 3, 5.00)],
        )
        stock_entry = frappe.get_doc("Stock Entry", self.transfer_entry)
        stock_entry.cancel()
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.transfer_entry,
                "item": self.item1,
                "warehouse": self.warehouse1,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, 3)
        self.assertEqual(cost, 5.00)
        qty_change, cost = frappe.db.get_value(
            "Stock Ledger Entry",
            {
                "voucher_name": self.transfer_entry,
                "item": self.item1,
                "warehouse": self.warehouse2,
            },
            ["qty_change", "cost"],
        )
        self.assertEqual(qty_change, -3)
        self.assertEqual(cost, 5.00)
