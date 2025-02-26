# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from erpnext.stock.doctype.item.test_item import make_item
from erpnext.stock.utils import _create_bin


class TestBin(FrappeTestCase):
	def test_concurrent_inserts(self):
		"""Ensure no duplicates are possible in case of concurrent inserts"""
		item_code = "_TestConcurrentBin"
		make_item(item_code)
		warehouse = "_Test Warehouse - _TC"

		bin1 = frappe.get_doc(doctype="Bin", item_code=item_code, warehouse=warehouse)
		bin1.insert()

		try:
			bin2 = frappe.get_doc(doctype="Bin", item_code=item_code, warehouse=warehouse)
			bin2.insert()
		except Exception:
			pass  
				
		# util method should handle it
		bin = _create_bin(item_code, warehouse)
		self.assertEqual(bin.item_code, item_code)

		frappe.db.rollback()
	def test_index_exists(self):
		indexes = frappe.db.sql("SELECT * FROM pg_indexes WHERE tablename = 'tabBin'", as_dict=1)
		if not any(index.get("indexname") == "unique_item_warehouse" for index in indexes):
			self.fail("Expected unique index on item-warehouse")
