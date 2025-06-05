import unittest
import frappe
from frappe.utils import today, add_days
from erpnext.stock.report.delivery_note_trends.delivery_note_trends import execute, get_chart_data


class TestDeliveryNoteTrendsReport(unittest.TestCase):
    def test_execute_with_fiscal_year_filter(self):
        filters = frappe._dict({
            "company": "_Test Company",
            "fiscal_year": "2024-2025",
            "based_on": "Customer",         # Dimension to analyze
            "group_by": "Item",             # Must not match 'based_on'
            "period": "Monthly",
            "period_based_on": "posting_date"
        })

        cols, data, none_val, chart = execute(filters)

        self.assertIsInstance(cols, list)
        self.assertIsInstance(data, list)
        self.assertIsNone(none_val)
        self.assertIsInstance(chart, dict)
        self.assertIn("data", chart)


    def test_get_chart_data_empty(self):
        result = get_chart_data([], {})
        self.assertEqual(result, [])

    def test_execute_with_empty_filters(self):
        filters = frappe._dict({
            "company": "_Test Company",
            "fiscal_year": "2024-2025",
            "based_on": "Customer",
            "group_by": "Item",
            "period": "Monthly",
            "period_based_on": "posting_date"
        })

        cols, data, none_val, chart = execute(filters)

        self.assertIsInstance(cols, list)
        self.assertIsInstance(data, list)
        self.assertIsNone(none_val)
        self.assertIsInstance(chart, dict)
        self.assertIn("data", chart)

    def test_get_chart_data_empty(self):
        # Covers the early return on empty data
        result = get_chart_data([], {})
        self.assertEqual(result, [])

    def test_get_chart_data_group_by_true(self):
        # Prepare dummy data with some rows having falsy first element
        data = [
            ["Group 1", 100],
            [None, 200],   # should be filtered out if group_by True
            ["Group 2", 300]
        ]
        filters = {"group_by": True}
        result = get_chart_data(data, filters)
        # Only rows with truthy first element included
        self.assertTrue(all(row in ["Group 1", "Group 2"] for row in result["data"]["labels"]))
        self.assertEqual(result["type"], "bar")
        self.assertEqual(result["fieldtype"], "Currency")

    def test_get_chart_data_top_10(self):
        # More than 10 rows to trigger slicing
        data = [[f"Label{i}", i * 10] for i in range(15)]
        filters = {}
        result = get_chart_data(data, filters)
        # Should only have 10 entries
        self.assertEqual(len(result["data"]["labels"]), 10)
        self.assertEqual(result["type"], "bar")

    def test_get_chart_data_less_than_10_no_group_by(self):
        data = [
            ["Label A", 150],
            ["Label B", 250],
            ["Label C", 50]
        ]
        filters = {}
        result = get_chart_data(data, filters)
        self.assertEqual(set(result["data"]["labels"]), {"Label A", "Label B", "Label C"})
        self.assertEqual(result["type"], "bar")
