from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from assets.controllers.overrides.buying_controller import AssetsBuyingController


class AssetsPurchaseInvoice(PurchaseInvoice, AssetsBuyingController):
    pass
