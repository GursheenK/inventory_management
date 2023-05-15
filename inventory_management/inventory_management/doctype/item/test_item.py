# Copyright (c) 2023, Gursheen Anand and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


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


class TestItem(FrappeTestCase):
    def setUp(self):
        self.item = create_item("Test Item")

    def test_create_item(self):
        self.assertTrue(frappe.db.exists("Item", self.item))
