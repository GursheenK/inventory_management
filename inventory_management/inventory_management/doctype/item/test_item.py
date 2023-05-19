# Copyright (c) 2023, Gursheen Anand and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ..warehouse.test_warehouse import create_warehouse


def create_item(item_name):
    item = frappe.db.get_value("Item", {"item_name": item_name})
    if not item:
        item = (
            frappe.get_doc(
                {
                    "doctype": "Item",
                    "item_name": item_name,
                    "brand": "Test Brand",
                    "item_code": item_name,
                    "description": "Test Description",
                }
            )
            .insert()
            .name
        )
    return item


def create_opening_stock_item(item_name, warehouse):
    item = frappe.db.get_value("Item", {"item_name": item_name})
    if not item:
        item = (
            frappe.get_doc(
                {
                    "doctype": "Item",
                    "item_name": item_name,
                    "brand": "Test Brand",
                    "item_code": item_name,
                    "description": "Test Description",
                    "opening_stock": 10,
                    "opening_stock_warehouse": warehouse,
                    "opening_valuation_rate": 2,
                }
            )
            .insert()
            .save()
            .name
        )
    return item


class TestItem(FrappeTestCase):
    def setUp(self):
        self.warehouse = create_warehouse("Test Warehouse", is_group=0)
        self.item = create_opening_stock_item("Item with Opening Stock", self.warehouse)

    def test_create_item(self):
        self.assertTrue(frappe.db.exists("Item", self.item))
        self.assertTrue(frappe.db.exists("Stock Entry", {"purpose": "Opening"}))
        doc = frappe.get_last_doc(
            "Stock Entry",
            {
                "purpose": "Opening",
            },
        )
        self.assertEqual(doc.items[0].item, self.item)
        self.assertEqual(doc.items[0].quantity, 10)
        self.assertEqual(doc.items[0].value, 2)
        self.assertEqual(doc.items[0].to_warehouse, self.warehouse)
