# Copyright (c) 2023, Gursheen Anand and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ...doctype.item.test_item import create_item
from ...doctype.warehouse.test_warehouse import create_warehouse
from ...doctype.stock_entry.test_stock_entry import create_entry
from ...report.stock_balance.stock_balance import execute


class TestStockBalance(FrappeTestCase):
    def setUp(self):
        self.item1 = create_item("Test Item 1")
        self.item2 = create_item("Test Item 2")
        self.warehouse1 = create_warehouse("Test Warehouse 1", is_group=0)
        self.warehouse2 = create_warehouse("Test Warehouse 2", is_group=0)

        create_entry(
            "Receive Entry",
            "Receive",
            [
                (self.item1, self.warehouse1, 10, 5.00),
                (self.item2, self.warehouse1, 20, 10.00),
            ],
        )
        create_entry(
            "Receive Entry 2",
            "Receive",
            [
                (self.item1, self.warehouse1, 10, 15.00),
                (self.item2, self.warehouse1, 10, 20.00),
            ],
        )
        create_entry(
            "Transfer Entry",
            "Transfer",
            [(self.item1, (self.warehouse1, self.warehouse2), 3, 15.00)],
        )

    def test_stock_balance(self):
        filters = {
            "item": self.item1,
            "warehouse": self.warehouse1,
        }
        results = execute(filters)[1]
        self.assertEqual(results[0]["balance_qty"], 17)
        self.assertEqual(results[0]["item_value"], 10)
        self.assertEqual(results[0]["balance_value"], 170)

        filters = {
            "item": self.item2,
            "warehouse": self.warehouse1,
        }
        results = execute(filters)[1]
        self.assertEqual(results[0]["balance_qty"], 30)
        self.assertAlmostEqual(round(results[0]["item_value"], 2), 13.33)
        self.assertEqual(results[0]["balance_value"], 400)

        filters = {
            "item": self.item1,
            "warehouse": self.warehouse2,
        }
        results = execute(filters)[1]
        self.assertEqual(results[0]["balance_qty"], 3)
        self.assertEqual(results[0]["item_value"], 10)
        self.assertEqual(results[0]["balance_value"], 30)