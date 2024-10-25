import frappe
from erpnext.controllers.buying_controller import BuyingController
from erpnext.buying.utils import update_last_purchase_rate
from frappe import _
from frappe.utils import flt, cint


class AssetsBuyingController(BuyingController):
	def validate(self):
		super().validate()
		self.validate_asset_return()

	def validate_stock_or_nonstock_items(self):
		if self.meta.get_field("taxes") and not self.get_stock_items() and not self.get_asset_items():
			msg = _('Tax Category has been changed to "Total" because all the Items are non-stock items')
			self.update_tax_category(msg)

	def validate_asset_return(self):
		if self.doctype not in ["Purchase Receipt", "Purchase Invoice"] or not self.is_return:
			return

		purchase_doc_field = "purchase_receipt" if self.doctype == "Purchase Receipt" else "purchase_invoice"
		not_cancelled_asset = []
		if self.return_against:
			not_cancelled_asset = [
				d.name
				for d in frappe.db.get_all("Asset", {purchase_doc_field: self.return_against, "docstatus": 1})
			]

		if self.is_return and len(not_cancelled_asset):
			frappe.throw(
				_(
					"{} has submitted assets linked to it. You need to cancel the assets to create purchase return."
				).format(self.return_against),
				title=_("Not Allowed"),
			)

	def get_asset_items(self):
		if self.doctype not in ["Purchase Order", "Purchase Invoice", "Purchase Receipt"]:
			return []

		return [d.item_code for d in self.items if d.is_fixed_asset]

	def on_submit(self):
		if self.get("is_return"):
			return

		if self.doctype in ["Purchase Receipt", "Purchase Invoice"]:
			self.process_fixed_asset()

		if self.doctype in [
			"Purchase Order",
			"Purchase Receipt",
			"Purchase Invoice",
		] and not frappe.db.get_single_value("Buying Settings", "disable_last_purchase_rate"):
			update_last_purchase_rate(self, is_submit=1)

	def on_cancel(self):
		super().on_cancel()
		if self.get("is_return"):
			return
		if self.doctype in ["Purchase Receipt", "Purchase Invoice"]:
			field = "purchase_invoice" if self.doctype == "Purchase Invoice" else "purchase_receipt"
			self.delete_linked_asset()
			self.update_fixed_asset(field, delete_asset=True)

	def process_fixed_asset(self):
		if self.doctype == "Purchase Invoice" and not self.update_stock:
			return

		asset_items = self.get_asset_items()
		if asset_items:
			self.auto_make_assets(asset_items)

	def auto_make_assets(self, asset_items):
		items_data = get_asset_item_details(asset_items)
		messages = []

		for d in self.items:
			if d.is_fixed_asset:
				item_data = items_data.get(d.item_code)

				if item_data.get("auto_create_assets"):
					# If asset has to be auto created
					# Check for asset naming series
					if item_data.get("asset_naming_series"):
						created_assets = []
						if item_data.get("is_grouped_asset"):
							asset = self.make_asset(d, is_grouped_asset=True)
							created_assets.append(asset)
						else:
							for _qty in range(cint(d.qty)):
								asset = self.make_asset(d)
								created_assets.append(asset)

						if len(created_assets) > 5:
							# dont show asset form links if more than 5 assets are created
							messages.append(
								_("{} Assets created for {}").format(
									len(created_assets), frappe.bold(d.item_code)
								)
							)
						else:
							assets_link = list(
								map(lambda d: frappe.utils.get_link_to_form("Asset", d), created_assets)
							)
							assets_link = frappe.bold(",".join(assets_link))

							is_plural = "s" if len(created_assets) != 1 else ""
							messages.append(
								_("Asset{} {assets_link} created for {}").format(
									is_plural, frappe.bold(d.item_code), assets_link=assets_link
								)
							)
					else:
						frappe.throw(
							_(
								"Row {}: Asset Naming Series is mandatory for the auto creation for item {}"
							).format(d.idx, frappe.bold(d.item_code))
						)
				else:
					messages.append(
						_("Assets not created for {0}. You will have to create asset manually.").format(
							frappe.bold(d.item_code)
						)
					)

		for message in messages:
			frappe.msgprint(message, title="Success", indicator="green")

	def make_asset(self, row, is_grouped_asset=False):
		if not row.asset_location:
			frappe.throw(_("Row {0}: Enter location for the asset item {1}").format(row.idx, row.item_code))

		item_data = frappe.get_cached_value(
			"Item", row.item_code, ["asset_naming_series", "asset_category"], as_dict=1
		)
		asset_quantity = row.qty if is_grouped_asset else 1
		purchase_amount = flt(row.valuation_rate) * asset_quantity

		asset = frappe.get_doc(
			{
				"doctype": "Asset",
				"item_code": row.item_code,
				"asset_name": row.item_name,
				"naming_series": item_data.get("asset_naming_series") or "AST",
				"asset_category": item_data.get("asset_category"),
				"location": row.asset_location,
				"company": self.company,
				"supplier": self.supplier,
				"purchase_date": self.posting_date,
				"calculate_depreciation": 0,
				"purchase_amount": purchase_amount,
				"gross_purchase_amount": purchase_amount,
				"asset_quantity": asset_quantity,
				"purchase_receipt": self.name if self.doctype == "Purchase Receipt" else None,
				"purchase_invoice": self.name if self.doctype == "Purchase Invoice" else None,
			}
		)

		asset.flags.ignore_validate = True
		asset.flags.ignore_mandatory = True
		asset.set_missing_values()
		asset.db_insert()

		return asset.name

	def update_fixed_asset(self, field, delete_asset=False):
		for d in self.get("items"):
			if d.is_fixed_asset:
				is_auto_create_enabled = frappe.db.get_value("Item", d.item_code, "auto_create_assets")
				assets = frappe.db.get_all("Asset", filters={field: self.name, "item_code": d.item_code})

				for asset in assets:
					asset = frappe.get_doc("Asset", asset.name)
					if delete_asset and is_auto_create_enabled:
						# need to delete movements to delete assets otherwise throws link exists error
						movements = frappe.db.sql(
							"""SELECT asm.name
							FROM `tabAsset Movement` asm, `tabAsset Movement Item` asm_item
							WHERE asm_item.parent=asm.name and asm_item.asset=%s""",
							asset.name,
							as_dict=1,
						)
						for movement in movements:
							frappe.delete_doc("Asset Movement", movement.name, force=1)
						frappe.delete_doc("Asset", asset.name, force=1)
						continue

					if self.docstatus == 2:
						if asset.docstatus == 2:
							continue
						if asset.docstatus == 0:
							asset.set(field, None)
							asset.supplier = None
						if asset.docstatus == 1 and delete_asset:
							frappe.throw(
								_(
									"Cannot cancel this document as it is linked with submitted asset {0}. Please cancel it to continue."
								).format(frappe.utils.get_link_to_form("Asset", asset.name))
							)

					asset.flags.ignore_validate_update_after_submit = True
					asset.flags.ignore_mandatory = True
					if asset.docstatus == 0:
						asset.flags.ignore_validate = True

					asset.save()

	def delete_linked_asset(self):
		if self.doctype == "Purchase Invoice" and not self.get("update_stock"):
			return

		asset_movement = frappe.db.get_value("Asset Movement", {"reference_name": self.name}, "name")
		frappe.delete_doc("Asset Movement", asset_movement, force=1)

def get_asset_item_details(asset_items):
	asset_items_data = {}
	for d in frappe.get_all(
		"Item",
		fields=["name", "auto_create_assets", "asset_naming_series", "is_grouped_asset"],
		filters={"name": ("in", asset_items)},
	):
		asset_items_data.setdefault(d.name, d)

	return asset_items_data
