# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe
from datetime import timedelta
from frappe.utils import now_datetime
from erpnext.stock.doctype.repost_item_valuation.repost_item_valuation import get_recipients


class TestStockRepostingSettings(unittest.TestCase):
	def tearDown(self):
		frappe.db.rollback()
	
	# codecov
	def test_convert_to_item_wh_reposting_TC_SCK_315(self):
		start_dt = now_datetime()
		end_dt = start_dt + timedelta(hours=1)

		start_time = start_dt.time().strftime("%H:%M:%S")
		end_time = end_dt.time().strftime("%H:%M:%S")

		stock_reposting_setting = frappe.get_doc({
			"doctype": "Stock Reposting Settings",
			"limit_reposting_timeslot": 1,
			"start_time": start_time,  # string like '15:04:52'
			"end_time": end_time,      # string like '16:04:52'
			"limits_dont_apply_on": "Sunday",
			"item_based_reposting": 1,
			"do_reposting_for_each_stock_transaction": 1
		}).insert()

		stock_reposting_setting.convert_to_item_wh_reposting()

	def test_notify_reposting_error_to_role(self):
		role = "Notify Reposting Role"

		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)

		user = "notify_reposting_error@test.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "Test",
					"language": "en",
					"time_zone": "Asia/Kolkata",
					"send_welcome_email": 0,
					"roles": [{"role": role}],
				}
			).insert(ignore_permissions=True)

		frappe.db.set_single_value("Stock Reposting Settings", "notify_reposting_error_to_role", "")

		users = get_recipients()
		self.assertFalse(user in users)

		frappe.db.set_single_value("Stock Reposting Settings", "notify_reposting_error_to_role", role)

		users = get_recipients()
		self.assertTrue(user in users)

	def test_do_reposting_for_each_stock_transaction(self):
		from erpnext.stock.doctype.item.test_item import make_item
		from erpnext.stock.doctype.stock_entry.stock_entry_utils import make_stock_entry

		frappe.db.set_single_value("Stock Reposting Settings", "do_reposting_for_each_stock_transaction", 1)
		if frappe.db.get_single_value("Stock Reposting Settings", "item_based_reposting"):
			frappe.db.set_single_value("Stock Reposting Settings", "item_based_reposting", 0)

		item = make_item(
			"_Test item for reposting check for each transaction", properties={"is_stock_item": 1}
		).name

		stock_entry = make_stock_entry(
			item_code=item,
			qty=1,
			rate=100,
			stock_entry_type="Material Receipt",
			target="_Test Warehouse - _TC",
		)

		riv = frappe.get_all("Repost Item Valuation", filters={"voucher_no": stock_entry.name}, pluck="name")
		self.assertTrue(riv)

		frappe.db.set_single_value("Stock Reposting Settings", "do_reposting_for_each_stock_transaction", 0)

	def test_do_not_reposting_for_each_stock_transaction(self):
		from erpnext.stock.doctype.item.test_item import make_item
		from erpnext.stock.doctype.stock_entry.stock_entry_utils import make_stock_entry

		frappe.db.set_single_value("Stock Reposting Settings", "do_reposting_for_each_stock_transaction", 0)
		if frappe.db.get_single_value("Stock Reposting Settings", "item_based_reposting"):
			frappe.db.set_single_value("Stock Reposting Settings", "item_based_reposting", 0)

		item = make_item(
			"_Test item for do not reposting check for each transaction", properties={"is_stock_item": 1}
		).name

		stock_entry = make_stock_entry(
			item_code=item,
			qty=1,
			rate=100,
			stock_entry_type="Material Receipt",
			target="_Test Warehouse - _TC",
		)

		riv = frappe.get_all("Repost Item Valuation", filters={"voucher_no": stock_entry.name}, pluck="name")
		self.assertFalse(riv)
