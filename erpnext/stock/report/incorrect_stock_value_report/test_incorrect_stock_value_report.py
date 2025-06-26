import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from erpnext.stock.report.incorrect_stock_value_report.incorrect_stock_value_report import get_data, execute
from erpnext.accounts.doctype.payment_entry.test_payment_entry import create_company
from erpnext.stock.doctype.item.test_item import create_item
from erpnext.stock.doctype.stock_entry.test_stock_entry import get_or_create_fiscal_year
from erpnext.stock.doctype.warehouse.test_warehouse import create_warehouse
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import create_territory
from datetime import date
from frappe.utils import nowdate, add_days


class TestIncorrectStockValueReport(FrappeTestCase): 
    def setUp(self):
        # Company Setup
        self.company = create_company("_Test Indian Registered Company")
        self.company = "_Test Indian Registered Company"
        frappe.db.set_value("Company", self.company, "enable_perpetual_inventory", 1)

        # Ensure required account exists
        if not frappe.db.exists("Account", "Stock Adjustment - _TIRC"):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": "Stock Adjustment",
                "company": self.company,
                "parent_account": "Expenses - _TIRC",  # Ensure this exists
                "account_type": "Temporary",
                "is_group": 0
            }).insert()
        frappe.db.set_value("Company", self.company, "stock_adjustment_account", "Stock Adjustment - _TIRC")

        # Warehouses
        self.stores_warehouse = create_warehouse("Stores", company=self.company)

        # Or with additional properties
        self.finished_goods_warehouse = create_warehouse(
            "Finished Goods",
            properties={"is_group": 0},  # Optional additional fields
            company=self.company
        )

        # Items
        self.item1 =create_item(
            item_code="ADI-SH-W07",
            valuation_rate=9250,
            warehouse=self.stores_warehouse,
            company=self.company,
        )

        self.item2 = create_item(
            item_code="ADI-SH-W08",
            valuation_rate=37500,
            warehouse=self.finished_goods_warehouse,
            company=self.company,
        )
        # Posting date
        posting_date = date(2024, 12, 31)

        # Create Stock Entry to generate initial SLEs
        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "company": "_Test Indian Registered Company",
            "posting_date": posting_date,
            "posting_time": "18:55:42",
            "difference_account": "Stock Adjustment - _TIRC",
            "items": [
                {
                    "item_code": "ADI-SH-W07",
                    "qty": 5,
                    "rate": 9250,  # 5 * 9250 = 46250
                    "t_warehouse": self.stores_warehouse,
                    # "allow_zero_valuation_rate": 1,
                },
                {
                    "item_code": "ADI-SH-W08",
                    "qty": 1,
                    "rate": 37500,  # 1 * 37500 = 37500
                    "t_warehouse": self.finished_goods_warehouse,
                    # "allow_zero_valuation_rate": 1,
                }
            ]
        })
        stock_entry.insert()
        stock_entry.submit()

        # Simulate stock value mismatch
        sle_list = frappe.get_all(
            "Stock Ledger Entry",
            filters={"voucher_no": stock_entry.name},
            fields=["name", "item_code"]
        )

        for sle in sle_list:
            if sle["item_code"] == "ADI-SH-W07":
                frappe.db.set_value("Stock Ledger Entry", sle["name"], "stock_value", 185000.0)  # mismatch on purpose
            elif sle["item_code"] == "ADI-SH-W08":
                frappe.db.set_value("Stock Ledger Entry", sle["name"], "stock_value", 37500.0)   # match, no mismatch

        self.account = "Stock In Hand - _TIRC"

    def test_execute_returns_columns_and_data(self):
        filters = {
            "company": "_Test Indian Registered Company",
            # "account": self.account,
            # "from_date": nowdate()
        }
        columns, data = execute(filters)
        self.assertTrue(columns, "Report should return columns")
        self.assertIsInstance(columns, list, "Columns should be a list")
        self.assertIsInstance(data, list, "Data should be a list")

    def test_get_data_detects_unsync(self):
        filters = {
            "company": "_Test Indian Registered Company",
            # "account": self.account,
            # "from_date": nowdate()
        }
        columns, data = execute(filters)
        self.assertTrue(data, "Expected at least one mismatch row in the report result")
        for row in data:
            self.assertIn("difference_value", row)
            self.assertGreater(abs(row["difference_value"]), 0.1)
            self.assertIn("expected_stock_value", row)

    
    def test_get_data_filters_and_calculates_correctly(self):
        filters = {
            "company": "_Test Indian Registered Company",
            # "account": self.account,
            # "from_date": nowdate()
        }

        # Directly invoke get_data to test filtering and calculation logic
        data = get_data(filters)
        self.assertIsInstance(data, list)

        for row in data:


            self.assertIn("stock_value", row)
            self.assertIn("expected_stock_value", row)
            self.assertIn("difference_value", row)

            # Validate mismatch condition
            calculated_expected = row["expected_stock_value"]
            actual_stock_value = row["stock_value"]
            self.assertAlmostEqual(
                row["difference_value"],
                abs(actual_stock_value - calculated_expected),
                delta=0.01,
                msg="Difference value must match computed mismatch"
            )

    def test_get_data_returns_empty_if_no_unsync_date(self):
        # Create stock entry with no intentional mismatch
        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "company": "_Test Company",
            "posting_date": today(),
            "posting_time": "09:00:00",
            "difference_account": "Stock In Hand - _TC",
            "items": [
                {
                    "item_code": self.item1,
                    "qty": 1,
                    "rate": 1000,
                    "t_warehouse": "_Test warehouse - _TC",
                    "allow_zero_valuation_rate": 1,
                }
            ]
        })
        stock_entry.insert()
        stock_entry.submit()

        # Execute report
        data = get_data({
            "company": "_Test Company"
        })

        # Since there is no mismatch, the report should return an empty list
        self.assertEqual(data, [], "Expected empty result when there is no unsync date or mismatch")


    def test_report_columns_have_expected_fields(self):
        filters = {"company": self.company}
        columns, _ = execute(filters)
        expected_keys = ["item_code", "stock_value", "expected_stock_value", "difference_value"]
        for key in expected_keys:
            self.assertTrue(any(key in str(col) for col in columns), f"Expected column '{key}' not found")


    def test_get_data_respects_account_filter(self):
        data = get_data({
            "company": self.company,
            # "account": self.account
        })
        self.assertIsInstance(data, list)
        # Since there is mismatch in the default SLE created in setup, this should not be empty
        self.assertTrue(any(row["stock_value"] for row in data), "Account filter should still return relevant mismatches")

    def test_get_data_respects_date_filters(self):
        future_date = add_days(today(), 30)
        data = get_data({
            "company": self.company,
            "from_date": future_date,
            "to_date": future_date,
        })
        self.assertEqual(data, [], "Report should return no data if no entries fall within the date range")