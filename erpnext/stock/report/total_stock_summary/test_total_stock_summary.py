import frappe
from frappe.tests.utils import FrappeTestCase

from erpnext.accounts.doctype.account.test_account import create_account
from erpnext.accounts.doctype.payment_entry.test_payment_entry import create_company
from erpnext.stock.doctype.item.test_item import create_item
from erpnext.stock.doctype.stock_entry.test_stock_entry import get_or_create_fiscal_year
from erpnext.stock.doctype.warehouse.test_warehouse import create_warehouse


class TestTotalStockSummary(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.original_get_value = frappe.db.get_value  # Save original method

	@classmethod
	def tearDownClass(cls):
		frappe.db.get_value = cls.original_get_value  # Restore original after tests
		super().tearDownClass()

	def setUp(self):
		# Restore frappe.db.get_value to prevent leaked lambda
		frappe.db.get_value = self.original_get_value

		self.company = create_company("_Test Company")
		self.warehouse = create_warehouse(warehouse_name="_Test Warehouse - _TC", company="_Test Company")
		self.item = create_item(
			item_code="TEST-STOCK-ITEM",
			valuation_rate=100,
			warehouse="_Test Warehouse - _TC",
			company="_Test Company",
		)

		get_or_create_fiscal_year("_Test Company")

		self.stock_entry_name = create_stock_entry(
			item_code=self.item, warehouse="_Test Warehouse - _TC", qty=15, company="_Test Company"
		)

	def test_execute_without_filters_T_TSS_001(self):
		from erpnext.stock.report.total_stock_summary.total_stock_summary import execute

		columns, data = execute()
		assert columns
		assert data
		assert "Company" in columns[0]

	def test_execute_with_group_by_warehouse_T_TSS_002(self):
		from erpnext.stock.report.total_stock_summary.total_stock_summary import execute

		filters = {"group_by": "Warehouse", "company": "_Test Company"}
		columns, data = execute(filters)
		assert columns
		assert data
		assert "Warehouse" in columns[0]

	def test_get_columns_variants_T_TSS_003(self):
		from erpnext.stock.report.total_stock_summary.total_stock_summary import get_columns

		columns_warehouse = get_columns({"group_by": "Warehouse"})
		assert "Warehouse" in columns_warehouse[0]

		columns_company = get_columns({})
		assert "Company" in columns_company[0]

	def test_get_total_stock_variants_T_TSS_004(self):
		from erpnext.stock.report.total_stock_summary.total_stock_summary import get_total_stock

		# Without group_by
		data = get_total_stock({})
		assert data
		assert any(float(d[3]) > 0 for d in data)

		# With group_by Warehouse
		data2 = get_total_stock({"group_by": "Warehouse", "company": "_Test Company"})
		assert data2
		assert any(float(d[3]) > 0 for d in data2)


def create_stock_entry(item_code, warehouse, qty, company):
	se = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"company": company,
			"items": [
				{"item_code": item_code, "qty": qty, "uom": "Nos", "t_warehouse": warehouse, "rate": 100}
			],
		}
	)
	se.insert(ignore_permissions=True)
	se.submit()
	return se.name
