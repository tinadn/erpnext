# Copyright (c) 2023, 8848 Digital LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder.functions import Coalesce
from erpnext.accounts.report.budget_entry.budget_entry_columns import get_columns


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_conditions(filters):
    wbs = frappe.qb.DocType("Work Breakdown Structure")
    conditions = []

    if filters.get("wbs"):
        if filters.get("show_group_totals"):
            wbs_list = get_all_wbs(filters.get("wbs"))
            if len(wbs_list) > 1:
                conditions.append(wbs.name.isin(wbs_list))
            elif len(wbs_list) == 1:
                wbs_list = wbs_list[0]
                conditions.append(wbs.name == wbs_list)
        else:
            wbs_list = filters.get("wbs")
            if len(wbs_list) > 1:
                conditions.append(wbs.name.isin(wbs_list))
            elif len(wbs_list) == 1:
                wbs_name = wbs_list[0]
                conditions.append(wbs.name == wbs_name)

    if filters.get("project"):
        conditions.append(wbs.project == filters.get("project"))
    return conditions


def get_all_wbs(wbs):
    all_wbs = []
    for w in wbs:
        wbs_parent = frappe.get_doc("Work Breakdown Structure", w)
        if wbs_parent:
            all_wbs.append(w)
            child_list = frappe.db.get_all(
                "Work Breakdown Structure", 
                filters={"lft": [">", wbs_parent.get("lft")], "rgt": ["<", wbs_parent.get("rgt")]},
                pluck="name"
            )
            all_wbs.extend(child_list)
    return all_wbs


def get_group_wbs(filters):
    mapped_wbs = frappe._dict()
    conditions = get_conditions(filters)

    wbs = frappe.qb.DocType("Work Breakdown Structure")
    query = (
        frappe.qb.from_(wbs)
        .select(
            wbs.name,
            wbs.lft,
            wbs.rgt,
            wbs.parent_work_breakdown_structure.as_("parent"),
            wbs.project
        )
        .where(wbs.company == filters.get("company"))
        .orderby(wbs.lft)
    )

    for condition in conditions:
        query = query.where(condition)

    all_wbs = query.run(as_dict=True)
    for d in all_wbs:
        mapped_wbs.setdefault(d.name, 0)

    return all_wbs, mapped_wbs


def get_column_conditions(filters):
    BE = frappe.qb.DocType("Budget Entry")
    condition = []
    vouchers = []

    if filters.get("only_overall_amounts"):
        vouchers.extend(["Zero Budget", "Supplementary Budget", "Budget Decrease", "Budget Transfer","Budget Amendment"])
    if filters.get("only_committed_overall_amounts"):
        vouchers.extend(["Material Request", "Purchase Order"])
    if filters.get("only_actual_overall_amounts"):
        vouchers.extend(["Purchase Receipt", "Purchase Invoice"])

    if vouchers:
        condition.append(BE.voucher_type.isin(vouchers))

    return condition


def get_data(filters):
    voucher_condition = get_column_conditions(filters)
    initial_data = []
    final_data = []

    all_wbs, mapped_wbs = get_group_wbs(filters)
    for d in reversed(all_wbs):
        row = {
            "project": d.project,
            "wbs": d.name,
            "indent": mapped_wbs.get(d.name)
        }
        initial_data = [row] + initial_data

    grand_total_overall_balance = 0.0
    for idata in initial_data:
        BE = frappe.qb.DocType("Budget Entry")
        query = (
            frappe.qb.from_(BE)
            .select(
                BE['wbs'],
				BE['wbs_name'],
				BE['wbs_level'],
				
                BE['project'],
                BE['name'].as_("budget_entry"),
                Coalesce(BE['overall_credit'], 0.0).as_("overall_credit"),
                Coalesce(BE['overall_debit'], 0.0).as_("overall_debit"),
                (Coalesce(BE['overall_credit'], 0.0) - Coalesce(BE['overall_debit'], 0.0)).as_("overall_balance"),
                Coalesce(BE['committed_overall_credit'], 0.0).as_("committed_overall_credit"),
                Coalesce(BE['committed_overall_debit'], 0.0).as_("committed_overall_debit"),
                Coalesce(BE['actual_overall_credit'], 0.0).as_("actual_overall_credit"),
                Coalesce(BE['actual_overall_debit'], 0.0).as_("actual_overall_debit"),
                BE['voucher_type'],
                BE['voucher_no'],
				BE['posting_date'],
                BE.modified_by.as_("created_by"),

            )
            .where(BE['wbs'] == idata.get("wbs"))
        )

        for condition in voucher_condition:
            query = query.where(condition)

        be_query = query.run(as_dict=True)
        if be_query:
            total_overall_balance = sum(be_data["overall_balance"] for be_data in be_query)
            grand_total_overall_balance += total_overall_balance

            final_data.append({
                "project": idata.get("project"),
                "wbs": idata.get("wbs"),
                "indent": idata.get("indent"),
                "overall_balance": total_overall_balance
            })

            final_data.extend(be_query)

    if not any([filters.get("only_overall_amounts"), filters.get("only_committed_overall_amounts"), filters.get("only_actual_overall_amounts")]) or filters.get("show_group_totals"):
        final_data.append({
            "wbs": "Total",
            "overall_balance": grand_total_overall_balance
        })

    return final_data
