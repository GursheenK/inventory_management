# Copyright (c) 2023, Gursheen Anand and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


def create_warehouse(warehouse_name, is_group):
    warehouse = frappe.db.get_value("Warehouse", {"warehouse_name": warehouse_name})
    if not warehouse:
        warehouse = (
            frappe.get_doc(
                {
                    "doctype": "Warehouse",
                    "warehouse_name": warehouse_name,
                    "warehouse_location": "Test Location",
                    "is_group": is_group,
                }
            )
            .insert()
            .name
        )
    return warehouse


class TestWarehouse(FrappeTestCase):
    def setUp(self):
        self.parent_warehouse = create_warehouse("Parent Warehouse", is_group=1)
        self.child_warehouse = create_warehouse("Child Warehouse", is_group=0)

    def test_create_warehouse(self):
        self.assertTrue(frappe.db.exists("Warehouse", self.parent_warehouse))
        self.assertTrue(frappe.db.exists("Warehouse", self.child_warehouse))
        parent_doc = frappe.get_doc("Warehouse", self.parent_warehouse)
        child_doc = frappe.get_doc("Warehouse", self.child_warehouse)
        child_doc.parent_warehouse = self.parent_warehouse
        self.assertGreater(child_doc.lft, parent_doc.lft)
