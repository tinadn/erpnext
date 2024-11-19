from frappe import _

def get_columns(filters):
    column = [
        {
            "label":_("WBS"),
            "fieldname":"wbs",
            "fieldtype":"Data",
            "width":180
        },
        {
            "label":_("WBS Name"),
            "fieldname":"wbs_name",
            "fieldtype":"Data",
            "width":180
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
            "label":_("Reference No"),
            "fieldname":"bill_no",
            "fieldtype":"Data",
            "width":100
        },
        {
            "label":_("Document Date"),
            "fieldname":"document_date",
            "fieldtype":"Datetime",
            "width":100
        },
        {
            "label":_("Supplier"),
            "fieldname":"supplier",
            "fieldtype":"Link",
            "options":"Supplier",
            "width":120
        },
        {
            "label":_("Supplier Name"),
            "fieldname":"supplier_name",
            "fieldtype":"Data",
            "width":120
        },
        {
            "label":_("Employee Name"),
            "fieldname":"employee_name",
            "fieldtype":"Link",
            "options":"Employee",
            "width":100
        },
        {
            "label":_("Expense Claim Type"),
            "fieldname":"expense_claim_type",
            "fieldtype":"Link",
            "options":"Expense Claim Type",
            "width":120
        },
        {
            "label":_("Stock Entry Type"),
            "fieldname":"stock_entry_type",
            "fieldtype":"Link",
            "options":"Stock Entry Type",
            "width":120
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
            "width":120
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
            "label":_("Material Description"),
            "fieldname":"material_description",
            "fieldtype":"Data",
            "width":150
        },
        {
            "label":_("Purchase Order No"),
            "fieldname":"purchase_order_no",
            "fieldtype":"Link",
            "options":"Purchase Order",
            "width":120
        },
        {
            "label":_("Purchase Order Item No"),
            "fieldname":"purchase_order_item_no",
            "fieldtype":"Data",
            "width":120
        },
        {
            "label":_("Qty"),
            "fieldname":"qty",
            "fieldtype":"Float",
            "width":150
        },
        {
            "label":_("UOM"),
            "fieldname":"uom",
            "fieldtype":"Data",
            "width":100
        },
        {
            "label":_("Currency"),
            "fieldname":"currency",
            "fieldtype":"Data",
            "width":100
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
        {
            "label":_("Dr/Cr"),
            "fieldname":"dr_cr_status",
            "fieldtype":"Data",
            "width":120
        },
        {
            "label":_("GL Account"),
            "fieldname":"gl_acc",
            "fieldtype":"Dynamic Link",
            "options":"Account",
            "width":120
        },
        {
            "label":_("Cost Center"),
            "fieldname":"cost_center",
            "fieldtype":"Dynamic Link",
            "options":"Cost Center",
            "width":120
        },
        {
            "label":_("Cost Center Name"),
            "fieldname":"cost_center_name",
            "fieldtype":"Data",
            "width":150
        },
        {
            "label":_("Plant"),
            "fieldname":"plant",
            "fieldtype":"Dynamic Link",
            "options":"Plant",
            "width":120
        },
        {
            "label":_("Plant Name"),
            "fieldname":"plant_name",
            "fieldtype":"Data",
            "width":120
        },
        {
            "label":_("Business Place"),
            "fieldname":"business_place",
            "fieldtype":"Data",
            "width":120
        },
        {
            "label":_("Posting Date"),
            "fieldname":"posting_date",
            "fieldtype":"Date",
            "width":120
        },
        {
            "label":_("Posting Time"),
            "fieldname":"posting_time",
            "fieldtype":"Time",
            "width":120
        },
        {
            "label":_("Submit Date"),
            "fieldname":"submit_date",
            "fieldtype":"Date",
            "width":120
        },
        {
            "label":_("Submit Time"),
            "fieldname":"submit_time",
            "fieldtype":"Time",
            "width":120
        },
        {
            "label":_("User Name"),
            "fieldname":"user_name",
            "fieldtype":"Data",
            "width":120
        }
    ]
    
    return column