from erpnext.stock.doctype.material_request.material_request import MaterialRequest
from assets.controllers.overrides.buying_controller import AssetsBuyingController


class AssetsMaterialRequest(MaterialRequest, AssetsBuyingController):
    pass
