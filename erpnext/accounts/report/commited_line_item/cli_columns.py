import frappe
from frappe import _

def get_columns(filters):
	column = [
		{
			"label":_("WBS"),
			"fieldname":"wbs",
			"fieldtype":"Data",
			"width":150
        },
		{
			"label":_("WBS Name"),
			"fieldname":"wbs_name",
			"fieldtype":"Data",
			"width":150
        },
		{
			"label":_("Voucher Type"),
			"fieldname":"voucher_type",
			"fieldtype":"Data",
			"width":180
        },
		{
			"label":_("Voucher Name"),
			"fieldname":"voucher_name",
			"fieldtype":"Dynamic Link",
			"options":"voucher_type",
			"width":200
        },
		{
			"label":_("Voucher Date"),
			"fieldname":"voucher_date",
			"fieldtype":"Date",
			"width":100
        },
		{
			"label":_("Document Date"),
			"fieldname":"document_date",
			"fieldtype":"Date",
			"width":100
        },
		{
			"label":_("Supplier"),
			"fieldname":"supplier",
			"fieldtype":"Link",
			"options":"Supplier",
			"width":100
        },
		{
			"label":_("Supplier Name"),
			"fieldname":"supplier_name",
			"fieldtype":"Data",
			"width":100
        },
		{
			"label":_("SNo"),
			"fieldname":"idx",
			"fieldtype":"Data",
			"width":50
        },
		{
			"label":_("Item Code"),
			"fieldname":"item_code",
			"fieldtype":"Data",
			"width":100
        },
		{
			"label":_("Item"),
			"fieldname":"item",
			"fieldtype":"Data",
			"width":120
        },
		{
			"label":_("Item Group"),
			"fieldname":"item_group",
			"fieldtype":"Data",
			"width":120
        },
		{
			"label":_("Qty"),
			"fieldname":"qty",
			"fieldtype":"Float",
			"width":120
        },
		{
			"label":_("UOM"),
			"fieldname":"uom",
			"fieldtype":"Data",
			"width":120
        },
		{
			"label":_("Currency"),
			"fieldname":"currency",
			"fieldtype":"Data",
			"width":120
        },
		{
			"label":_("Rate"),
			"fieldname":"rate",
			"fieldtype":"Float",
			"width":120,
			"precision": 2
        },
		{
			"label":_("Amount"),
			"fieldname":"amount",
			"fieldtype":"Float",
			"width":120, 
			"precision": 2
        },
	]
	
	return column