import frappe

def execute(filters=None):
    # Define columns to display in the report
    columns = [
        {"label": "WBS", "fieldname": "wbs", "fieldtype": "Link","options":"Work Breakdown Structure" ,"width": 200},
        {"label": "WBS Name", "fieldname": "wbs_name", "fieldtype": "Data", "width": 150},
        {"label": "WBS Level", "fieldname": "wbs_level", "fieldtype": "Int", "width": 100},
        {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": 100},
        {"label": "Voucher Name", "fieldname": "voucher_no", "fieldtype": "Data", "width": 150},
        {"label": "Voucher Date", "fieldname": "voucher_date", "fieldtype": "Date", "width": 100},
        {"label": "Item", "fieldname": "item", "fieldtype": "Data", "width": 100},
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 150},
        {"label": "Rate", "fieldname": "rate", "fieldtype": "Float", "width": 100},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Float", "width": 100},
    ]

    # Build query conditions based on filters
    conditions = []
    if filters.get("project"):
        conditions.append("be.project IN %(project)s")
    if filters.get("wbs"):
        conditions.append("be.wbs IN %(wbs)s")

    # Add condition to fetch only specified voucher types
    vouchers = ["Purchase Invoice", "Purchase Receipt"]
    conditions.append("be.voucher_type IN %(vouchers)s")

    # Prepare filters dictionary
    filters = filters or {}
    filters["vouchers"] = vouchers

    # Prepare SQL query with CASE statement
    base_query = """
        SELECT 
            be.wbs AS wbs,
            be.wbs_name AS wbs_name,
            be.wbs_level AS wbs_level,
            be.voucher_type AS voucher_type,
            be.voucher_no AS voucher_no,
            be.posting_date AS voucher_date,
            CASE
                WHEN be.voucher_type = 'Purchase Invoice' THEN pii.item_code
                WHEN be.voucher_type = 'Purchase Receipt' THEN mri.item_code
                ELSE NULL
            END AS item,
            CASE
                WHEN be.voucher_type = 'Purchase Invoice' THEN pii.qty
                WHEN be.voucher_type = 'Purchase Receipt' THEN mri.qty
                ELSE NULL
            END AS qty,
            CASE
                WHEN be.voucher_type = 'Purchase Invoice' THEN pii.rate
                WHEN be.voucher_type = 'Purchase Receipt' THEN mri.rate
                ELSE NULL
            END AS rate,
            CASE
                WHEN be.voucher_type = 'Purchase Invoice' THEN pii.qty * pii.rate
                WHEN be.voucher_type = 'Purchase Receipt' THEN mri.qty * mri.rate
                ELSE 0
            END AS amount
        FROM 
            `tabBudget Entry` AS be
        LEFT JOIN 
            `tabPurchase Invoice` AS pi ON pi.name = be.voucher_no
        LEFT JOIN 
            `tabPurchase Invoice Item` AS pii ON pii.parent = pi.name
        LEFT JOIN 
            `tabMaterial Request` AS mr ON mr.name = be.voucher_no
        LEFT JOIN 
            `tabMaterial Request Item` AS mri ON mri.parent = mr.name
    """
    query_conditions = " AND ".join(conditions)
    final_query = f"{base_query} WHERE {query_conditions}" if query_conditions else base_query

    # Execute query
    data = frappe.db.sql(final_query, filters, as_dict=True)

    # Calculate Grand Totals
    total_qty = sum(row.get("qty", 0) for row in data)
    total_rate = sum(row.get("rate", 0) for row in data)
    total_amount = sum(row.get("amount", 0) for row in data)

    # Append Grand Total Row
    grand_total_row = {
        "wbs": "Grand Total",
        "wbs_name": "",
        "wbs_level": None,
        "voucher_type": "",
        "voucher_no": "",
        "voucher_date": None,
        "item": "",
        "qty": total_qty,
        "rate": total_rate,
        "amount": total_amount,
    }

    # Leave one row space before Grand Total
    data.append({})
    data.append(grand_total_row)

    return columns, data
