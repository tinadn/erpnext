from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe import _

def after_install():
	create_custom_fields(get_custom_fields(), ignore_validate=True)

def get_custom_fields():
	return {
		"Purchase Receipt Item": [
			{
                "default": "0",
                "fieldname": "is_fixed_asset",
                "fieldtype": "Check",
                "hidden": 1,
                "label": "Is Fixed Asset",
                "no_copy": 1,
                "print_hide": 1,
                "read_only": 1,
				"insert_after": "column_break_40",
            },
            {
                "depends_on": "is_fixed_asset",
                "fieldname": "asset_location",
                "fieldtype": "Link",
                "label": "Asset Location",
                "options": "Location",
				"insert_after": "manufacturer_part_no",
            },
			{
                "depends_on": "is_fixed_asset",
                "fetch_from": "item_code.asset_category",
                "fieldname": "asset_category",
                "fieldtype": "Link",
                "label": "Asset Category",
                "options": "Asset Category",
                "read_only": 1,
				"insert_after": "asset_location",
            },
            {
                "fieldname": "wip_composite_asset",
                "fieldtype": "Link",
                "label": "WIP Composite Asset",
                "options": "Asset",
				"insert_after": "add_serial_batch_bundle",
            },
		],
	}
