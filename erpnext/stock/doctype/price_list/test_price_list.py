# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
import unittest
import frappe
from frappe.utils import random_string

# test_ignore = ["Item"]

test_records = frappe.get_test_records("Price List")

class TestPriceList(unittest.TestCase):
    
    def setUp(self):
        # Generate unique names for price lists
        self.buying_price_list_name = f"Buying-{random_string(5)}"
        self.selling_price_list_name = f"Selling-{random_string(5)}"
        
    def test_buying_price_list(self):
        # Create Buying Price List
        buying_price_list = frappe.get_doc({
            "doctype": "Price List",
            "price_list_name": self.buying_price_list_name,
            "buying": 1,
            "selling": 0
        }).insert()
        
        # Verify in Purchase Order
        price_lists = [pl.name for pl in frappe.get_all("Price List", fields=["name"], filters={"buying": 1})]
        self.assertIn(buying_price_list.name, price_lists, "Buying Price List not available in Purchase Order")
        
        # Verify not available in Sales Order
        price_lists = [pl.name for pl in frappe.get_all("Price List", fields=["name"], filters={"selling": 1})]
        self.assertNotIn(buying_price_list.name, price_lists, "Buying Price List should not be available in Sales Order")
    
    def test_selling_price_list(self):
        # Create Selling Price List
        selling_price_list = frappe.get_doc({
            "doctype": "Price List",
            "price_list_name": self.selling_price_list_name,
            "buying": 0,
            "selling": 1
        }).insert()
        
        # Verify in Sales Order
        price_lists = [pl.name for pl in frappe.get_all("Price List", fields=["name"], filters={"selling": 1, "buying": 0})]
        self.assertIn(selling_price_list.name, price_lists, "Selling Price List not available in Sales Order")
        
        # Verify not available in Purchase Order
        price_lists = [pl.name for pl in frappe.get_all("Price List", fields=["name"], filters={"buying": 1, "selling": 0})]
        self.assertNotIn(selling_price_list.name, price_lists, "Selling Price List should not be available in Purchase Order")
    
    def tearDown(self):
        # Cleanup created price lists
        if frappe.db.exists("Price List", self.buying_price_list_name):
            frappe.delete_doc("Price List", self.buying_price_list_name)
        if frappe.db.exists("Price List", self.selling_price_list_name):
            frappe.delete_doc("Price List", self.selling_price_list_name)
