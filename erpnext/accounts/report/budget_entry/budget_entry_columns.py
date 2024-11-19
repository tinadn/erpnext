from frappe import _

def get_columns(filters):
	if filters.get("show_credit_debit_columns"):
		columns = [
			{
				"label": _("Project"),
				"fieldname":"project",
				"fieldtype": "Link",
				"options":"Project"
			},
			{
				"label": _("WBS Element"),
				"fieldname": "wbs",
				"fieldtype": "Link",
				"options":"Work Breakdown Structure",
				"width": 200
			},
			{
				"label": _("WBS Name"),
				"fieldname": "wbs_name",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _("WBS Level"),
				"fieldname": "wbs_level",
				"fieldtype": "Data",
				"width": 50
			},
			{
				"label": _("Budget Entry"),
				"fieldname":"budget_entry",
				"fieldtype": "Link",
				"options":"Budget Entry"
			},
			{
				"label": _("Overall Credit"),
				"fieldname":"overall_credit",
				"fieldtype": "Float",
				"precision": 2
			},
			{
				"label": _("Overall Debit"),
				"fieldname":"overall_debit",
				"fieldtype": "Float",
				"precision": 2
			},
			{
				"label": _("Value In Trns Crcy"),
				"fieldname":"overall_balance",
				"fieldtype": "Float",
				"precision": 2
			},
			{
				"label": _("Committed Overall Credit"),
				"fieldname":"committed_overall_credit",
				"fieldtype": "Float",
				"precision": 2
			},
			{
				"label": _("Committed Overall Debit"),
				"fieldname":"committed_overall_debit",
				"fieldtype": "Float",
				"precision": 2
			},
			{
				"label": _("Actual Overall Credit"),
				"fieldname":"actual_overall_credit",
				"fieldtype": "Float",
				"precision": 2
			},
			{
				"label": _("Actual Overall Debit"),
				"fieldname":"actual_overall_debit",
				"fieldtype": "Float",
				"precision": 2
			},
			{
				"label": _("Voucher Type"),
				"fieldname":"voucher_type",
				"fieldtype": "Link",
				"options":"DocType"
			},
			{
				"label": _("Voucher No"),
				"fieldname":"voucher_no",
				"fieldtype": "Dynamic Link",
				"options":"voucher_type"
			},
			{
				"label": _("Document Date"),
				"fieldname":"document_date",
				"fieldtype": "Datetime"
			},
			
			{
				"label": _("Voucher Creation Date"),
				"fieldname":"posting_date",
				"fieldtype": "Date"
			},
			{
				"label": _("Created By"),
				"fieldname":"created_by",
				"fieldtype": "Link",
				"options":"User"
			},
			{
				"label": _("Text"),
				"fieldname":"reason",
				"fieldtype": "Data"
			}
		]
	
	else:
		columns = [
			{
				"label": _("Project"),
				"fieldname":"project",
				"fieldtype": "Link",
				"options":"Project"
			},
			{
				"label": _("WBS Element"),
				"fieldname": "wbs",
				"fieldtype": "Link",
				"options":"Work Breakdown Structure",
				"width": 200
			},
			{
				"label": _("WBS Name"),
				"fieldname": "wbs_name",
				"fieldtype": "Data",
				"width": 200
			},
			{
				"label": _("WBS Level"),
				"fieldname": "wbs_level",
				"fieldtype": "Data",
				"width": 200
			},
			{
				"label": _("Budget Entry"),
				"fieldname":"budget_entry",
				"fieldtype": "Link",
				"options":"Budget Entry"
			},
			{
				"label": _("Value In Trns Crcy"),
				"fieldname":"overall_balance",
				"fieldtype": "Float",
				"precision": 2
			},
			{
				"label": _("Voucher Type"),
				"fieldname":"voucher_type",
				"fieldtype": "Link",
				"options":"DocType"
			},
			{
				"label": _("Voucher No"),
				"fieldname":"voucher_no",
				"fieldtype": "Dynamic Link",
				"options":"voucher_type"
			},
			
			
			{
				"label": _("Voucher Creation Date"),
				"fieldname":"voucher_creation_date",
				"fieldtype": "Datetime"
			},
			{
				"label": _("Created By"),
				"fieldname":"created_by",
				"fieldtype": "Link",
				"options":"User"
			},
			{
				"label": _("Text"),
				"fieldname":"reason",
				"fieldtype": "Data"
			}
			]

	return columns