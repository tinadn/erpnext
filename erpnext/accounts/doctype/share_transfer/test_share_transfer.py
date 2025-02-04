# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe

from erpnext.accounts.doctype.share_transfer.share_transfer import ShareDontExists

test_dependencies = ["Share Type", "Shareholder"]


class TestShareTransfer(unittest.TestCase):
	def setUp(self):
		frappe.db.sql("delete from `tabShare Transfer`")
		frappe.db.sql("delete from `tabShare Balance`")
		share_transfers = [
			{
				"doctype": "Share Transfer",
				"transfer_type": "Issue",
				"date": "2018-01-01",
				"to_shareholder": "SH-00001",
				"share_type": "Equity",
				"from_no": 1,
				"to_no": 500,
				"no_of_shares": 500,
				"rate": 10,
				"company": "_Test Company",
				"asset_account": "Cash - _TC",
				"equity_or_liability_account": "Creditors - _TC",
			},
			{
				"doctype": "Share Transfer",
				"transfer_type": "Transfer",
				"date": "2018-01-02",
				"from_shareholder": "SH-00001",
				"to_shareholder": "SH-00002",
				"share_type": "Equity",
				"from_no": 101,
				"to_no": 200,
				"no_of_shares": 100,
				"rate": 15,
				"company": "_Test Company",
				"equity_or_liability_account": "Creditors - _TC",
			},
			{
				"doctype": "Share Transfer",
				"transfer_type": "Transfer",
				"date": "2018-01-03",
				"from_shareholder": "SH-00001",
				"to_shareholder": "SH-00003",
				"share_type": "Equity",
				"from_no": 201,
				"to_no": 500,
				"no_of_shares": 300,
				"rate": 20,
				"company": "_Test Company",
				"equity_or_liability_account": "Creditors - _TC",
			},
			{
				"doctype": "Share Transfer",
				"transfer_type": "Transfer",
				"date": "2018-01-04",
				"from_shareholder": "SH-00003",
				"to_shareholder": "SH-00002",
				"share_type": "Equity",
				"from_no": 201,
				"to_no": 400,
				"no_of_shares": 200,
				"rate": 15,
				"company": "_Test Company",
				"equity_or_liability_account": "Creditors - _TC",
			},
			{
				"doctype": "Share Transfer",
				"transfer_type": "Purchase",
				"date": "2018-01-05",
				"from_shareholder": "SH-00003",
				"share_type": "Equity",
				"from_no": 401,
				"to_no": 500,
				"no_of_shares": 100,
				"rate": 25,
				"company": "_Test Company",
				"asset_account": "Cash - _TC",
				"equity_or_liability_account": "Creditors - _TC",
			},
		]
		for d in share_transfers:
			st = frappe.get_doc(d)
			st.submit()

	def test_invalid_share_transfer(self):
		doc = frappe.get_doc(
			{
				"doctype": "Share Transfer",
				"transfer_type": "Transfer",
				"date": "2018-01-05",
				"from_shareholder": "SH-00003",
				"to_shareholder": "SH-00002",
				"share_type": "Equity",
				"from_no": 1,
				"to_no": 100,
				"no_of_shares": 100,
				"rate": 15,
				"company": "_Test Company",
				"equity_or_liability_account": "Creditors - _TC",
			}
		)
		self.assertRaises(ShareDontExists, doc.insert)

		doc = frappe.get_doc(
			{
				"doctype": "Share Transfer",
				"transfer_type": "Purchase",
				"date": "2018-01-02",
				"from_shareholder": "SH-00001",
				"share_type": "Equity",
				"from_no": 1,
				"to_no": 200,
				"no_of_shares": 200,
				"rate": 15,
				"company": "_Test Company",
				"asset_account": "Cash - _TC",
				"equity_or_liability_account": "Creditors - _TC",
			}
		)
		self.assertRaises(ShareDontExists, doc.insert)


	def test_create_share_transfer_and_then_jv_TC_ACC_106(self):
		from erpnext.accounts.doctype.share_transfer.share_transfer import make_jv_entry
		
		# Create a valid share transfer document (Transfer from SH-00001 to SH-00002)
		doc = frappe.get_doc(
			{
				"doctype": "Share Transfer",
				"transfer_type": "Issue",
				"date": "2025-01-03",
				"to_shareholder": "SH-00003",
				"share_type": "Equity",
				"from_no": 801,
				"to_no": 900,
				"no_of_shares": 100,
				"rate": 15,
				"company": "_Test Company",
				"asset_account": "Cash - _TC",
				"equity_or_liability_account": "Creditors - _TC",
			}
		)
		doc.submit()
		# Assert that the Share Transfer document is successfully submitted
		self.assertEqual(doc.docstatus, 1, "The Share Transfer document was not submitted correctly.")

		amount = doc.no_of_shares * doc.rate
		journal_entry = make_jv_entry(
				company=doc.company,
				account=doc.asset_account,
				amount=amount,
				payment_account=doc.equity_or_liability_account,
				credit_applicant_type="Shareholder",
				credit_applicant=doc.to_shareholder,
				debit_applicant_type="",
				debit_applicant=""
			)
		self.assertEqual(
			journal_entry['accounts'][0]['debit_in_account_currency'], amount,
			f"Debit amount in Journal Entry is incorrect. Expected: {amount}, Found: {journal_entry['accounts'][0]['debit_in_account_currency']}"
		)
		self.assertEqual(
			journal_entry['accounts'][1]['credit_in_account_currency'], amount,
			f"Credit amount in Journal Entry is incorrect. Expected: {amount}, Found: {journal_entry['accounts'][1]['credit_in_account_currency']}"
		)