# Copyright (c) 2023, Gursheen Anand and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ...doctype.item.test_item import create_item
from ...doctype.warehouse.test_warehouse import create_warehouse
from ...doctype.stock_entry.test_stock_entry import create_entry
from ...report.stock_ledger.stock_ledger import execute


class TestStockLedger(FrappeTestCase):
    def setUp(self):
        self.item1 = create_item("Test Item 1")
        self.item2 = create_item("Test Item 2")
        self.warehouse1 = create_warehouse("Test Warehouse 1", is_group=0)
        self.warehouse2 = create_warehouse("Test Warehouse 2", is_group=0)

        self.receive_entry = create_entry(
            "Receive Entry",
            "Receive",
            [
                (self.item1, self.warehouse1, 10, 5.00),
                (self.item2, self.warehouse1, 20, 10.00),
            ],
        )
        self.consume_entry = create_entry(
            "Consume Entry",
            "Consume",
            [
                (self.item1, self.warehouse1, 5, 5.00),
                (self.item2, self.warehouse1, 5, 10.00),
            ],
        )
        self.transfer_entry = create_entry(
            "Transfer Entry",
            "Transfer",
            [(self.item1, (self.warehouse1, self.warehouse2), 3, 15.00)],
        )


    def test_stock_ledger_receive(self):
        filters = { "voucher_name": self.receive_entry }
        columns, data = execute(filters)
        self.assertEqual(data[0]["value"], 50)
        self.assertEqual(data[0]["valuation_rate"], 5)
        self.assertEqual(data[0]["available_qty"], 10)
       
        self.assertEqual(data[1]["value"], 200)
        self.assertEqual(data[1]["valuation_rate"], 10)
        self.assertEqual(data[1]["available_qty"], 20)
        


    def test_stock_ledger_consume(self):
        filters = { "voucher_name": self.consume_entry }
        columns, data = execute(filters)
        self.assertEqual(data[0]["value"], -25)
        self.assertEqual(data[0]["valuation_rate"], 5)
        self.assertEqual(data[0]["available_qty"], 5)
       
        self.assertEqual(data[1]["value"], -50)
        self.assertEqual(data[1]["valuation_rate"], 10)
        self.assertEqual(data[1]["available_qty"], 15)



    def test_stock_ledger_transfer(self):
        filters = { "voucher_name": self.transfer_entry }
        columns, data = execute(filters)
        self.assertEqual(data[0]["value"], -15)
        self.assertEqual(data[0]["valuation_rate"], 5)
        self.assertEqual(data[0]["available_qty"], 2)
        
        self.assertEqual(data[1]["value"], 15)
        self.assertEqual(data[1]["valuation_rate"], 5)
        self.assertEqual(data[1]["available_qty"], 3)
