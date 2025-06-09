import unittest
import frappe

class TestSupplierSalesAnalyticsReport(unittest.TestCase):
    def test_supplier_filter_and_invoice_handling(self):
        from erpnext.buying.doctype.supplier.test_supplier import create_supplier
        from erpnext.stock.doctype.item.test_item import create_item
        from erpnext.accounts.doctype.purchase_invoice.test_purchase_invoice import make_purchase_invoice
        from erpnext.stock.report.supplier_wise_sales_analytics.supplier_wise_sales_analytics import get_suppliers_details

        # Create two suppliers
        supplier_a = create_supplier(supplier_name="Test Supplier A")
        supplier_b = create_supplier(supplier_name="Test Supplier B")

        # Create two items
        item1 = create_item(item_code="TEST-ITEM-001", is_stock_item=1)
        item2 = create_item(item_code="TEST-ITEM-002", is_stock_item=1)

        # Create PI for both with update_stock = 1
        pi1 = make_purchase_invoice(
            supplier=supplier_a.name,
            item_code=item1.name,
            update_stock=True,
            qty=2,
            rate=100
        )
        pi1.submit()

        pi2 = make_purchase_invoice(
            supplier=supplier_b.name,
            item_code=item2.name,
            update_stock=True,
            qty=3,
            rate=150
        )
        pi2.submit()

        # Filters with only supplier A — item2 should be filtered out
        filters = frappe._dict({"supplier": supplier_a.name})

        supplier_map = get_suppliers_details(filters)

        # Only item1 should remain
        self.assertIn(item1.name, supplier_map)
        self.assertNotIn(item2.name, supplier_map)
