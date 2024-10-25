from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
from assets.controllers.overrides.buying_controller import AssetsBuyingController


class AssetsPurchaseOrder(PurchaseOrder, AssetsBuyingController):
    pass
